# Anti-template phase: three art directions (v5.3)

The pipeline used to pick one style pack and run it on every slide; the decks passed and looked the
same: one dark ground, title left, photo right, thirty times. The skill now asks for three genuinely
different directions **before** the storyboard, a choice with a reason, and (for 20+ slides) a
scene-level style shift.

## 1. Sketch three

Each direction differs on at least three of: ground (white paper / noir / cream editorial / full-bleed
photo), palette, type pairing, composition, motion idea, signature visual. Three colourways of one layout
are one direction. Fill `design/directions.json` and run:

```bash
python3 $S/directions.py WORK     # -> design/directions.jpg (3 thumbnails) + design/directions.md
```

Compositions the sketcher knows: `swiss-grid`, `hero-object`, `full-bleed`, `kinetic-number`,
`editorial`, `split`. Use the deck's real fonts and one real asset per thumbnail.

## 2. Choose and say why

`- chosen:` one direction (optionally a second for named chapters) and `- why:` in a sentence that names
what the subject asks for and what the other two get wrong. "Looks modern" is not a reason. Example:
"A (white workshop, #1464F4) for the industrial chapters because the subject is a factory and the
Anatomy machines read best on white; B (highway night) only for hook and close; C (audit paper) for
the money chapter because losses deserve a sober, printed look."

## 3. Scene-level style shifts

A deck of 20+ slides changes style at least once at scene level (`"style": "<pack or file>"` on the
first slide of the scene; it holds until changed). Shift at chapter boundaries, keep the fonts (chapter
packs inherit the deck fonts; at most one extra display face, four families in total), keep the
signature layers alive across the cut.

## 4. Geometry, not labels

check_deck now fingerprints each slide from what is drawn (picture boxes, text mass). Text left + photo
right on 4+ slides FAILS, whatever the layout column says. Compositions that break the habit:
full-bleed plate with text in a band, hero object centred with labels around it, kinetic number,
Swiss grid with a small inset, two-up comparison, map/diagram full width with a caption strip, film
across the slide with a stat rail under it.
