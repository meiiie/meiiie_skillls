# Source findings and custom adaptations

Primary repository documentation was read on 2026-10-04. No upstream executable or implementation was installed, downloaded as software, or run. This toolkit uses independently authored code.

| Source | Documented idea | Custom decision |
| --- | --- | --- |
| [crapper](https://github.com/unclebob/crapper) | Combines cyclomatic complexity and test coverage; missing tools or failed coverage runs can produce 0% coverage, while no-coverage mode reports unavailable values. | Prioritize branching plus actual test evidence. Preserve unavailable/failed measurements as separate states. No CRAP score is manufactured for this pilot. |
| [dryer](https://github.com/unclebob/dryer) | Reports structural similarity candidates using normalized fingerprints. | Review whether repeated code represents the same rule before extracting anything. No clone detector or similarity metric was built for this tiny fixture. |
| [mutator](https://github.com/unclebob/mutator) | Requires a passing baseline; groups test failures, timeouts and noncompiling replacements as killed; excludes uncovered sites from its displayed denominator. Differential runs retain kills when function text is unchanged. | Use explicit domain faults and distinguish assertion detections from invalid syntax, timeout and infrastructure cases. Recreate fresh runs after test-only changes; show every declared semantic fault in the denominator. |
| [uml-viewer](https://github.com/unclebob/uml-viewer) | Separates dependency topology from metric snapshots and labels proposed architecture. | Use a small source-backed dependency sketch when relevant, with measured evidence separate from proposed changes. No interactive viewer or agent companion was built or launched. |

These are design choices inferred from the documentation, not proof that this small pilot reproduces upstream behavior or scales across languages.

## Preventive typed-design addition

The [pstack principles](https://github.com/cursor/plugins/tree/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack) by Lauren Tan supplied additional design references for concrete type invariants, owned boundary parsing and reduced reader indirection. Current pinned manifest: 0.15.9; license: MIT. Our [preventive gate](preventive-types.md) is independently authored, uses project-native checks, and preserves static/runtime/escape-review limits. No pstack source implementation, substantial text or required orchestration is included. Attribution and the original license link are retained in that reference; this is not a license grant for the repository.
