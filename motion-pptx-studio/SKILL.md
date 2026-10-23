---
name: motion-pptx-studio
description: Designed, cinematic PowerPoint decks whose core is signature ManimGX films and Anatomy isometric machine films with editable native fallbacks, real sourced numbers, credited real images, native classic keyframe animation on every component (no Morph required) and a timed speaker script. Use for any presentation, slide deck or .pptx that must look designed rather than templated ("slide động", "thuyết trình chuyên nghiệp", pitch, data story, explainer).
---
# Motion PPTX Studio 6.22.0
Principles first, tools second. **At each step, open and read every file named in its [brackets]** before you decide:
they hold the numbers and tests this page leaves out. End NOTES.md with "Principles used" (principles-used).
Needs python3, python-pptx, Pillow, LibreOffice + poppler, ffmpeg, **ManimGX** and **Anatomy (Node 20.10+, Chrome)**: both mandatory.

**Step 0: before anything else, install and smoke-test ManimGX** (principles/manimgx-first.md) **and Anatomy**
(principles/anatomy-first.md: `bash scripts/setup_anatomy.sh`, then the smoke.mjs film). If either cannot run,
stop and tell the user; only then go to web-film (ChatGPT web, locked sandboxes). Never skip or fall back silently.

## Workflow
1. **Facts** - research/facts.md, one id per number, source + date. [never-invent-numbers]
2. **Concept + story** - one sentence, a SIGNATURE DEVICE, design/style.json (LOCKED palette 4-7 + treatment); design/story.md: the
   through-line, the arc, one PURPOSE line per slide; table chapter -> numbers -> instrument -> film. [concept-art-direction, through-line, one-concept, stagecraft, unity]
2b. **Photo library first** - 12-15 credited real photos/chapter, hero >= 1600 px; no photo of the product -> real comparables + lit renders; concept -> physical thing, boards, 4+ different subjects, hero/detail/wide/sequence picks (`scripts/photo_library.py`); slides are written FROM it. [photo-library-first]
3. **Art direction** - THREE radically different directions (A deliberately extreme) on one board, cliché rejected, one picked with a reason;
   then palettes, one MATERIAL per chapter (`scripts/surface.py`), visible at 1x; directions differ in COMPOSITION. Each chapter:
   a bold full-bleed or dark dramatic slide; no small icon in an empty field. [art-analysis, three-directions,
   art-direction, surface-and-depth, composition-range, one-type-scale]
3b. **Hero plan** - design/hero-plan.md: every slide's visual + library source; chapter heroes; explain with photo/object/3-D/film, not cream diagrams layout per slide, none > 3x, a strong slide every 4 (`photo_library.py plan`). [hero-plan, layout-rhythm]
4. **Storyboard** - ~1 slide/min: opener, per chapter (opener, FILM, a NEW composition, evidence), close,
   sources; every hero number is drawn as its object [data-as-object]. Each photo gets an ARRANGEMENT (full-bleed, cut-out, bleed crop,
   pair, sequence, mask) from its job: `scripts/photo_layout.py analyze|crop|cutout|mask`. Real credited photographs
   on most chapters, even for abstract topics. [photo-arrangement, photo-treatment, abstract-illustration, credit-every-image]
5. **Films (mandatory)** - ManimGX (`scripts/manim_kit.py` + `manimgx render`), plus at least one Anatomy film
   (`scripts/anatomy_film.py`) when the topic has any structure or process. Not installable: `scripts/web_film.mjs`,
   then canvas_film.py or native keyframes, the tier reported to the user and in NOTES.md. [manimgx-first, anatomy-first, web-film]
   2+ camera moves (one 3-D) over a running process; Anatomy hero shot >= 50 % with a flowing medium [film-language].
   Lit, textured, real-shaped, deep camera [cinematic-manimgx]; `film_check.py` + `film_art.py FILM.mp4` (fails toy renders) + strip.
6. **Build** - write make_deck.py that emits deck.json (references/deck-json.md), then
   `python3 scripts/build.py deck.json --out deck/NAME.pptx` (pptx + motion + renders/rN/contact-*.jpg +
   film + art + anim gates). A failed gate renames the deck NAME.UNFINISHED.pptx: fix it, never deliver it.
   Motion = films + a classic keyframe per component (entrance/path/emphasis/exit in purpose order); Morph never required (compat "safe"). [native-keyframes, vary-motion, techniques]
