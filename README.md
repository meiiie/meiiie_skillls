# meiiie_skillls

## Available skills

| Skill | Status | Purpose |
| --- | --- | --- |
| [contest-code-quality](contest-code-quality/SKILL.md) | Experimental | Bounded correctness and refactoring workflow with an optional command-evidence helper. |
| [meiiie-explain-clearly](meiiie-explain-clearly/SKILL.md) | Available | Precise Vietnamese/English explanations and teaching media chosen by the learning need. |
| [meiiie-interactive-webgl](meiiie-interactive-webgl/SKILL.md) | Available | Semantic 3D objects, reversible assembly, accessible controls and explicit render checks. |
| [meiiie-operating-office](meiiie-operating-office/SKILL.md) | Available | Task-scoped coordination with one accountable lead, bounded specialist work and evidence-based review. |
| [neko-wiii-product-studio](neko-wiii-product-studio/SKILL.md) | Available | Neko Core and Wiii ownership, shared contracts and integration acceptance. |
| [motion-pptx-studio](motion-pptx-studio/SKILL.md) | Available | v6.2 principle-based PowerPoint decks: ManimGX and Anatomy are mandatory, install first, and never fall back silently. |
| [heritage-visual-research](heritage-visual-research/SKILL.md) | Available | Sourced facts, true/wrong motif lists, anatomy checks and licensed images for cultural topics. |
| [presentation-speech-craft](presentation-speech-craft/SKILL.md) | Available | Hook, anchor phrase, pauses, circular close, word budget and a speaker-script document. |

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

## Operating Office

[Meiiie Operating Office](meiiie-operating-office/SKILL.md) coordinates substantial software/IT, academic research and procurement assignments through one accountable lead and the smallest useful team. It includes domain playbooks and templates for work briefs, results and proportionate review.

This is an instruction and template layer. Installation does not establish persistent workers, background execution, independent identities, new permissions or demonstrated research effectiveness; actual tools and artifacts establish what happened. Its [operating rationale](meiiie-operating-office/references/operating-rationale.md) preserves source attribution and implementation limits.

## Neko and Wiii Product Studio

[Neko and Wiii Product Studio](neko-wiii-product-studio/SKILL.md) defines task-scoped ownership for Neko Core, Wiii and their integration. It includes a project brief, an integration contract checklist and a [dated orientation](neko-wiii-product-studio/references/project-baseline.md) with immutable source links.

The accepted product direction and historical audit findings guide current inspection; they do not establish that current repositories conform, that their boundary is fully implemented, or that end-to-end integration has passed. This skill adds no persistent workers, permissions or release authority.

## Motion PPTX Studio

[Motion PPTX Studio](motion-pptx-studio/SKILL.md) (v6.2) is a short, principle-based workflow. Step 0 installs
and smoke-tests [ManimGX](motion-pptx-studio/principles/manimgx-first.md) and
[Anatomy](motion-pptx-studio/principles/anatomy-first.md) before any design. If either cannot run, stop and
report it. Canvas and native motion are fallbacks only after the user has been told and the reason is in
NOTES.md. Any structure or process needs at least one Anatomy film. There is no house style. Palette and
fonts come from the deck. The default palette is neutral greyscale and the default fonts are DejaVu.
Principles live in [principles/](motion-pptx-studio/principles/one-concept.md), including
[art direction](motion-pptx-studio/principles/art-direction.md) and
[examples are a yardstick, not a mold](motion-pptx-studio/principles/examples-are-a-yardstick-not-a-mold.md).

`python3 scripts/build.py` builds the deck, applies motion, packs, renders to a new `renders/rN` folder, and runs
`film_check`. A deck with fewer than two films fails. Yardsticks, not templates:
[Trái Đất](motion-pptx-studio/examples/reference-trai-dat/README.md),
[Bưu điện ánh sáng](motion-pptx-studio/examples/space-buu-dien-anh-sang-v2/README.md), and
[Khí áp](motion-pptx-studio/examples/flagship-khi-ap/README.md). The old paper-editorial pack remains only as an
optional illustration inside the Khí áp example. See
[deck-json.md](motion-pptx-studio/references/deck-json.md) and
[manimgx-quirks.md](motion-pptx-studio/references/manimgx-quirks.md).

v5 gates, the design genome, the router, the style-pack library, and the test suites are removed.

## Heritage visual research

[Heritage Visual Research](heritage-visual-research/SKILL.md) collects sourced facts, a true/wrong motif list, an object anatomy checklist and openly licensed images before a cultural visual is designed. Templates live in [templates/](heritage-visual-research/templates/facts.md). Shared scripts are copies of the Motion PPTX Studio originals.

## Presentation speech craft

[Presentation Speech Craft](presentation-speech-craft/SKILL.md) writes the spoken track: a hook, an anchor phrase, marked pauses, a circular close, a word budget and a speaker-script document. It can time a deck that was built elsewhere. The lesson template is [templates/lessons.md](presentation-speech-craft/templates/lessons.md).

## Install these three skills

Copy the folders into the harness skill directory, then check the toolchain once per machine. Motion PPTX Studio v6.2 needs Python 3.9+ (Python 3.13+ for ManimGX), python-pptx, Pillow, LibreOffice, poppler, and ffmpeg. ManimGX and Anatomy (Node 20.10+ and Chrome) are required; install and smoke-test both before building. The companion skills still use their own scripts.

```bash
# Claude Code
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.claude/skills/
# Codex (personal, or .agents/skills/ inside a repo)
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.agents/skills/
# Cursor (~/.cursor/skills/ or .cursor/skills/; also reads .agents/skills and .claude/skills)
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.cursor/skills/
```

A generic shell agent follows [motion-pptx-studio/SKILL.md](motion-pptx-studio/SKILL.md) directly. Optional external skills (Anthropic `pptx` / `docx`) are never required.
