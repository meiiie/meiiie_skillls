# film-is-the-core
A deck without signature films fails this skill, however good its text slides are.
- **Plan 3-6 films**, one per main chapter, each 10-20 s. Make them **full-bleed 16:9** (1920x1080) by
  default, with the slide's type set over the film's quiet area. A 64:27 band under a headline is the exception.
- **ManimGX is mandatory.** Install it and smoke-test it first (manimgx-first). Write the films
  with scripts/manim_kit.py (slide-point type, pins) inside a ThreeDScene: at least one 3-D camera move (film-language).
- **Anatomy is mandatory too** whenever the topic has any structure or process (architecture,
  system, machine, pipeline, cycle): at least one film from scripts/anatomy_film.py (anatomy-first).
  It also gives an editable shapes.json.
- **Only if ManimGX or Anatomy cannot run AND the user has been told,** go down the tiers in web-film:
  scripts/web_film.mjs (HTML/SVG/Canvas in headless Chrome), then canvas_film.py, then native Morph.
  Write the tier and the reason in NOTES.md.
- **A film must MOVE:** a camera that pushes, tracks or pulls, and parts that travel. A bar
  growing or a dot sliding along a timeline is a chart animation, not a signature film. Run
  `film_check.py FILM` after every render.
- **Every film gets an editable native slide of its end state.** Use the same geometry module
  with two renderers.
- **Look at a contact strip of each film (5+ frames)** before it goes on a slide. Fix collisions,
  empty halves and tiny type.
- More: references/details/film-is-the-core.md (commands, flags, edge cases).
