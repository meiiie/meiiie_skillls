# Pro craft: variety, composition and flavour (v5.2)

Why this file exists: the cà phê phin sample (v5.1) was judged "better, but not truly professional". The four
gaps were too little **animation variety**, weak **art direction and composition**, too little **flavour**, and
too little **overall variety**. This file holds the rules that close those gaps. `scripts/variety_audit.py` measures
them, and `check_deck.py --variety warn|strict` runs it on every build. The worked example is the Earth deck
(`examples/earth-fall/`, 22 slides, four sub-styles).

Sources (read Oct 2026):
- [S1] Kurzgesagt, "Our video process": https://kurzgesagt.org/what-we-do?visit=videos
  and "How to Make a Kurzgesagt Video in 1200 Hours": https://www.youtube.com/watch?v=uFk0mgljtns
- [S2] Eames Office, *Powers of Ten* (1977): https://www.eamesoffice.com/the-work/powers-of-ten/
- [S3] Duarte, "Using contrast to craft persuasive presentations": https://www.duarte.com/blog/ultimate-guide-to-contrast/
  and *slide:ology* ch. 6, "Arranging Elements": https://www.oreilly.com/library/view/slide-ology/9780596522346/chapter-11.html
- [S4] Microsoft Fluent 2, Motion (duration, easing, choreography, stagger, hierarchy): https://fluent2.microsoft.design/motion
- [S5] Microsoft Learn, "Timing and easing" (enter fast-out/slow-in, exit slow-out/fast-in; 167/250/333 ms):
  https://learn.microsoft.com/en-us/windows/apps/design/motion/timing-and-easing
- [S6] BrightCarbon, "Parallax scrolling effect in PowerPoint" (layers moving different distances in the same time):
  https://www.brightcarbon.com/blog/create-parallax-scrolling-effect-powerpoint/
- [S7] CreativePro (M. Parkinson), "Timelines with parallax effects" (Morph plus a background that moves less):
  https://creativepro.com/how-to-create-timelines-with-parallax-effects-in-powerpoint/
- [S8] Microsoft Support, "Morph transition: tips and tricks" (`!!` names; charts cross-fade; edit-point rules):
  https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks
- [S9] NASA Images and Media Usage Guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/

## 1. The four gaps as testable rules

| Gap | Rule | Measured by |
|---|---|---|
| Animation variety | ≥ 10 distinct effect techniques in a deck of 15+ slides; no single technique > 35% of effect nodes | `variety_audit` techniques and top share |
| Transition variety | ≥ 5 transition types; Morph only where a shape truly travels | `variety_audit` transition types |
| Composition | ≥ 60% distinct composition signatures across scene cuts; never 3 equal signatures in a row | `variety_audit` composition |
| Depth | ≥ 20% of slides have plate + moving layer + text (three planes); parallax on at least a couple | `variety_audit` moving depth |
| Flavour | 3–4 sub-styles inside one family, each with its own ground, type voice and motion verb | art-direction.md, contact sheet review |

## 2. Motion vocabulary per scene

Kurzgesagt sketch "transitions between ideas" before illustrating, and they move every part by hand [S1]. A pro deck
gives **each scene its own motion verb** and keeps it consistent within the scene. Variety then comes from the cut
between scenes, not from noise inside one slide.

| Scene mood | Verb | Techniques (motionlib) | Easing / time [S4][S5] |
|---|---|---|---|
| Vast, quiet (space) | drift | `path` loop, slow `zoom`, `fade` 900–1400 ms | linear only for orbit and rotation |
| Measured, documentary (atlas) | draw | `wipe` from the axis, `grow` bars, `type` kicker | fast-out/slow-in, 250–500 ms |
| Violent (inferno) | erupt | `rise`, `split`, `pulse` glow, `spin` arrows | short, staggered, with a big hierarchy gap |
| Contemplative (deep time) | tick | `wheel` (clock sweep), `appear` on beat, `word` | uniform beat, 1 event per second |
| Close / echo | return | the opening's exact motion, reversed | mirror of slide 1 |

Rules:
- **Stagger** sets, never animate a group at once (except very large sets) [S4]. Use `step` 30–120 ms.
- **Hierarchy**: the lead element moves longest and furthest; supporting text fades in sync [S4].
- **Loops** (`path` with `loop`, `spin` loop, `pulse`) give a slide life while the speaker talks. Use 1–2 per slide,
  slow, and never on text.
- **One technique ≤ 35%.** If `fade` dominates, swap supporting fades for `wipe` along the reading direction, `type`
  for kickers, `word` for quotes, and `appear` on the beat.

## 3. Cut grammar (which transition, when)

| Cut | Transition | Why |
|---|---|---|
| Same object, new scale or place (Powers of Ten step) | Morph with shared `!!` names [S8] | continuity of one object [S2] |
| Change of scene or world | push / cover / uncover in the travel direction | spatial logic: the fall goes down, time goes right |
| Reveal under a surface (crust → mantle) | split out, wipe down, reveal | the motion says "open up" |
| Big tonal break | fade through black, dissolve | breath, before an emotional beat |
| Climax (one per deck) | flythrough / vortex / ripple | spent once, it lands; spent often, it is a template |

Use at least 5 types in a 15+ slide deck, Morph on ≤ 40% of cuts, and the "climax" transition only once.

## 4. Composition systems

Duarte: contrast makes the main point instantly identifiable, flow sets reading order, and whitespace isolates [S3].
Reusing one grammar ("big numeral top-left + photo right") on 3 slides in a row reads as a template even when the
pictures change. The Earth deck failed exactly this in round 1 (slides 5–7) and fixed it in round 2.

A slide composition is described by: media cover (full bleed / half / spot / none), side (left / right / centre),
plate (shape diagram or not), the lead-text cell (3×3 grid), and the text count. Rotate through at least six systems:

1. **Full-bleed + text on the image's quiet zone**: the numeral sits *on* the lunar surface, dark on light.
2. **Edge crop** (the subject bleeds off one side) + a vertical numeral (`rot: 270`) on the other edge.
3. **Centre object + orbiting labels**: the diagram is the slide.
4. **Strip chart**: one bar the full width, a giant numeral above it.
5. **Cross-section / quarter-disc in a corner**: the scale is implied by what is cut off.
6. **Instrument** (clock or gauge) with a list rail.
7. **Typographic poster**: one word, enormous, a photo through or beside it.
8. **Empty field + a tiny object** (Pale Blue Dot): negative space as content.

The signature object (the Earth deck's altitude/depth gauge) is what stays put. Everything else moves cell between
cuts.

## 5. Depth: three planes and parallax

Three planes per hero slide: a **plate** (photo or gradient ground), a **moving layer** (stars drifting, aurora
sway, convection arrows), and **text**. Parallax is two layers moving different distances in the same duration
[S6]. Across a Morph run, move the background less than the foreground [S7]. In motionlib, give the far layer a
`path` of 0.2 in and the near layer 0.8 in, with the same `ms`.

## 6. Flavour: sub-styles inside one family

Pick 3–4 sub-styles that share the type family and the signature object, but each has its own:
- ground (near-black blue / warm paper / ember / ink-navy),
- display voice (serif italic / grotesk / condensed heavy / mono),
- accent (one hot colour per sub-style),
- motion verb (§2).

Write the colour arc as a line in art-direction.md. Then check on the contact sheet that you can tell the scenes
apart at thumbnail size. Kurzgesagt's distinctiveness comes from drawing most images from scratch rather than from
a library [S1]: build diagrams from editable shapes and Manim, not icon packs.

## 7. Narrative device

A **scale journey** (Powers of Ten [S2]) gives every slide a coordinate (km above or below the surface) and makes
Morph meaningful: the same gauge marker travels. Other devices that work: a clock (deep time compressed into one
day), a single object followed through states, or a ring close that mirrors slide 1 word for word.

## 8. Imagery licence

NASA imagery is generally not copyrighted in the US and is usable for education with acknowledgement. It must not
imply endorsement, NASA insignia are protected, and third-party images on NASA sites keep their owner's copyright
[S9]. Record every kept file in CREDITS.md with its URL and licence.

## 9. Review ritual (harsh critique)

After every render, write a critique against the four gaps before you fix anything:
1. List repeated grammars (slide numbers).
2. List slides with < 3 planes.
3. List any technique over 35%.
4. Ask whether each scene has a nameable flavour.

Fix the worst, re-render, and log it in notes/gN.md.
