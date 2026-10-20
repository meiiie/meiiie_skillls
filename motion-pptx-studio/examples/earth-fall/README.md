# earth-fall: TRÁI ĐẤT · Rơi về nhà (v5.2 worked example)

This is a 22-slide Vietnamese deck of about 6 minutes, with compat `dual`. It answers the four "not pro yet" gaps
(see `references/pro-craft.md`).

- **Device**: a Powers-of-Ten fall from 6 billion km (Pale Blue Dot) down to the inner core, then a pivot into deep
  time (the 24-hour clock) and a ring close that mirrors slide 1 ("Đây là nhà.").
- **Signature**: the altitude/depth gauge on the right edge. Its marker morphs on every slide.
- **Sub-styles**:
  - cosmos: near-black, serif, drift
  - atlas: warm paper, editorial, draw/wipe
  - inferno: ember, condensed heavy, erupt
  - deeptime: ink-navy, mono, tick
- **Variety** (variety_audit):
  - 18 techniques, top entr:fade 28%
  - 11 transition types (Morph 8/22)
  - 12/14 composition signatures
  - moving depth on 13/22, parallax on 4
- **Films**: `manim/seasons.py` and `manim/plates.py` (ManimGX, 1920×1080, posters from the last frame).

Rebuild: put the files from CREDITS.md in `assets/`, then run `python3 make_deck.py && python3 make_docs.py &&
python3 ../../scripts/studio.py build . --group g1`. The photos (about 175 MB) are not shipped. Fetch them from the
URLs in CREDITS.md.
