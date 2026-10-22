# Changelog

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
