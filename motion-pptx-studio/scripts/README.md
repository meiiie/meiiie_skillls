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
| `make_assets_example.py` | 2 | procedural gold-leaf textures, layered object drawings, duotone photos (adapt to your TRUE list) |
| `check_fonts.py` | 3 | glyph coverage for a language (`--lang vi`), variable-font warning, sample render |
| `words_budget.py` | 4, 6 | `plan` a word budget from minutes and slides; `measure` notes/deck against a target |
| `build_deck.py` | 5 | JSON spec → .pptx with named shapes; keyframes via `"from": "prev"` |
| `ooxml.py` | 5 | unpack / pack / order / inventory / sequence / clean / ensure-notes / notes-get / notes-set |
| `motion.py` | 5 | one Morph per slide, `@fade/@float/@wipe/@blink` from names, durations from motion.json; idempotent |
| `roles.py` | 5 | three-column highlight-walk keyframes on an OOXML slide |
| `check_deck.py` | 5, 6 | transitions, `!!` pairs, CJK, leftovers, fonts, media, anchor count; exit 1 on errors |
| `render.sh` | 5, 6 | LibreOffice → PDF → slide-NN.jpg + contact sheets (isolated profile) |
| `finish_dedupe.py` | 6 | merge identical media, downscale oversized images |
| `script_docx.py` | 6 | speaker-script .docx with scenes and time estimates (same counting as words_budget) |
| `deliver.py` | 6 | deliver/: pptx + docx + fonts (+ README, OFL) + CREDITS + zip |
Companion skills carry copies of some of these; `bash ../sync_companions.sh` refreshes them from this folder.
