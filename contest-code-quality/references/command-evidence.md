# Command evidence (experimental)

Use `scripts/run_checks.py` when a small project needs repeatable command records. It runs reviewed argument arrays with Python's standard library, records results, and leaves mutation creation and domain oracles with the project. It is optional. It is not a security sandbox, language parser, mutation engine or process-tree supervisor.

Run from the skill folder, or pass its absolute script path:

```text
python scripts/run_checks.py /path/to/checks.json --output /path/to/project/evidence/checks.json
```

The output must be a new path inside the declared workspace. Existing evidence is preserved. Example manifest, with project-specific test paths to replace:

```json
{
  "version": 1,
  "workspace": "/path/to/project",
  "budget_seconds": 30,
  "checks": [
    {
      "id": "clean-tests",
      "phase": "baseline",
      "argv": ["{python}", "tests/test_cli.py"],
      "cwd": ".",
      "timeout_seconds": 5,
      "result_mode": "exit",
      "hash_inputs": ["src/main.py", "tests/test_cli.py"]
    },
    {
      "id": "actual-interface",
      "phase": "check",
      "argv": ["{node}", "tests/http-check.mjs"],
      "timeout_seconds": 10,
      "result_mode": "exit",
      "hash_inputs": ["src/server.mjs", "tests/http-check.mjs"]
    }
  ]
}
```

The manifest directory is the default workspace. A declared workspace can be absolute or relative to the manifest. Every cwd, hash input and output must stay within its resolved workspace; this containment does not restrict arbitrary actions inside the reviewed child command.

Known optional runtime tokens are `{python}` (the current interpreter) and `{node}` (an already installed Node). Other languages may use their existing executable and declared project commands directly. No adapter or package is installed automatically. On Windows prefer explicit executables or direct Python/Node scripts; shell/batch command portability is untested. Review the command and project test scripts before running them, including any nested install/network actions.

## Results and mutation boundaries

`exit` mode records zero exit as `pass` and nonzero exit as `command_failure`. It does not infer an assertion or mutation kill from nonzero exit.

`quality-json` mode requires the last nonempty stdout line to be a trusted test-runner result such as:

```json
{"quality_result":{"status":"assertion_failure","checks":3,"failures":1}}
```

Allowed protocol statuses are `pass`, `assertion_failure` and `runtime_failure`. Counts must be integers with at least one check and failures no greater than checks. Passing requires zero failures and zero exit; failure statuses require positive failures and nonzero exit. Missing, inconsistent or malformed output is `protocol_error`. The protocol conveys the project's assertion evidence; it cannot itself prove the oracle is correct.

A manifest's `mutant` phase requires this explicit protocol and at least one preceding clean `baseline`. A failing baseline skips all later commands. For a mutant, `pass` means the tests survived; equivalence still requires a separate argument. Syntax checks should be separate declared commands, such as Node's built-in `--check`; inspect their diagnostics and retain invalid-syntax cases separately from assertion detections. The generic helper intentionally leaves those nonzero results unclassified as `command_failure`, rather than guessing from compiler text.

Other outcomes are `timeout`, `infrastructure_error`, `inputs_changed`, `input_hash_error`, `skipped_baseline_failure` and `skipped_budget_exhausted`. A hash error before execution prevents that command from starting; a hash error after execution retains its command result and diagnostic. Earlier records remain in the report. Each command has a finite timeout; the remaining total budget may shorten it. Configuration permits 1-32 commands, at most 60 seconds per command and at most 300 seconds of command-running budget. Initialization and evidence writing add overhead. These maxima are capability limits, not recommended test targets.

Records include resolved argv/cwd, exit, stdout/stderr, elapsed time, per-command before/after hashes, manifest/helper hashes and interpreter identity. The manifest identity hashes the same byte snapshot that was parsed before execution; the helper identity is captured before commands start. Final manifest/helper hashes are separate. A changed or unreadable final evidence source sets `evidence_sources_changed` and makes the overall exit nonzero, while preserving executed records. The helper executes the loaded manifest snapshot; it does not reload changed instructions. Node's path is recorded; add an explicit `node --version` check when its version matters. Cache identity also needs the project's fixture/config/runtime/environment/seed identity; this helper has no result cache. Do not dump secrets to capture environment identity.

## Practical limits and tested status

The helper directly supervises only its own child process. Project test commands must own and clean up their descendants. Stored stdout/stderr are truncated after 65,536 characters; capture itself is not a memory-limit mechanism. Use it for trusted, bounded commands. Missing tracked inputs are rejected before execution; changed tracked bytes after a command fail preservation. Do not put secrets in argv or publish private command evidence.

Tested here on Windows with Python 3.13.7 and Node 25.9.0: six classification controls, a failing-baseline gate, total-budget stopping, changed-input detection, Node protocol output, containment rejection, and real CSV CLI/live HTTP checks (14 grouped checks). This is seven validation groups including the controls and interface group, not a language or production-correctness guarantee. A separate reviewer designed two fresh controls without reading this validation, exposing manifest-identity and tracked-path evidence-loss defects. One bounded repair was followed by fresh validation and rechecks of those controls. Other operating systems, compilers, large output, grandchildren on timeout, package-manager commands and UI rendering remain untested.

Keep a task's actual command evidence private unless publication is explicitly authorized. A public skill package should contain authored instructions, helper source, relevant notices and truthful test status rather than raw private experiment output.
