# Dated project orientation

Verified upstream snapshot supplied from repository inspection on 2026-09-30. These facts guide discovery; recheck current commits and code before relying on them for a new assignment.

## Neko Core

Repository: https://github.com/meiiie/neko-core

Snapshot: `1cdd298579d2f9b07f65b3e94f42cebaf5ed5b72` on main, dated 2026-09-24.

- [package.json](https://github.com/meiiie/neko-core/blob/1cdd298579d2f9b07f65b3e94f42cebaf5ed5b72/package.json) reports version 1.7.0 and `@agentclientprotocol/sdk` 1.3.0
- [src/adapters/acp.ts](https://github.com/meiiie/neko-core/blob/1cdd298579d2f9b07f65b3e94f42cebaf5ed5b72/src/adapters/acp.ts) implements an ACP v1 JSON-RPC boundary over newline-delimited stdio and references Wiii computer tooling, host MCP/profile handling, and session lease/writer behavior
- The inspected adapter selects host-profile authority from a trusted launcher boundary, not arbitrary ACP input; preserve and reverify that trust boundary when modifying integration
- [scripts/acp-smoke.ts](https://github.com/meiiie/neko-core/blob/1cdd298579d2f9b07f65b3e94f42cebaf5ed5b72/scripts/acp-smoke.ts) provides a no-model smoke path for the compiled `neko acp` initialization/authentication advertisement; this is narrower than full end-to-end validation

## Wiii

Repository: https://github.com/meiiie/wiii

Snapshot: `31ba311a73cec24560b455cf4134b579636b760d` on main, dated 2026-09-22.

- [CHANGELOG.md](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/CHANGELOG.md) describes stable 1.2.0, Neko as the default harness, explicit alternative harnesses preserved, and local-first behavior with optional Service
- Treat these as documented product claims until the relevant implementation and tests have been inspected for the current task

## Cross-product boundary audit

Findings from inspection of the snapshot pair above on 2026-09-30; confirm behavior with the task's contract matrix and runtime tests before release.

- Wiii's [native Neko module](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src-tauri/src/neko/mod.rs) launches `neko acp` with an optional profile and manages the native process/host side. Its [ACP driver](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src/neko-chill/drivers/acp/driver.ts) communicates using JSON-RPC over stdio.
- ACP v1 is the external Wiii–Neko boundary. Neko Control v1 is a distinct internal Wiii boundary: [protocol types](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src/neko/control-protocol.ts), [client](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src/neko/control-client.ts), and [contract specification](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/specs/941-neko-durable-runtime/contracts/neko-control-protocol-v1.md). Do not merge these names or their compatibility/version rules.
- The audit found a coverage distinction: the Control schema lists initialize, session-resume, and approval-resolve, while the [Tauri command surface](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src-tauri/src/commands/neko_agent.rs) does not implement every schema operation uniformly; resume and approval currently have direct ACP-driver paths. Treat this as an audit finding to resolve in an implementation/contract matrix, not a proven runtime defect or a uniformly implemented API. Inspect [protocol tests](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src/__tests__/neko/control-protocol.test.ts) and [ACP driver tests](https://github.com/meiiie/wiii/blob/31ba311a73cec24560b455cf4134b579636b760d/wiii-desktop/src/__tests__/neko-chill/acp-driver.test.ts) alongside implementation.
- Wiii's local GUI integration is Neko Chill; the ADE shell is a preview. Keep Wiii transcript/checkpoint and lifecycle-journal responsibilities distinct from Neko agent continuation. The audit did not establish full stdout/tool-delta durable replay or an independent daemon; do not promise either from the presence of a journal or specification.
- Neko's inspected ACP adapter supports session new/list/load/resume/close, streaming, and request_permission. For Wiii Computer integration, distinguish Neko agent-loop and gate decisions from Wiii provisioning, project grants, display handling, and native leases. End-to-end cancellation/disconnect lease cleanup remained untested in this audit.

## Workspace caution

An audit can encounter a substantially older local Neko checkout or a Wiii worktree with unrelated changes. This is a reason to verify environment, HEAD, and dirty state, not to encode a canonical local path or automatically reset a repository. Historical workspace observations are not a current authorization or permanent repository property.
