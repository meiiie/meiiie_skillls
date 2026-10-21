# heritage-collage — magazine pages cut from paper and photographs

Measured from a heritage magazine-style student deck (Hội quán Ôn Lăng, 13 pages; reference images are not
shipped: third-party) and the public critique of it. The pack keeps what made that deck read as a
designed magazine and fixes what the critique pointed at.

**Use for** heritage and architecture, museums and collections, travel, school and research reports,
and product anatomy (an object read part by part).
**Palette** aged paper `#EEDFBE` (stains and fibres, `make_assets` `paper` with `stains`), a terracotta
gradient `#5E2210 → #D98A3D` for chapter openers (`gradient`), dark ember `#22150E`; ink `#2A1D15`;
accents **red `#962018`** and **burnt orange `#9C4409`**, sun `#F0B43C` only on dark grounds.
**Fonts** Anton (display, caps) · Be Vietnam Pro (text) · Barlow Condensed (labels, callouts) ·
Dancing Script (`script`, the handwritten accent line). All OFL, all with Vietnamese.

## Layout grammar
- **Two page kinds, alternating.** Dense pages (grid of 5–9 photos, a cut-out with 3–5 callouts, a map)
  and **airy chapter openers** (one numeral, one caps title, one script line, 20 words at most). Never
  three dense pages in a row; a 20-slide deck has 3–4 openers.
- **Titles**: heavy caps, 1–2 accent colours *inside* the title as runs
  (`{"runs": [{"text": "Toạ độ "}, {"text": "của tàu", "color": "accent"}]}`), never a third colour.
- **Script accent line**: `role: "script"` (rotated −4°, may cross the title: `overlay`), one per page, ≤ 6 words.
- **Object cut-outs** float on the paper with the pack shadow (`cutout.py`, then `"type": "image"` with
  `"shadow": true`); the object is the picture, the page shows around it.
- **Callouts** point at parts: `{"type": "callout", "at": [x, y], "x": .., "y": .., "label": "NGÓI", "desc": ".."}`
  = a dot on the part, a hairline leader, the label on a colour chip; `"elbow": true` for a right-angle leader.
- **Photo grids**: `{"type": "photogrid", "images": [{"path", "span": [2, 2], "label"}...], "cols", "rows", "tilt": [..]}`
  = bordered prints with a shadow; every label sits on a chip.
- **Palette strip**: `{"type": "swatch", "image": "<photo or cut-out>", "n": 4..5}` samples the photo
  (a cut-out samples the object only; `"vivid": true` favours saturated colours); hex codes sit inside the chips.
- **Maps**: `{"type": "nodemap", "nodes": [{"x", "y", "label", "desc", "side"}], "links": [[a, b]], "image": optional}`
  = red nodes, connecting lines, labels on dark chips; a faint card or a toned map photo under it.

## Legibility rules (from the critique; checked)
- **Text on a photo always sits on something**: a chip, a colour band, a gradient scrim
  (`"gradient": [["veil", 0, 0], ["veil", 0.85, 100]], "angle": 90`) or a toned photo (`brightness` < 0).
  `legibility_audit.py` finds bare text on photos; with this pack the gates FAIL it (other packs WARN).
- **Caps only for headlines, kickers and labels**: a paragraph of 12+ words in capitals is an ERROR in
  `check_deck.py` for every pack. Body text is sentence case.
- Red on paper is for titles and kickers at 13 pt and up; small red text needs the darker `accent`.

## Signature motion
- Callouts `wipe` out from the dot, 400–500 ms apart, after the object `zoom`s in.
- Grid prints `zoom` in with 70 ms stagger; the big print first.
- Swatch chips `rise` one by one; map nodes `fade` in along the route, then the lines.
- A print on the opener `float`s (loop); a full-bleed photo drifts on a short `path` under its scrim.
- Transitions: `fade` into openers, `push` between dense pages, `wipe` onto a map.

## Avoid
Body paragraphs in caps; text straight on a busy photo; more than two accent colours; a script line
longer than a phrase; dense page after dense page; collage shapes (torn paper, tape) that hide the photos.
See `examples` in the v5.4 CHANGELOG for the sample deck (SpaceX "Con người lên tàu", 7 slides).
