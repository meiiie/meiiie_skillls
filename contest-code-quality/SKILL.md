---
name: contest-code-quality
description: Experimental workflow for bounded, evidence-driven correctness and simplification in contest coding tasks and prototypes. Use when tests, semantic faults, risky branching, repeated rules, or dependency boundaries need evaluation; adapt checks to the actual contract and deadline.
---

# Contest code quality

Turn a concrete behavior or change into a small, reviewable implementation with reproducible evidence. Start from the user's actual contest task, rules, constraints and available runtime. This workflow does not supply contest eligibility or authority to install, spend, transmit data or publish.

Keep implementation, acceptance design and verification as task responsibilities; one agent may fill several roles. Use available approved models and runtimes without binding a role to a model or requiring a fixed team. This skill is experimental: the small pilots support specific behavior, not parity with another author's tooling.

## Establish a reliable baseline

Write the observable contract before choosing checks: valid inputs, exact boundaries, failure behavior, precedence/fallback semantics and the requested endpoint. Separate known requirements from assumptions. Run the relevant existing tests on clean source; record source/test hashes, runtime and command. A failing or unavailable baseline blocks mutation claims. Preserve user work with a task-local copy when experimenting.

For a fresh task, derive concrete acceptance criteria from the brief and build a first runnable slice before expanding. Establish happy-path and error checks, then exercise the actual CLI, API or UI endpoint. Assert the contract's observable meaning; avoid requiring an unspecified newline or formatting convention. State any adopted convention before scoring it.

Choose the smallest risky behavior. Prioritize meaningful branches, unverified error paths and repeated domain rules. Treat unavailable coverage or metrics as unknown. Numeric risk and duplicate-shape reports guide inspection; they do not prove defects or justify automatic abstraction. For source background and adaptations, read [references/source-adaptations.md](references/source-adaptations.md).

For repeatable command records, optionally use [scripts/run_checks.py](scripts/run_checks.py) with [references/command-evidence.md](references/command-evidence.md). Its reviewed command arrays support existing runtime adapters, explicit assertion evidence, clean-baseline gates, finite budgets and hashes. Missing runtimes remain failures; no install is automatic. Keep syntax rejection, unknown nonzero exits and runtime failures separate from assertion detections. Use the project's actual interface oracle and retain private output locally.

## Prevent defects in the representation

Before editing a risky type or boundary, name the concrete invariant and its bad example. Use distinct states and exhaustive consumers when they rule out a real contradiction; parse external unknown data instead of asserting its type. Keep only the abstraction needed to express that rule.

Read [references/preventive-types.md](references/preventive-types.md) for the thin preventive gate: positive/negative compilation, real consumer exhaustiveness, boundary tests, and review of unsafe assertions, suppressions, imports and effective compiler configuration. Use the project's existing toolchain and actual contract. Type evidence complements runtime/integration/UI checks and the feedback loop below; it does not replace them or prove every value invariant.

## Test whether the tests discriminate

Use a bounded set of explicit faults justified by the contract, such as exclusive instead of inclusive boundaries, accepting an invalid sentinel, or treating valid empty input as missing. State the distinguishing input and observable consequence for each. Keep a pristine source and one private copy per fault. Validate that each patch matches exactly one intended site.

Check syntax separately, then run deterministic tests under a finite timeout. Keep assertion detections, unexpected runtime errors, invalid syntax, timeouts, infrastructure failures, equivalent behavior, survivors and measured uncovered sites separate. Do not turn a timeout or missing tool into a correctness success. State the denominator and exclusions. Surviving tests alone cannot prove equivalence.

Record exact patches, outputs and hashes. Run fresh after test changes; any cache would need the source, tests, fixtures, configuration, runtime and harness identity. If the same author knows the faults while writing tests, disclose that evaluation leakage; a reserved fault is not independent merely because it was run later.

When an independent challenge is useful and delegation is authorized, give its designer the brief, accepted conventions and skill without the implementation, existing tests or suspected fixes. Freeze the design's inputs, timestamp and hashes; freeze source and baseline tests before revealing challenges. Distinguish blind challenge design from exact source patches adapted after disclosure. A design-only pass makes no executable baseline claim.

## Repair only what evidence warrants

For a meaningful survivor, add a contract-level example or invariant that fails for the observed faulty behavior and passes for clean behavior. Include nearby valid boundaries where rejection logic might become overstrict. If real source behavior violates the contract, repair source within the authorized task; if the evidence only exposes weak tests, keep the implementation unchanged.

Default to one repair/recheck round for a small pilot; adjust the budget to task risk and deadline. Rerun clean tests, regenerate all affected faults from pristine source, and verify hashes. Stop when the allocated budget expires, evidence plateaus, or a required dependency is unavailable; report the remaining defect rather than extending the loop silently.

## Use structure reviews when they change a decision

When duplication is demonstrated, ask whether the repeated code expresses the same rule and should change together. Extract only a coherent shared rule; similar syntax can encode different policies. After a refactor, rerun behavior tests and the relevant fresh mutants.

For changes spanning modules, keep a small dependency map tied to actual imports/calls and label any proposed structure as a proposal. Focus on an observed cycle or responsibility leak. A one-module task may need no architecture diagram. Do not expand a contest prototype into a generalized framework merely to improve a metric.

Deliver the artifact plus baseline/recheck results, exact remaining failures, scope, local time/cost, hashes and limits. Build or unit-test evidence supports only the exercised code behavior. Verify the requested user-facing endpoint separately, using the checks that actually fit it.
