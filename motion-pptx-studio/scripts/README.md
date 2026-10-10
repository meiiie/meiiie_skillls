# scripts/: one line each (run any with -h)

| Script | Phase | Purpose |
|---|---|---|
| `setup.sh` | 0 | check (default) or `--install` the toolchain; `--with-rembg` for AI cut-outs |
| `gates.py` | all | `init WORK --kind …` creates the project; `check WORK --gate N` enforces Gates 0–6 |
| `video_frames.py` | 1 | time-coded frames + contact sheet from a video (user media audit, reference talks) |
| `fetch_commons.py` | 2 | `search` Commons + Openverse with licence metadata → candidates + contact sheet; `keep` downloads full size and writes CREDITS |
| `contact_sheet.py` | 2, 5 | grid of images with captions, for looking at many images at once |
| `cutout.py` | 2 | plain-background object → transparent PNG (`--rembg` for busy backgrounds) |
| `inpaint_text.py` | 2 | remove text or foreign script from photo regions (OpenCV TELEA + grain) |
| `make_assets.py` | 2, 3 | the asset kit: `ground` (lacquer, noir, paper, clean, halftone, flat), `foil` (SVG/PNG → gold, silver, copper, bronze, ink, chalk, neon, metal), `layers` (one PNG per `<g id>` on one canvas), `photo` (duotone, sepia, mono, grade, `--pair`), `glow`, `pattern` |
| `make_assets_example.py` | 2 | the ca trù drawings of the reference deck (đàn đáy in three parts, medallion, phách, trống chầu, basin, tally, mat band): a worked example of drawing TRUE objects in SVG |
| `fetch_fonts.py` | 3 | a style pack's fonts as static TTFs + OFL (npm `@expo-google-fonts`, then google/fonts); `--install`, `--check vi` |
| `check_fonts.py` | 3 | glyph coverage for a language (`--lang vi`), variable-font warning, sample render |
| `words_budget.py` | 4, 6 | `plan` a word budget from minutes and slides; `measure` notes/deck against a target |
| `studio.py` | 3–5 | `new` (style pack + starter deck), `build` (build → motion → pack → render → audit), `compare` (your sheet above the reference), `fonts` |
| `build_deck.py` | 3–5 | deck.json → .pptx: style packs, chrome, roles, grid, grounds, shadows, image effects, groups, components (heading, card, stat, screen, timeline, bars, list, quote), layout warnings, motion.json |
| `typeset.py` | 5 | measure text with the installed font (used by build_deck and craft_audit) |
| `ooxml.py` | 5 | unpack / pack / order / inventory / sequence / clean / ensure-notes / notes-get / notes-set |
| `motion.py` | 5 | one Morph per slide, `@fade/@float/@wipe/@blink` from names, durations from motion.json; idempotent |
| `roles.py` | 5 | three-column highlight-walk keyframes on an OOXML slide |
| `check_deck.py` | 5, 6 | transitions, `!!` pairs, CJK, leftovers, fonts, media, anchor count; keyframe delta, image reuse, editorial-left layout, on-slide words; the craft audit; a `.pdf` is audited the same way; exit 1 on errors |
| `visual_audit.py` | 4, 5, 6 | the same visual measurements on a pptx or PDF (also imported by `gates.py` and `check_deck.py`); hold beats allowed one per scene |
| `craft_audit.py` | 5, 6 | persistent system (error), overflow into other text, safe area, type scale, flat grounds, contrast with renders |
| `render.sh` | 5, 6 | LibreOffice → PDF → slide-NN.jpg + contact sheets (isolated profile) |
| `finish_dedupe.py` | 6 | merge identical media, downscale oversized images |
| `script_docx.py` | 6 | speaker-script .docx with scenes and time estimates (same counting as words_budget) |
| `deliver.py` | 6 | deliver/: pptx + docx + fonts (+ README, OFL) + CREDITS + zip |
Companion skills carry copies of some of these; `bash ../sync_companions.sh` refreshes them from this folder.

Tests: `python -m pytest tests -q` (set `MOTION_REF_DECK=/path/NEKO_CORE_CaTru_motion.pptx` to include the reference-deck regression).
