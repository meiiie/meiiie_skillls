import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time

MAX_LOG_CHARS = 65536


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(label + " must be a finite positive number")
    return float(value)


def within(workspace, value):
    target = (workspace / value).resolve()
    if not target.is_relative_to(workspace):
        raise ValueError("path leaves declared workspace: " + str(value))
    return target


def hashes(workspace, names):
    result = {}
    for name in names:
        path = within(workspace, name)
        result[name] = sha(path) if path.is_file() else None
    return result


def log(value):
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    value = value or ""
    return {"text": value[:MAX_LOG_CHARS], "truncated": len(value) > MAX_LOG_CHARS,
            "original_characters": len(value)}


def protocol_status(stdout, exit_code):
    try:
        lines = [line for line in stdout.splitlines() if line.strip()]
        payload = json.loads(lines[-1])["quality_result"]
        status, checks, failures = payload["status"], payload["checks"], payload["failures"]
        if isinstance(checks, bool) or isinstance(failures, bool):
            raise ValueError("boolean count")
        if not isinstance(checks, int) or not isinstance(failures, int) or checks < 1 or not 0 <= failures <= checks:
            raise ValueError("invalid counts")
        if status == "pass" and failures == 0 and exit_code == 0:
            return "pass"
        if status == "assertion_failure" and failures > 0 and exit_code != 0:
            return "assertion_failure"
        if status == "runtime_failure" and failures > 0 and exit_code != 0:
            return "runtime_failure"
    except (IndexError, KeyError, TypeError, ValueError):
        pass
    return "protocol_error"


