# native-keyframes
Morph plays only in PowerPoint 365/2019+; the deck must move the same in PowerPoint 2010-2016 and LibreOffice.
- **Films carry the cinema:** embedded ManimGX/Anatomy mp4s (autoplay, loop, muted) are the hero motion.
- **Every component gets its own classic keyframe animation**: entrance, motion path, emphasis or exit, timed in
  a sequence that tells the slide's purpose (photo settles -> number rises -> caption fades). Names `@fade1-`,
  `@fly2b-`, `@zoom3-`... or motion.json "effects" with paths, delays and "with" (motion.py, motionlib.py).
- **Default compat is "safe"**: no Morph; any authored Morph is rebuilt as classic paths/zooms. "dual" (Morph for
  365 + classic fallback) is an optional enhancement; never a hero moment that depends on Morph.
- One idea per motion: move toward the point, never decorate; 300-900 ms entrances, 4-10 s slow drifts.
- Gate: `scripts/anim_check.py DECK.pptx --deck deck.json` (build.py runs it): >= 70 % of components animated on
  all but a few slides, no Morph without classic effects, a purpose on every slide.
