---
name: motion-pptx-studio
description: Designed, cinematic PowerPoint decks whose core is signature films (Manim, pure-Python canvas or Anatomy isometric machines) with editable native fallbacks, real sourced numbers, credited real images, native Morph/transition motion and a timed speaker script. Use for any presentation, slide deck or .pptx that must look designed rather than templated ("slide động", "thuyết trình chuyên nghiệp", pitch, data story, explainer).
---
# Motion PPTX Studio 6.0

Principles first, tools second. Read the principle files you use (10-20 lines each) and, at the end,
name in NOTES.md which principle shaped which decision (principles/principles-used.md). Needs python3,
python-pptx, Pillow, LibreOffice + poppler for renders; ffmpeg for films; ManimGX / Node+Chrome optional.

## Workflow (one pass, then loops only where it looks wrong)
1. **Facts** - research/facts.md, one id per number, source + date. [never-invent-numbers]
2. **Concept** - one sentence, then a table chapter -> numbers -> instrument -> film. [one-concept]
3. **Art direction** - chapter palettes, background per slide, type pairing, one motif, a board PNG
   critiqued against a reference. ds.py tokens. [art-direction, fit-style-to-subject, one-type-scale]
4. **Storyboard** - ~1 slide/min: opener, per chapter (opener, FILM, a NEW composition, evidence), close,
   sources; every hero number gets its visual. Mark where each film and each real image goes. [no-ai-cliche, credit-every-image]
5. **Films (mandatory)** - pick the route in film-is-the-core: Manim (`scripts/manim_kit.py`) -> else
   `scripts/canvas_film.py` -> Anatomy (`scripts/anatomy_film.py`) for machines -> else native motion paths.
   After each render: `python3 scripts/film_check.py FILM.mp4` and look at a 5-frame strip. Fix, re-render.
6. **Build** - write make_deck.py that emits deck.json (references/deck-json.md), then
   `python3 scripts/build.py deck.json --out deck/NAME.pptx` (pptx + motion + renders/rN/contact-*.jpg +
   film check of every video in the deck; it FAILS under 2 films). [vary-motion]
7. **Look and fix** - open every contact sheet tile; score in critique-log.md; redo what is under 8. [look-then-fix]
8. **Script + preview** - notes per slide (`scripts/ooxml.py notes-set`), Vietnamese per natural-vietnamese;
   optional labelled preview: `python3 scripts/preview_motion.py DECK --out X-SIMULATION.mp4 --lang vi`
   (run it on a COPY of the deck).
9. **Deliver** - pptx, contact sheets, films, script, NOTES.md with "Principles used" and honest scores.

## Principles (principles/*.md)
| principle | one line |
|---|---|
| one-concept | one visual world; each chapter one number -> one instrument |
| film-is-the-core | 3-6 moving films, a route for every harness, never skipped silently |
| never-invent-numbers | every number has a fact id and a source; derived ones say how |
| no-ai-cliche | no starfields, glow, stock icons, repeated stat cards; real evidence |
| art-direction | palette per chapter, a background on every slide, a visual per hero number, type pairing, motif, board |
| examples-are-a-yardstick-not-a-mold | match the examples' care, never their palettes, fonts or layouts |
| fit-style-to-subject | palette and type from the subject's own objects, one job per colour |
| one-type-scale | 7 sizes, one grid, fixed chrome; nothing overlaps |
| vary-motion | Morph as camera, 5+ transitions, 10+ effects, each for a reason |
| look-then-fix | contact strips and sheets, scores, one redo loop under 8 |
| natural-vietnamese | decimal comma, finding-titles, 160-190 syllables/min |
| credit-every-image | open licences, verified subject, credit on the slide |
| principles-used | the closing "principle -> decision -> where" list |

## Helpers (scripts/)
build.py, build_deck.py (+typeset, motion, motionlib, compat, ooxml), render.sh, contact_sheet.py,
film_check.py, manim_kit.py, canvas_film.py, anatomy_film.py (+anatomy/, setup_anatomy.sh),
preview_motion.py, fetch_commons.py. No house style: palette and fonts come from each deck's ds.py.
Yardsticks (not templates): examples/reference-trai-dat, examples/space-buu-dien-anh-sang-v2,
examples/flagship-khi-ap. References: references/deck-json.md, references/manimgx-quirks.md.