7. **Persistent art-director critic, <= 3 loops (mandatory)** - `scripts/critic.sh --slides renders/rN critique-1.md`, then
   `... renders/rM critique-K.md renders/rN critique-(K-1).md`: one director, DECK score, <= 5 library-tied orders, DONE marks; keep the better render, stop if gain < 0.5. [per-slide-critic, look-then-fix]
8. **Script + preview** - notes per slide (`scripts/ooxml.py notes-set`), Vietnamese per natural-vietnamese; optional
   preview on a COPY: `scripts/preview_motion.py DECK --out X-SIMULATION.mp4 --lang vi`.
9. **Deliver** - embed the static font files (`scripts/embed_fonts.py`; else name the fallback); the .pptx with the mp4 films embedded, the mp4s alongside it, contact sheets, script, and NOTES.md
   with "Principles used", the critic's and your scores. Never deliver a PDF only.

## Principles (principles/*.md)
| principle | one line |
|---|---|
| one-concept, never-invent-numbers, no-ai-cliche | one visual world; each chapter one number -> one instrument; every number sourced, derived ones say how; no starfields, glow, stock icons, stat cards |
| manimgx-first, anatomy-first | install + smoke-test both at step 0 (3 routes each); Anatomy for any structure/process; stop and report if impossible |
| film-is-the-core, web-film | 3-6 moving films in the pptx; web-film (HTML -> mp4) and lower tiers only when reported |
| three-directions, art-direction, art-analysis | 3 radically different directions, cliché rejected; chapter palettes, a visual per hero number, motif, board; study references for WHY/HOW on annotated boards, never copy; temperature, value, accent, scale |
| surface-and-depth, fit-style-to-subject, examples-are-a-yardstick-not-a-mold | every slide a made object: one material per chapter, light falloff, grain, textured panels; palette/type from the subject's objects; match examples' care, never their looks |
| film-language, composition-range, data-as-object | 3-D camera move over a running process; 5-7 named compositions, no 3 in a row, art density at 1x; numbers drawn as their thing; default charts and text lists <= 1 per chapter; no reused pictures |
| photo-library-first, sample-chapters, stagecraft | photo library/chapter (4+ subjects) before slides; 3 sample chapters, critic picks, style.md binds; 3-second glance test, one number per slide, picture shows the claim, sparkline swings, area = priority |
| hero-plan, abstract-illustration, per-slide-critic | per-slide visual plan from the library before code; abstract hero = metaphor photo, >=250 pt poster on photo or lit 3-D still; <=1 app screen; persistent critic, <= 5 orders/loop, keep-better |
| concept-art-direction, through-line, unity | signature device + treatment before looks; story.md + purpose per slide; one image treatment |
| native-keyframes, techniques | films + classic keyframes per component; Morph optional only; references/techniques.md |
| photo-arrangement, photo-treatment | photo first, type fits it: arrangement by job, bleed, scale contrast; grade, grain, material edge |
| one-type-scale, vary-motion | ratio scale, 200-400 pt heroes, no fixed title strip; 5+ transitions, effects with reasons |
| look-then-fix, principles-used, natural-vietnamese, credit-every-image | scored contact sheets + redo under 8; closing list; decimal comma, 160-190 syll/min; credited open images |
## Helpers (scripts/)
build.py, build_deck.py (+typeset, motion, motionlib, compat, ooxml), render.sh, contact_sheet.py, film_check.py, manim_kit.py, canvas_film.py, anatomy_film.py (+anatomy/, setup_anatomy.sh), web_film.mjs (+web/smoke.html), surface.py (grounds + photo grade), photo_layout.py, photo_library.py, art_check.py, anim_check.py, film_art.py, style_check.py, pptx_fx.py (text fill, masks, parallax), critic.sh (--pick, --slides), embed_fonts.py, preview_motion.py, fetch_commons.py. No house style. Yardsticks, not templates: examples/yardsticks (critic), reference-trai-dat, space-buu-dien-anh-sang-v2, flagship-khi-ap. Refs: references/. 