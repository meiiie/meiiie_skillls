# Build engine (Phase 5)

Two ways to build, both ending in the same `ooxml.py` + `motion.py` + `check_deck.py` pipeline.

## A. Default: `build_deck.py` (JSON spec → .pptx); works everywhere
Write `WORK/deck.json`, build, render, look, edit the JSON, rebuild. No slide service needed.
```json
{
  "palette": {"bg": "#0E0A07", "ink": "#F1E4C8", "gold": "#C79A3B", "dim": "#8C7B63"},
  "fonts": {"display": "Cormorant Garamond SemiBold", "body": "Be Vietnam Pro"},
  "slides": [
    {"id": "s1k1", "bg": "bg", "notes": "Có một âm thanh…\n[ngừng 2 giây]",
     "shapes": [
       {"type": "line", "name": "!!str2", "x1": 6.67, "y1": 0.6, "x2": 6.67, "y2": 6.9, "color": "gold", "width": 1.25},
       {"type": "text", "name": "@fade1-anchor", "text": "Nghe bằng cả trái tim.", "x": 7.1, "y": 5.9, "w": 5.4, "h": 0.6,
        "font": "body", "size": 20, "color": "dim"}
     ]},
    {"id": "s1k2", "from": "prev", "notes": "…",
     "set":  {"!!str2": {"x1": 6.2, "x2": 6.2}},
     "drop": ["@fade1-anchor"],
     "add":  [{"type": "image", "name": "!!photo", "path": "assets/01_catru_trio_clean.jpg",
               "x": 8.4, "y": 2.2, "w": 4.2, "h": 3.1, "fit": "cover", "alpha": 0.45}]}
  ]
}
```
- Units are inches on a 13.333 × 7.5 canvas. Colours are `#RRGGBB` or palette keys; fonts are keys in `fonts` or family names.
- Shape types: `image` (fit cover/contain/stretch, focus, alpha), `text` (paragraph list, runs, size, bold, italic,
  align, anchor, spacing, line, caps, alpha), `rect` / `ellipse` (fill + alpha, `gradient` stops `[colour, alpha, pos%]`
  + `angle`, outline, radius), `line` (x1, y1, x2, y2, colour, width, alpha). Every shape accepts `rot`.
- **Keyframes**: `"from": "prev"` (or a slide `id`) copies the shapes; `set` changes keys by name, `drop` removes,
  `add` appends, `front` reorders. Unknown names in `set`/`drop` are errors, which catches typos in `!!` names.
- `fit: cover` crops instead of stretching (a stretched photo was a real defect in the ca trù deck).
- Notes go in `"notes"`; positions = file numbers in a freshly built deck, so `motion.json` keys = slide numbers.
- Text boxes have zero insets and no autofit: size the box for the longest line, and check the render.
  Vietnamese words are short, so line breaks are rarely a problem, but monospace headings in narrow boxes are.
- Off-slide parking: give a shape x ≥ 13.6 or y ≤ -2 so it can fly in on the next keyframe.
- Greyscale for a muted state: use a pre-made `_mono` copy of the image with the same `!!` name (it cross-fades), or
  add `<a:grayscl/>` inside the picture's `a:blip` with a small XML edit after unpacking.

Build loop for one group:
```bash
python $S/build_deck.py WORK/deck.json --out WORK/deck/build.pptx
rm -rf WORK/deck/unpacked && python $S/ooxml.py unpack WORK/deck/build.pptx WORK/deck/unpacked
python $S/motion.py WORK/deck/unpacked
python $S/ooxml.py pack WORK/deck/unpacked WORK/deck/preview-g2.pptx
python $S/check_deck.py WORK/deck/preview-g2.pptx --anchor "…"
bash $S/render.sh WORK/deck/preview-g2.pptx WORK/renders/g2-1
```
Rebuilding the whole deck each time is fine for 50 slides (a few seconds). Write each group's slides into the
same deck.json, so earlier groups stay as they are.

## B. Editing an existing or template deck (OOXML)
Use this when the user gives a template, when you build a family deck with another tool (pptxgenjs,
Anthropic's pptx skill, a managed slide service), or for effects the JSON spec lacks.
```bash
python $S/ooxml.py ensure-notes deck.pptx                    # every slide gets a notes page
python $S/ooxml.py unpack deck.pptx WORK/deck/unpacked
python $S/ooxml.py inventory WORK/deck/unpacked              # shape ids, names, kinds, x/y/w/h (in), text
python $S/ooxml.py sequence WORK/deck/unpacked slide1.xml slide1.xml slide1.xml slide2.xml   # duplicate = keyframes
python $S/ooxml.py order WORK/deck/unpacked                  # position → file (+ !! layers)
python $S/ooxml.py notes-set WORK/deck/unpacked WORK/notes.md   # '##### N' blocks by POSITION
python $S/ooxml.py clean WORK/deck/unpacked                  # drop unused slides + orphan media
```
- Rename shapes to `!!name` / `@fade1-x` in the slide XML (`p:cNvPr name="…"`); positions are EMU (914400 per inch).
- Edit with a small Python + lxml script per group (keep it in `WORK/notes/gN_edit.py`, so it can be re-run).
- `roles.py` builds three-column highlight-walk keyframes (groups `!!role1-3` + `!!hl`) on such a deck.
- After any edit: `motion.py` again (idempotent), then pack and check.

## C. Gotchas seen in real decks
| Symptom | Cause / fix |
|---|---|
| PowerPoint "repair" dialog | invalid child order (e.g. `a:spcBef` after `a:buNone` in `a:pPr`); keep the schema order. `pack` only checks well-formedness, so open the deck in PowerPoint or validate with the Open XML SDK if available |
| Chart shows old numbers in PowerPoint | the chart's embedded workbook (`ppt/embeddings/*.xlsx`) was not updated together with the chart XML cache |
| Morph does nothing | names differ (typo, trailing space), kinds differ, or two transitions (run `motion.py` and `check_deck.py`) |
| Durations reset to 1300 | motion.json not found (motion.py prints which config it used) or `--dur` given once only |
| Entrance plays before the Morph ends | normal: entrances start 350–500 ms after the slide starts; raise `stagger_ms` or the order numbers |
| Hand-made animation vanished | `motion.py` rebuilds `p:timing`; add the slide file to `keep_timing` |
| Photo looks stretched | picture box ratio ≠ image ratio; use `fit: cover` or set `a:srcRect` |
| Deck is 100 MB | duplicate media from copied slides; `finish_dedupe.py` (the ca trù deck went from 104 MB to 15.8 MB) |
| Hidden slide missing from the render | LibreOffice skips hidden slides; unhide to check them |

## D. Alternatives (optional, not required)
- **pptxgenjs** (Node) or **Anthropic's pptx skill** (Claude Code: html2pptx workflow) for a family deck; then path B.
- A managed slide service in your harness: fine for the family deck; keep this skill's gates, motion.py and checks.
Whatever the engine, the outputs must pass `check_deck.py` and the gates.
