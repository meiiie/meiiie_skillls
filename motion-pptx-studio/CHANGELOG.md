# Changelog

## 6.2.0 (2026-10-22)
Anatomy is now as strict as ManimGX.

### Added
- **principles/anatomy-first.md:**
  - when Anatomy is required (any structure or process: at least one Anatomy film per deck);
  - install with `setup_anatomy.sh`, plus the GitHub-tarball route for sandboxes with no git access;
  - the smoke test, how anatomy_film.py works, its flags and the figure recipe;
  - the rule: stop and report, never skip silently.
- **scripts/anatomy/smoke.mjs:** a 10-line figure that renders a 3-second test film.

### Changed
- **SKILL.md:** step 0 now sets up ManimGX AND Anatomy; the films step, index and description
  are updated.
- **film-is-the-core:** Anatomy is required for any structure or process.
- **manimgx-first:** points to anatomy-first.
- **setup_anatomy.sh:** documents the tarball route. Its failure message now says stop and report,
  and no longer points to the deleted v5 diagram_video.py.
- **anatomy_film.py:** dead links to the v5 signature-moments.md now point to anatomy-first.

## 6.1.0 (2026-10-22)
**Why.** In a ChatGPT test the agent built a 30-slide deck with no films and delivered it as a PDF.
v6.0 treated Manim as optional and gave no install path. The agent ran `pip install manimgx` on
Python 3.11 and got "no matching distribution" (ManimGX needs Python 3.13 or newer), so it quietly
fell back.

### Added
- **principles/manimgx-first.md:**
  - links to the docs and to llms.txt;
  - three install routes (venv with Python 3.13+, uv tool, or the standalone offline binary);
  - a 10-line smoke scene and the render flags;
  - the rule: install and smoke-test first, and if ManimGX is impossible, stop and report it.
- **Anatomy docs link** for isometric machine films.

### Changed
- **ManimGX is mandatory.** This is now in SKILL.md (a new step 0, step 5, the index), in
  film-is-the-core and in the film_check message.
- **canvas_film and native motion are reported fallbacks only.** They need the user to have been
  told and the reason in NOTES.md.
- **Deliverable:** a .pptx with the mp4 films embedded plus the mp4s alongside. Never a PDF only.

## 6.0.0 (2026-10-22)
Rewritten as a compressed skill: principles first, tools second.

### Changed
- **SKILL.md** is now about 50 lines: a 5-step workflow and an index.
- **Principles:** 13 short files (10–20 lines each) replace the long rulebook.
- **Films are mandatory.** Each film is the deck's core and has a route fallback: Manim, then
  the pure-Python canvas (`canvas_film.py`), then the Anatomy isometric machine.
- **Native fallbacks** stay editable.
- **One-command build:** `scripts/build.py` runs build_deck → motion → pack → render →
  `film_check`. It writes each render to a new `renders/rN` folder.

### Added
- **principles/art-direction.md:** chapter palettes, a background on every slide, a picture
  for every hero number, type roles, one motif, and a board critiqued before building.
- **principles/examples-are-a-yardstick-not-a-mold.md.**
- **Examples:**
  - `examples/reference-trai-dat` (the yardstick contact sheet);
  - `examples/space-buu-dien-anh-sang-v2` (art direction, board and contacts).
- **references/manimgx-quirks.md:** Typst resolves fonts by typographic family plus weight.

### Removed
- Gates, the design genome, the router and the test suites from v5.x.
- **House style:**
  - `DEFAULT_PALETTE` is now neutral greyscale, and `DEFAULT_FONTS` is DejaVu.
  - The film fonts come from each deck's `ds.py` and fall back to ManimGX-shipped faces.
  - `assets/styles/` is gone. The old paper-editorial pack now lives in
    `examples/flagship-khi-ap/` as `style-pack.optional-illustration.json`, labelled as an
    optional illustration only.