def load_manifest(path):
    manifest_bytes = path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    if manifest.get("version") != 1:
        raise ValueError("manifest version must be 1")
    workspace = (path.parent / manifest.get("workspace", ".")).resolve()
    if not workspace.is_dir():
        raise ValueError("workspace is unavailable")
    budget = number(manifest.get("budget_seconds", 30), "budget_seconds")
    if budget > 300:
        raise ValueError("budget_seconds may not exceed 300")
    checks = manifest.get("checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 32:
        raise ValueError("checks must contain 1 to 32 entries")
    seen = set()
    baseline_finished = False
    for check in checks:
        identifier = check.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("check IDs must be unique non-empty strings")
        seen.add(identifier)
        phase = check.get("phase", "check")
        if phase not in ("baseline", "check", "mutant"):
            raise ValueError("unknown phase")
        if phase == "baseline" and baseline_finished:
            raise ValueError("baseline checks must precede other phases")
        baseline_finished |= phase != "baseline"
        argv = check.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
            raise ValueError("argv must be a non-empty string array")
        mode = check.get("result_mode", "exit")
        if mode not in ("exit", "quality-json"):
            raise ValueError("unknown result_mode")
        if phase == "mutant" and mode != "quality-json":
            raise ValueError("mutants require explicit quality-json assertion evidence")
        check["phase"] = phase
        check["result_mode"] = mode
        check["timeout_seconds"] = number(check.get("timeout_seconds", 5), "timeout_seconds")
        if check["timeout_seconds"] > 60:
            raise ValueError("per-command timeout may not exceed 60")
        check["cwd"] = str(within(workspace, check.get("cwd", ".")))
        if not Path(check["cwd"]).is_dir():
            raise ValueError("check cwd is unavailable")
        names = check.get("hash_inputs", [])
        if not isinstance(names, list) or not all(isinstance(name, str) and name for name in names):
            raise ValueError("hash_inputs must be a string array")
        if any(value is None for value in hashes(workspace, names).values()):
            raise ValueError("declared hash input is missing")
        check["hash_inputs"] = names
    if any(check["phase"] == "mutant" for check in checks) and not any(check["phase"] == "baseline" for check in checks):
        raise ValueError("mutation manifest needs a clean baseline")
    return workspace, budget, checks, hashlib.sha256(manifest_bytes).hexdigest()


def execute(check, workspace, remaining):
    argv = list(check["argv"])
    if argv[0] == "{python}":
        argv[0] = sys.executable
    elif argv[0] == "{node}":
        argv[0] = shutil.which("node") or "node-runtime-unavailable"
    record = {"id": check["id"], "phase": check["phase"], "argv": argv, "cwd": check["cwd"],
              "result_mode": check["result_mode"],
              "timeout_seconds": min(check["timeout_seconds"], remaining)}
    started = time.perf_counter()
    try:
        before = hashes(workspace, check["hash_inputs"])
        record["hashes_before"] = before
    except (OSError, ValueError) as error:
        record.update({"status": "input_hash_error", "hash_error_stage": "before",
                       "hash_error": type(error).__name__ + ": " + str(error),
                       "seconds": time.perf_counter() - started})
        return record
    try:
        child = subprocess.run(argv, cwd=check["cwd"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", shell=False,
                               timeout=record["timeout_seconds"], check=False)
        record.update({"exit_code": child.returncode, "stdout": log(child.stdout), "stderr": log(child.stderr)})
        status = protocol_status(child.stdout, child.returncode) if check["result_mode"] == "quality-json" else (
            "pass" if child.returncode == 0 else "command_failure")
    except subprocess.TimeoutExpired as error:
        status = "timeout"
        record.update({"exit_code": None, "stdout": log(error.stdout), "stderr": log(error.stderr)})
    except OSError as error:
        status = "infrastructure_error"
        record.update({"exit_code": None, "error": type(error).__name__ + ": " + str(error)})
    record["command_status"] = status
    try:
        after = hashes(workspace, check["hash_inputs"])
        record.update({"hashes_after": after, "status": "inputs_changed" if before != after else status})
    except (OSError, ValueError) as error:
        record.update({"status": "input_hash_error", "hash_error_stage": "after",
                       "hash_error": type(error).__name__ + ": " + str(error)})
    record["seconds"] = time.perf_counter() - started
    return record


def main():
    parser = argparse.ArgumentParser(description="Run reviewed command arrays and preserve classified local evidence.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    try:
        workspace, budget, checks, manifest_hash = load_manifest(manifest_path)
        helper_hash = sha(Path(__file__))
        output = args.output.resolve()
        if not output.is_relative_to(workspace) or output.exists():
            raise ValueError("output must be a new path inside the declared workspace")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.exit(2, "manifest error: " + str(error) + "\n")
    started = time.perf_counter()
    baseline_failed = False
    records = []
    for check in checks:
        remaining = budget - (time.perf_counter() - started)
        if baseline_failed:
            record = {"id": check["id"], "phase": check["phase"], "status": "skipped_baseline_failure"}
        elif remaining <= 0:
            record = {"id": check["id"], "phase": check["phase"], "status": "skipped_budget_exhausted"}
        else:
            record = execute(check, workspace, remaining)
            if check["phase"] == "baseline" and record["status"] != "pass":
                baseline_failed = True
        records.append(record)
        print(json.dumps({"id": record["id"], "phase": record["phase"], "status": record["status"]}), flush=True)
    source_hashes_after = {}
    for label, path in (("manifest", manifest_path), ("helper", Path(__file__))):
        try:
            source_hashes_after[label] = {"sha256": sha(path)}
        except OSError as error:
            source_hashes_after[label] = {"sha256": None, "error": type(error).__name__ + ": " + str(error)}
    sources_changed = (source_hashes_after["manifest"]["sha256"] != manifest_hash or
                       source_hashes_after["helper"]["sha256"] != helper_hash)
    report = {
        "format": "command-evidence/v1", "completed_utc": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace), "manifest_sha256": manifest_hash,
        "helper_sha256": helper_hash, "evidence_sources_after": source_hashes_after,
        "evidence_sources_changed": sources_changed, "python_version": sys.version.split()[0],
        "node_path": shutil.which("node"), "budget_seconds": budget,
        "elapsed_seconds": time.perf_counter() - started, "baseline_failed": baseline_failed, "results": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if not sources_changed and all(record["status"] == "pass" for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
