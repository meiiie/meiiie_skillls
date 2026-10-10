# Build engine (Phase 5)

Two ways to build, both ending in the same `ooxml.py` + `motion.py` + `check_deck.py` pipeline, which
`studio.py build` runs in one command.

## A. Default: `deck.json` → `build_deck.py` (works everywhere)

### A.1 The loop
```bash
python $S/studio.py new WORK --kind product --style noir-product --title "…" --fonts   # once
# edit WORK/deck.json (or a make_deck.py that writes it), then:
python $S/studio.py build WORK --group g1        # build → motion → pack → render → audit; new renders/g1-N each time
python $S/studio.py compare WORK WORK/renders/g1-1
```
`build` prints the layout warnings (text that does not fit, a single word on a last line, text
outside the safe area, texts that overlap, text running over a card), the audit (ERROR/WARN) and
the contact sheets to open. Fix the warnings before you look: they are what you would see.

### A.2 The spec
```json
{
  "style": "design/style.json",
  "title": "Diều",
  "motion": {"default_ms": 1100},
  "slides": [
    {"id": "type", "scene": "S1", "ms": 1400, "notes": "Cuộc họp vừa kết thúc. [ngừng]",
     "shapes": [
       {"type": "rect", "name": "!!cursor", "x": 8.32, "y": 3.42, "w": 0.22, "h": 0.5, "fill": "accent"},
       {"type": "text", "name": "!!line", "role": "title", "text": "Cuộc họp vừa kết thúc.", "x": 1.0, "y": 3.3, "w": 7.2, "h": 0.75, "align": "r"}]},
    {"id": "panel", "scene": "S1", "ms": 1600,
     "shapes": [
       {"type": "rect", "name": "!!cursor", "x": 6.55, "y": 1.45, "w": 5.9, "h": 3.85, "fill": "surface", "line_color": "accent", "radius": 0.04},
       {"type": "heading", "name": "!!h", "col": [1, 5], "y": 1.6, "kicker": "47 phút", "title": "Ai đang giữ biên bản?"}]},
    {"from": "prev", "id": "panel2", "set": {"!!h": {"title": "Không ai cả."}}}
  ]
}
```
Units are inches on 13.333 × 7.5. Colours are palette roles or `#RRGGBB`; fonts are `display`, `text`,
`label` or family names. The full key list is in the docstring of `build_deck.py` (`-h`). In short:

| Level | Keys |
|---|---|
| deck | `style`, `title`, `palette`, `fonts`, `type`, `grid`, `grounds`, `bg`, `chrome` / `chrome_add`, `card`, `screen`, `shadow`, `motion` |
| slide | `id`, `from` + `set` / `drop` / `add` / `front`, `bg` (ground name, palette key, `#hex`, `{"image": path}`), `scene`, `chrome` (true/false/[names]), `chrome_set`, `source`, `ms`, `morph`, `keep_timing`, `notes` |
| any shape | `type`, `name`, `x`, `y`, `w`, `h` or `col: [start, span]`, `rot`, `alpha`, `hidden`, `shadow` (true or {blur, dist, dir, color, alpha}) |
| text | `text` (string or paragraphs with their own keys or `runs`), `role`, `font`, `size`, `bold`, `italic`, `color`, `align`, `anchor`, `spacing`, `line`, `caps`, `fade` + `fade_bg`, `bleed` |
| image | `path`, `fit` cover/contain/stretch, `focus`, `radius`, `line_color`, `line_width`, `grayscale`, `duotone`, `brightness`, `contrast` |
| rect / ellipse | `fill`, `alpha`, `gradient` + `angle`, `line_color`, `line_width`, `line_alpha`, `radius`, `geom` (CHEVRON, TRIANGLE, …) |
| line | `x1`, `y1`, `x2`, `y2`, `color`, `width`, `alpha`, `cap`, `dash` |
| group | `shapes` |

### A.3 Components
| Component | Keys | Parts (Morph names) |
|---|---|---|
| `heading` | kicker, title, sub, body, title_role, align, `<part>_style` | NAME.kick/.title/.sub/.body, stacked by measured height |
| `card` | title, kicker, desc, image or icon (+ image_h/icon_h), state rest/lit/dim, pad | a group NAME with "NAME bg/rule/title/kicker/desc/icon" |
| `stat` | value, unit, label, src, size, color, label_color | NAME.value/.unit/.label/.src; the unit shrinks to fit beside the value |
| `screen` | image, device browser/phone/plain, url, focus, shadow | a group NAME (bezel, bar, dots, url, image, notch) |
| `timeline` | nodes [{t, label, desc}], active, label_w, color | NAME.rail/.prog/.dot{i}/.t{i}/.l{i}/.d{i}; first label left, last right |
| `bars` | data [{label, value, display}], max, grow 0..1, highlight, gap, color | NAME.base/.bar{i}/.v{i}/.k{i}; values appear when grow = 1 |
| `list` | items [str or {text, sub}], reveal, focus, numbered, size, rules | NAME.n{i}/.i{i}/.r{i} |
| `quote` | text, by, size, mark_color | NAME.mark (hanging in the margin)/.text/.by |
In a keyframe, `set` the component (`{"!!b": {"grow": 1}}`), not its parts.

### A.4 Generate deck.json from a script when geometry depends on geometry
When parts must line up (strings locked to an instrument's neck, a cursor that becomes a panel the
size of the screen), write a small `make_deck.py` that computes the boxes and writes `deck.json`, as the
three examples do. Change one number (where the instrument stands) and every keyframe follows.

### A.5 Notes on the output
- Text boxes have zero insets and no autofit; components size their boxes from the real font
  (`typeset.py`), so install the fonts first (`studio.py fonts`).
- Quiet text uses `fade` (a solid colour mixed toward its background), not transparency: LibreOffice
  misplaces Vietnamese marks on transparent text.
- Grounds named in the style are generated once into `WORK/assets/grounds/` and placed as slide
  backgrounds (not shapes), cropped to 16:9.
- Scene ids go into the slide name (`p:cSld/@name`), where the audits read them.
- Notes go in `"notes"`; positions = file numbers in a freshly built deck.

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
| Durations reset | motion.json not found (motion.py prints which config it used); put `ms` on the slides in deck.json |
| Entrance plays before the Morph ends | normal: entrances start 350–500 ms after the slide starts; raise `stagger_ms` or the order numbers |
| Hand-made animation vanished | `motion.py` rebuilds `p:timing`; `"keep_timing": true` on the slide |
| Photo looks stretched | picture box ratio ≠ image ratio; use `fit: cover` or set `a:srcRect` |
| Vietnamese marks drift in the render | transparent text in LibreOffice; use `fade` instead of `alpha` on text |
| Render shows the wrong font | the font is not installed where you render (`studio.py fonts`, `fc-list`) |
| Deck is 100 MB | duplicate media from copied slides; `finish_dedupe.py` (the ca trù deck went from 104 MB to 15.8 MB) |
| Hidden slide missing from the render | LibreOffice skips hidden slides; unhide to check them |

## D. Alternatives (optional, not required)
- **pptxgenjs** (Node) or **Anthropic's pptx skill** (html2pptx) for a family deck; then path B. The reference
  deck was built this way: ~11 designed slides, sequenced into 48 keyframes.
- A managed slide service in your harness: fine for the family deck; keep this skill's gates, motion.py and checks.
Whatever the engine, the outputs must pass `check_deck.py` and the gates.
