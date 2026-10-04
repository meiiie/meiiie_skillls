# Software and IT delivery

## Establish the executable scope

Identify the repository or system, target environment, desired behavior, reproducible starting state, acceptance tests, release constraints, and permitted mutations. Respect the user's selected environment and repository instructions. Inspect before changing; do not substitute a different machine or deployment target silently.

Select only useful roles: an implementation lead, domain specialist, test/review specialist, or release operator. Separate authorship and review for consequential changes when available. Keep one owner for overlapping files or coordinate commits explicitly.

## Build and verify

1. Reproduce the reported problem or establish a baseline. Record existing failures separately from introduced ones.
2. Choose the smallest coherent change that meets the criteria. Preserve unrelated user changes and public interfaces unless explicitly in scope.
3. Write or update focused tests. Run relevant unit, integration, static, security, and end-to-end checks according to the change's risk; do not inflate the checklist with irrelevant checks.
4. Review the actual diff and behavior. Check failure paths, data handling, compatibility, observability, and secrets exposure where relevant.
5. Record commands, environment, results, and limitations. “Not run,” “failed,” and “passed” must remain distinct. Never infer successful tests from the presence of a test file.

For user-facing changes, inspect the rendered result or actual interaction when possible. Screenshots supplement functional evidence; they do not replace it.

## Release boundaries

Keep local edits, committed changes, published branches, merged code, deployed code, and verified live behavior distinct. Do not treat approval to write code as blanket authority to change production, account access, security settings, or spending.

For consequential deployment or migration, prepare rollback or recovery steps, preconditions, relevant backup status, and a verification plan. Do not claim rollback is safe without checking what it restores and what it cannot restore. Obtain approvals required for the actual target and operation.

Completion evidence: artifact or diff, behavior against acceptance criteria, tests actually run, unresolved risks, release state, and recovery notes when applicable. If CI is still running or a rollout is pending, report that state honestly and follow the user's requested completion boundary.
