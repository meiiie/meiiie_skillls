---
name: neko-wiii-product-studio
description: Run Meiiie's task-scoped product studio for github.com/meiiie/neko-core and github.com/meiiie/wiii, with distinct Neko Core and Wiii teams and shared integration acceptance. Use for planning, auditing, implementing, reviewing, or releasing these products and their integration; not for unrelated coding tasks.
---

# Neko and Wiii Product Studio

Keep Meiiie accountable for the user's overall product outcome. Organize two distinct delivery teams around [Neko Core](https://github.com/meiiie/neko-core) and [Wiii](https://github.com/meiiie/wiii), with a shared integration workstream. Treat the teams as a reusable division of responsibility activated for actual assignments, not permanent running employees or autonomous infrastructure.

## Establish the live baseline

Read [references/project-baseline.md](references/project-baseline.md) as a dated orientation, then verify current repository evidence before making architecture or priority claims. For every assignment, establish the selected environment, exact repository, branch, HEAD commit, upstream relationship, dirty/untracked files, applicable repository instructions, and relevant tests. Capture immutable links for factual claims. Never assume a local checkout matches upstream or treat a remembered path as canonical.

Respect the user's environment selection. Do not pull, reset, clean, stash, overwrite, or publish unrelated work to make an audit convenient. Inspect stale or dirty workspaces first, isolate changes through an authorized method, and ask for a decision when ownership or the intended base is unclear. Do not copy credentials or private local state into task reports.

Use [assets/project-brief.md](assets/project-brief.md) for substantial work. Define the product outcome, acceptance criteria, scope, constraints, exact starting revisions, authority, and completion boundary before assigning work. Derive priorities from the current request and audit; do not invent a product roadmap from the baseline.

## Apply the accepted product direction

Use Neko Core as the single canonical Neko agent core, as directed by the user on 2026-09-30. Keep the model/tool loop, memory, compaction, and logical task/session semantics in Neko Core. Route Neko CLI and ACP/GUI execution through a shared implementation and verify their semantic parity with conformance tests. Fix core behavior once rather than maintaining parallel Neko harness logic in Wiii; Wiii changes may still be needed for an actual contract or presentation change.

Keep Wiii responsible for presentation, workspace/worktree orchestration, and host process/capability enforcement, rather than a second Neko model loop or memory stack. A native host runtime, lifecycle journal, or presentation cache is not by itself duplicated agent logic. Preserve supported third-party harness adapters unless the user requests their removal. Treat T3 as a source reference, not a required dependency or migration target.

This is the accepted architectural direction, not evidence that the current repositories already conform or currently contain duplicate logic. Establish any implementation gap through source inspection and tests before proposing a scoped change; do not infer duplication from component names or runtime boundaries.

## Assign ownership

- **Meiiie:** integrate findings, resolve cross-team tradeoffs within scope, manage blockers and approvals, and deliver the final user-facing result
- **Neko Core delivery lead:** own the canonical model/tool loop, memory, compaction, logical task/session semantics, shared CLI/ACP implementation, and core/conformance tests relevant to the assignment
- **Wiii delivery lead:** own GUI presentation, workspace/worktree orchestration, its native runtime/host boundary, process and host-capability enforcement, permission UX, third-party harness adapters, and application-side tests relevant to the assignment
- **Integration acceptance owner:** own the shared contract, compatibility matrix, cross-repository dependency order, and end-to-end acceptance evidence

Separate Wiii host enforcement and user-facing permission decisions from Neko agent decisions; map their joint protocol/host responsibilities from current source. Keep Neko logical session semantics separate from Wiii host-process lifecycle and presentation state; neither a visual-only Wiii nor a second Neko agent core is the intended boundary.

These are responsibility boundaries, not assertions that every component currently exists in either repository. Confirm code ownership from source before assigning a change. One person/agent may hold multiple roles for small work; identify that explicitly. Add specialists only for separable work or useful independent review. Do not require two teams to work when a task only affects one product.

Give each work package an owner, inputs, artifact, criteria, dependencies, and authority boundaries. Coordinate ownership of shared files and avoid concurrent conflicting edits. Assign exactly one executor for each external mutation, including publishing, deployment, or release. After uncertain success or a timeout, verify destination state before retrying.

## Govern the joint contract

Before changing the boundary between products, complete the applicable sections of [assets/integration-contract-checklist.md](assets/integration-contract-checklist.md). Record both exact product revisions, protocol version, contract owner, compatibility expectations, and acceptance checks. Separate protocol compatibility from application/product release numbering.

Preserve Wiii's existing provider and harness capabilities unless a change is explicitly authorized. Making Neko the default does not authorize deleting alternatives, removing local-first operation, or requiring an optional service. Inspect the actual capability paths and regression coverage before concluding what is supported.

Treat permissions, host capabilities, trusted-launcher selection, and tool execution as security boundaries. Never let untrusted protocol or user content silently select a more privileged host profile. Keep authority decisions at their verified trusted boundary and test denial paths as well as successful calls.

## Build, verify, and release

Use the current environment's supported engineering workflow and repository instructions. Keep implementation, tests, review, integration, and release status distinct. Run checks relevant to changed behavior; report actual commands, results, skipped checks, and baseline failures. A protocol initialization smoke test does not establish model execution, GUI integration, real tool permissions, or full end-to-end readiness.

Have the integration owner verify the agreed user journey across the exact revision pair, including applicable cancellation, errors, recovery, capability negotiation, and regressions in preserved alternatives. Use independent review for consequential cross-boundary or security changes when available; disclose limitations when only self-review occurred. Require evidence rather than consensus among role labels.

Before a consequential release, establish the authorized target, version pairing, migration and rollback/recovery plan, and post-release verification. Approval to plan or implement is not blanket approval to publish packages, deploy production, spend money, or expand access. Do not create new persistent services or claim continuous availability from this skill.

Deliver the artifact/diff, accepted criteria, exact versions tested, evidence, unresolved risks, actual release state, and narrow user decisions. If work is blocked, continue unaffected authorized work and name the precise missing input or approval. Do not mark integration complete merely because both repositories build separately.
