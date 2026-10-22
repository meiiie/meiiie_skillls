# film-is-the-core
A deck without signature films fails this skill, however good its text slides are.
- **Plan 3-6 films**, one per main chapter, each 10-20 s, at 1920x810 (64:27) to fill the
  full-width film window.
- **ManimGX is mandatory.** Install it and smoke-test it first (manimgx-first). Write the films
  with scripts/manim_kit.py: slide-point type, a 2-D camera, pins.
- **Anatomy is mandatory too** whenever the topic has any structure or process (architecture,
  system, machine, pipeline, cycle): at least one film from scripts/anatomy_film.py (anatomy-first).
  It also gives an editable shapes.json.
- **Only if ManimGX or Anatomy cannot run AND the user has been told:**
  - scripts/canvas_film.py (pure Python + Pillow + ffmpeg);
  - else native motion paths with Morph across 2-3 slides.
  - Write the reason in NOTES.md.
- **A film must MOVE:** a camera that pushes, tracks or pulls, and parts that travel. Run
  `film_check.py FILM` after every render.
- **Every film gets an editable native slide of its end state.** Use the same geometry module
  with two renderers.
- **Look at a contact strip of each film (5+ frames)** before it goes on a slide. Fix collisions,
  empty halves and tiny type.
- **The deliverable is a .pptx with the mp4 films embedded,** plus the mp4s alongside it. Never
  deliver a PDF only. A PDF is at most an extra handout.
