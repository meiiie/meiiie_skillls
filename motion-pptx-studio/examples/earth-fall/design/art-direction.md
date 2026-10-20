# Art direction (Gate 3)
- style: four sub-styles written for this deck: design/styles/cosmos.json, atlas.json, inferno.json, deeptime.json (cloned from the blueprint pack; the pack itself is untouched)

## Concept: "TRÁI ĐẤT · Rơi về nhà"
One continuous fall, Powers-of-Ten style (Eames 1977): 6 billion km → 150 million km → 384,400 km → 29,400 km →
400 km → 100 km → 0 km → −2,900 km → −6,371 km, then a pivot from depth in space to depth in time (4.54 Ga as
one day) and a circular return to the dot. Every chapter is a new altitude band, and each band gets its own
material: photography in space, paper plates in the air and on the ground, ember posters underground, an
instrument dial for time.

## Style choice (no default template: one sub-style per altitude band, on purpose)
- chosen: cosmos (S1-S2 + close: true black, NASA photography, Fraunces hairline serif, micro mono captions, 90% empty)
- chosen: atlas (S3-S4: warm paper #EDE5D3, hand-built scientific plates numbered "Hình 2-5", ink hairlines, figure letters a-d)
- chosen: inferno (S5: ember-black ground, Anton condensed poster numerals, to-scale concentric cut-away, heat ramp)
- chosen: deeptime (S6: midnight navy, 24-hour instrument dial, JetBrains Mono tabular numerals, one lime hand)
- rejected: blueprint pack as-is (cyan grid reads "engineering", wrong for a planet; kept only as the JSON skeleton)
- rejected: lacquer-heritage (gold-on-lacquer belongs to Vietnamese heritage topics, would be costume here)
- rejected: one dark theme for everything (Darren's "too little flavour": four materials make the descent felt)

## Motion vocabulary (signature techniques beyond Morph: references/motion-library.md, references/pro-craft.md)
- camera: Morph push-in, crop-morph and zoom-into-detail (×2.6 dot, ×100 air strip, ×4.2 mantle, ×26 dial)
- parallax: three planes at different path lengths (stars far, Earth mid, Moon near) on the Earthrise slide
- living loops: ring pulse, ISS orbit path loop, droplets on curved looping paths, rain, convection spin, aurora sway, core glow
- kinetic type: letters for "Đây là nhà." and the Sagan quote, words for the limb line, 25° rotated type along the horizon
- choreographed sync: on the dial the eon bands, event dots and ledger rows land exactly when the spinning hand passes
- film: two Manim diagram films (seasons, plates) + one rendered globe loop
- cuts: 10 transition types, chosen by meaning (push up = rising Earth, wipe down = falling through the sky, split = cutting into the ground, reveal = opening the planet, dissolve = time)

## Signature (ONE object through the deck as !! layers)
- the altitude/depth gauge on the right edge (!!g-rail, !!g-surf, !!g-top, !!g-bot, !!g-dot, !!g-val): orange dot,
  log scale above the surface, linear below. It morphs on every slide; it is the hero on slide 3 (the route) and
  in the close, where the dot jumps back to "6 tỉ km".

## Fonts (OFL; fonts/ ships the static TTFs)
- display: Fraunces 300/400/700 + 400 italic (soft optical serif for the cosmos voice; full Vietnamese)
- poster: Anton 400 (inferno numerals; Vietnamese diacritics checked in renders)
- body: Be Vietnam Pro 400/500/700 (made for Vietnamese)
- label: JetBrains Mono 400/700 (instrument captions, tabular numerals)
- rejected: Bebas Neue (no Vietnamese marks), Inter (neutral, no flavour)

## Palette (each hex with its source)
- #05070B cosmos ground, sampled from the Pale Blue Dot black (pixel)
- #FF6A2B signature orange (gauge dot, ring), from style pack blueprint accent, warmed
- #8FD8FF cosmos kicker ice-blue, sampled from the limb photo upper band (photo)
- #EDE5D3 atlas paper, from style pack atlas / blueprint "paper" variant
- #A8380A atlas accent (darkened orange for 5:1 contrast on paper, measured)
- #2E6FA8 atlas ocean blue, sampled from the Blue Marble oceans (photo)
- #120605 inferno ground, sampled from the lava photo shadows (photo)
- #FFB23F inferno accent, sampled from the lava fountain highlights (photo)
- #0A1020 deeptime navy, style pack deeptime
- #C6FF4A deeptime lime hand, style pack deeptime (one instrument colour)

## Motifs and textures
- grounds: cosmos flat black; atlas paper grain + vignette; inferno noir lift; deeptime clean grid (make_assets grounds via build_deck)
- drawn: atmosphere plate, air strip, water-cycle diorama, cross-section, 24-hour dial, the dot (all editable shapes)

## Layered objects for Morph
- er_moon.png / er_earth.png cutouts from Earthrise (parallax), bm_disc.png circular cutout from Blue Marble
- pbd_wide.jpg (the dot's position known: 0.5945 W, 0.5 H) for the push-in and crop-morph

## Colour arc
- S1-S2 #05070B → S3-S4 #EDE5D3 → S5 #120605 → S6 #0A1020 → close #05070B (the fall goes black → paper → ember → navy → black)

## Samples rendered and compared
- renders/g1-1 … g1-8: see NOTES.md "Critique and iterations" for what each round changed
- design/compare-1.jpg (Earth g1-9 above the ca trù reference): the reference is one material (lacquer) held for 48
  slides; this deck changes material per altitude band, so the system has to come from the gauge, the folio and
  the mono captions. Changed after the comparison: kept the gauge on every slide (including the full-bleed films),
  gave atlas plates figure numbers and letters, and rebuilt the close to mirror slide 1 exactly.
