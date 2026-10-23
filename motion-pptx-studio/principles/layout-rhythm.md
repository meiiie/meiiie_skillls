# layout-rhythm
R14: "a rectangular photo beside a text column" on 10+ slides flattened every deck into a template.
- Every slide in deck.json names its `"layout"`: full-bleed, detail-crop, type-on-photo, cutout-over-type, split,
  pair, sequence, mask, poster, film, object, chart, diagram, sources, title.
- **No layout more than 3 times** in a deck (sources/title excepted).
- **Rhythm:** every run of 4 slides contains a full-bleed, a detail-crop, a type-on-photo or a film; alternate wide
  and close, light and dark, big and quiet.
- **Data rhythm:** a chapter with figures (>= 3 quantities) gets >= 1 real chart (bars from zero, line, dot field,
  to scale) beside its big numerals; numerals alone never show a comparison (R16 lost to the reference here).
- Plan it in design/hero-plan.md (visual + layout per slide) before code.
- Gate: `scripts/style_check.py` (build.py) fails a layout used > 3 times, a 4-slide run without a strong slide,
  missing layout keys, or a figures chapter without a chart (CHART).
