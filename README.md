# meiiie_skillls

## Available skills

| Skill | Status | Purpose |
| --- | --- | --- |
| [contest-code-quality](contest-code-quality/SKILL.md) | Experimental | Bounded correctness and refactoring workflow with an optional command-evidence helper. |
| [meiiie-explain-clearly](meiiie-explain-clearly/SKILL.md) | Available | Precise Vietnamese/English explanations and teaching media chosen by the learning need. |
| [meiiie-interactive-webgl](meiiie-interactive-webgl/SKILL.md) | Available | Semantic 3D objects, reversible assembly, accessible controls and explicit render checks. |
| [meiiie-operating-office](meiiie-operating-office/SKILL.md) | Available | Task-scoped coordination with one accountable lead, bounded specialist work and evidence-based review. |
| [neko-wiii-product-studio](neko-wiii-product-studio/SKILL.md) | Available | Neko Core and Wiii ownership, shared contracts and integration acceptance. |
| [motion-pptx-studio](motion-pptx-studio/SKILL.md) | Available | Researched, licensed, Morph-animated PowerPoint decks with a timed speaker script and a gated pipeline. |
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

[Motion PPTX Studio](motion-pptx-studio/SKILL.md) (v2) builds a researched, licensed PowerPoint deck as Morph keyframe sequences, with a timed speaker script. The pipeline is gated from brief to delivery (Gates 0–6 in [gates.py](motion-pptx-studio/scripts/gates.py)): brief, research, assets, art direction, storyboard, group build and final delivery. [Harness notes](motion-pptx-studio/references/harness-adapters.md) cover Claude Code, Codex, Cursor, Grok Bot and a generic shell agent. Helper scripts are listed in [scripts/README.md](motion-pptx-studio/scripts/README.md).

Morph, entrance effects and blink play in PowerPoint 365 / 2019+. LibreOffice renders are static keyframes. Image search covers Wikimedia Commons and Openverse; museum sites stay manual. Installing the skill does not review a deck in PowerPoint, embed fonts or grant licences for images. Case studies and the quality bar are in the skill; they do not establish that a new deck has passed the gates.

## Heritage visual research

[Heritage Visual Research](heritage-visual-research/SKILL.md) collects sourced facts, a true/wrong motif list, an object anatomy checklist and openly licensed images before a cultural visual is designed. Templates live in [templates/](heritage-visual-research/templates/facts.md). Shared scripts are copies of the Motion PPTX Studio originals.

## Presentation speech craft

[Presentation Speech Craft](presentation-speech-craft/SKILL.md) writes the spoken track: a hook, an anchor phrase, marked pauses, a circular close, a word budget and a speaker-script document. It can time a deck that was built elsewhere. The lesson template is [templates/lessons.md](presentation-speech-craft/templates/lessons.md).

## Install these three skills

Copy the folders into the harness skill directory, then check the toolchain once per machine. Python 3.9+, LibreOffice and poppler (`pdftoppm`) are required. ffmpeg, yt-dlp and the Python image libraries are recommended. `setup.sh --install` installs the Python packages (pip `--user`, or a venv when pip is locked) and prints the system-package command for binaries. It does not run sudo.

```bash
# Claude Code
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.claude/skills/
# Codex (personal, or .agents/skills/ inside a repo)
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.agents/skills/
# Cursor (~/.cursor/skills/ or .cursor/skills/; also reads .agents/skills and .claude/skills)
cp -r motion-pptx-studio heritage-visual-research presentation-speech-craft ~/.cursor/skills/
bash motion-pptx-studio/scripts/setup.sh
```

A generic shell agent follows [motion-pptx-studio/SKILL.md](motion-pptx-studio/SKILL.md) directly. Per-harness differences are in [harness-adapters.md](motion-pptx-studio/references/harness-adapters.md). Optional external skills (Anthropic `pptx` / `docx`) are never required.

`motion-pptx-studio/scripts/` is the canonical copy of the shared scripts. After editing one, run `bash motion-pptx-studio/sync_companions.sh`.
