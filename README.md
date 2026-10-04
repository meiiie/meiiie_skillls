# meiiie_skillls

## Available skills

| Skill | Status | Purpose |
| --- | --- | --- |
| [contest-code-quality](contest-code-quality/SKILL.md) | Experimental | Bounded correctness and refactoring workflow with an optional command-evidence helper. |
| [meiiie-explain-clearly](meiiie-explain-clearly/SKILL.md) | Available | Precise Vietnamese/English explanations and teaching media chosen by the learning need. |
| [meiiie-interactive-webgl](meiiie-interactive-webgl/SKILL.md) | Available | Semantic 3D objects, reversible assembly, accessible controls and explicit render checks. |

Read [SKILL.md](contest-code-quality/SKILL.md) for the workflow and [command-evidence.md](contest-code-quality/references/command-evidence.md) before running a reviewed project manifest. The helper uses Python's standard library and already installed runtimes; no fixed model or agent team is required.

On Windows with Python 3.13.7 and Node 25.9.0, seven validation groups and fourteen grouped CSV CLI/live HTTP checks passed. Two independent controls exposed provenance and report-preservation defects; one repair and fresh rechecks addressed those cases. This is experimental evidence, with limits documented in the skill, rather than tooling parity, production assurance or UI/video quality.

Primary-source ideas are attributed in [source-adaptations.md](contest-code-quality/references/source-adaptations.md). The linked third-party tools' implementation and binaries are not included. This entry makes no repository-wide license grant. Private command outputs and experiment bundles are excluded.

The existing code-quality workflow now includes a [thin preventive typed-design gate](contest-code-quality/references/preventive-types.md). Its isolated TypeScript pilot checked invalid-state rejection, canonical exhaustiveness, runtime parsing and explicit escape/config controls, with two frozen independent scenarios. Results and limits are documented in that reference; runtime and UI checks remain separate. No pstack orchestration or installation is required.

## Explain clearly

[Meiiie Explain Clearly](meiiie-explain-clearly/SKILL.md) frames the learning goal, preserves meaningful qualifications, and selects text, diagrams, interactive HTML or video when useful. It includes original Vietnamese/English worked examples and [clarity/source notes](meiiie-explain-clearly/references/clarity-and-sources.md) with official ASD/STEMG attribution.

It uses STE-inspired clarity. “About 80% STE” is a soft editorial direction, not a measured score or ASD-STE100 compliance claim. The full standard and controlled dictionary are not included. The skill does not bind a model or provider, and its publication does not establish learning effectiveness or artifact QA. No repository-wide license grant is added.

## Interactive WebGL

[Meiiie Interactive WebGL](meiiie-interactive-webgl/SKILL.md) is a procedural workflow for inspectable 3D objects, semantic selection, reversible exploded views and explanatory effects. Its [architecture](meiiie-interactive-webgl/references/architecture.md) and [acceptance gates](meiiie-interactive-webgl/references/render-gates.md) keep logic, rendered inspection, interaction and real-device measurements separate.

The package contains instructions, metadata, an icon and primary-source notes. It includes no reference media or demo implementation; publishing the skill does not establish render quality, measured performance, physical-phone behavior or engineering accuracy.
