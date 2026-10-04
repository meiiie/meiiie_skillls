# Joint integration contract and acceptance

Apply only sections relevant to the requested change. Mark unknown or untested items explicitly; do not fill gaps with assumptions presented as facts.

## Identity and ownership

- Contract owner and single integration acceptance owner:
- Neko exact commit/version:
- Wiii exact commit/version:
- Relevant immutable source links:
- External ACP versus internal Neko Control boundary, implemented surface versus schema/specification:
- Protocol/version negotiation separate from product release numbering:
- Supported version pairs and behavior for unsupported peers:
- Owner and dependency order for each side of the change:

## Boundary behavior

- Transport, framing, lifecycle, startup, and shutdown:
- Message/schema compatibility and optional/required fields:
- Capability discovery and preservation of existing alternatives:
- Authentication advertisement versus actual authentication execution:
- Trusted launcher/host-profile authority and untrusted-input handling:
- Permissions and computer/tool execution boundaries:
- Streaming, progress, cancellation, and timeout semantics:
- Error mapping and user-visible failure messages:
- Neko continuation versus Wiii transcript/checkpoint/lifecycle journal; replay guarantees actually verified:
- Session persistence, writer ownership, reconnect, and recovery:
- Resource limits, sensitive logging, and compatibility/migration:

## Acceptance evidence

- Smallest representative user journey and expected observable outcome:
- Canonical Neko core path used by CLI and ACP/GUI, with source evidence:
- Conformance tests for shared model/tool-loop, memory, compaction, and logical task/session semantics:
- Any alleged duplicate agent logic distinguished from native host lifecycle or presentation state:
- Unit/contract checks on each affected side:
- Integration run using the exact revision pair:
- GUI interaction evidence where applicable:
- Denied permission, malformed input, unavailable capability, and failure-path checks:
- Regression checks for preserved non-Neko providers/harnesses and local-first behavior:
- What a smoke test proves and what remains untested:
- Commands/environment/results, baseline failures, and skipped checks:
- Independent review findings and resolution:
- Verdict: accepted / limited acceptance / revise / blocked:

## Release boundary, when requested

- Approved target, executor, version pairing, and publication scope:
- Migration and rollback/recovery preconditions:
- Destination-state check after uncertain action results:
- Post-release verification and ownership:
- Residual risk and user decision:
