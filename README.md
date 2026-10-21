# meiiie_skillls

## Available skills

| Skill | Status | Purpose |
| --- | --- | --- |
| [contest-code-quality](contest-code-quality/SKILL.md) | Experimental | Bounded correctness and refactoring workflow with an optional command-evidence helper. |
| [meiiie-explain-clearly](meiiie-explain-clearly/SKILL.md) | Available | Precise Vietnamese/English explanations and teaching media chosen by the learning need. |
| [meiiie-interactive-webgl](meiiie-interactive-webgl/SKILL.md) | Available | Semantic 3D objects, reversible assembly, accessible controls and explicit render checks. |
| [meiiie-operating-office](meiiie-operating-office/SKILL.md) | Available | Task-scoped coordination with one accountable lead, bounded specialist work and evidence-based review. |
| [neko-wiii-product-studio](neko-wiii-product-studio/SKILL.md) | Available | Neko Core and Wiii ownership, shared contracts and integration acceptance. |
| [motion-pptx-studio](motion-pptx-studio/SKILL.md) | Available | v5.3.1 designed, researched PowerPoint decks for any kind of talk: style packs, a motion library beyond Morph, signature moments (Anatomy, Manim, Codex), art directions, hard and soft gates, film and variety audits, a deck engine and a timed speaker script. |
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

[Motion PPTX Studio](motion-pptx-studio/SKILL.md) (v5.3.1) builds a PowerPoint deck as a short film shot on one set: a
style pack holds the system (material ground, chrome, grid, type roles), one signature object carries the deck, and
each scene uses a chosen motion vocabulary — Morph keyframes when PowerPoint 365/2019+ will play them, otherwise
classic transitions, entrances, paths and type. It covers product launches, pitches, business reviews and data stories,
lectures, events and heritage topics with one pipeline, gated from brief to delivery (Gates 0–6 in
[gates.py](motion-pptx-studio/scripts/gates.py)). The no-default-template rule is Gate 3: a written style
choice (including a rejected pack) and at least two techniques beyond Morph.

- Ten [style packs](motion-pptx-studio/references/styles.md): lacquer-heritage, noir-product, paper-editorial,
  boardroom-data, studio-pop, plus kinetic-type, blueprint, swiss-blue, neo-brutal and retro-terminal. Each of
  the new packs is a layout grammar, with OFL fonts that cover Vietnamese
  ([gallery](motion-pptx-studio/assets/reference/styles-gallery.jpg) of the first five). Three experimental packs
  (glass-tech, papercut-collage, desktop-os) are palette-only until their grammar is designed.
- A [motion library](motion-pptx-studio/references/motion-library.md) of 49 transitions and 24 effects.
  `compat` is `morph` (default), `safe` or `dual`: Morph is converted to classic animation automatically, and a
  no-Morph render gate checks that safe mode leaves no Morph behind.
- `studio.py new / build / compare`: a starter deck that proves the system, a one-command
  build → motion → render → audit loop, and a side-by-side with the
  [reference deck](motion-pptx-studio/references/reference-bar.md). `verify_motion.py` round-trips effects through
  LibreOffice, `preview_motion.py` writes a labelled simulation, and `diagram_video.py` builds a diagram film
  (Manim route or native shapes).
- A deck engine with components (heading, card, stat, screen, timeline, bars, list, quote) and layout warnings
  measured with the real font; an asset kit for grounds, foil drawings, layered parts and photo grading.
- Audits that fail stuck keyframes, one-template decks and decks without a persistent system, and pass the accepted
  reference deck. The v3 visual-audit gates are included. [Craft](motion-pptx-studio/references/craft.md),
  [pro craft](motion-pptx-studio/references/pro-craft.md) and
  [genre](motion-pptx-studio/references/genres.md) references. `check_deck.py --variety` measures technique,
  transition and composition variety, and flags a repeated text-left/photo-right fingerprint.
- v5.3 is a floor: at least two hand-built [signature moments](motion-pptx-studio/references/signature-moments.md)
  (Anatomy or Manim films of the subject's own mechanism, with a Codex asset path for textures and grounds),
  three [art directions](motion-pptx-studio/references/art-directions.md) before a style is chosen, and hard gates
  only for facts, licences and render integrity. v5.3.1 adds a film audit (no label under a video, poster colour
  against the page) and density and contrast floors for Anatomy posters.
  [Worked examples](motion-pptx-studio/examples/README.md) include the six-style phin deck and the earth-fall deck.

Morph plays in PowerPoint 365 / 2019+. PowerPoint 2016, Google Slides, Keynote and LibreOffice need `compat: safe`
or `dual`. Image search covers Wikimedia Commons and Openverse; museum sites stay manual. Installing the skill
does not review a deck in PowerPoint, embed fonts or grant licences for images. Motion in this release was
verified with LibreOffice; real PowerPoint playback is still unconfirmed. The examples use fictional products and illustrative numbers;
the reference renders credit their CC BY-SA photos in [assets/reference](motion-pptx-studio/assets/reference/README.md).

## Heritage visual research

[Heritage Visual Research](heritage-visual-research/SKILL.md) collects sourced facts, a true/wrong motif list, an object anatomy checklist and openly licensed images before a cultural visual is designed. Templates live in [templates/](heritage-visual-research/templates/facts.md). Shared scripts are copies of the Motion PPTX Studio originals.

## Presentation speech craft

[Presentation Speech Craft](presentation-speech-craft/SKILL.md) writes the spoken track: a hook, an anchor phrase, marked pauses, a circular close, a word budget and a speaker-script document. It can time a deck that was built elsewhere. The lesson template is [templates/lessons.md](presentation-speech-craft/templates/lessons.md).

## Install these three skills

Copy the folders into the harness skill directory, then check the toolchain once per machine. Python 3.9+ (python-pptx, lxml, Pillow, numpy, fonttools, python-docx, cairosvg), LibreOffice, poppler (`pdftoppm`) and fontconfig are required. ffmpeg, yt-dlp, scipy, OpenCV and pymupdf are recommended. `setup.sh --install` installs the Python packages (pip `--user`, or a venv when pip is locked) and prints the system-package command for binaries. It does not run sudo.

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
