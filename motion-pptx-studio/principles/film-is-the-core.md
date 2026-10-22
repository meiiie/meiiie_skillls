# film-is-the-core
A deck without signature films has failed this skill, however good its text slides are.
Never skip silently.
- Plan 3-6 films (one per main chapter), 10-20 s each, 1920x810 (64:27) for the
  full-width film window.
- Route 1: Manim (`manimgx`, scripts/manim_kit.py: slide-point type, a 2-D camera,
  pins). Route 2: no Manim -> scripts/canvas_film.py (pure Python + Pillow + ffmpeg, a
  camera, piped frames). Route 2b: isometric machine -> scripts/anatomy_film.py (Node +
  Chrome; gives an editable shapes.json too). Route 3: no ffmpeg -> native motion paths
  + Morph across 2-3 slides that redraw the same picture. Write which route you used,
  and why, in "Principles used".
- A film must MOVE: a camera that pushes/tracks/pulls, parts that travel. `film_check.py
  FILM` after every render.
- Every film gets an editable native slide of its end state (same geometry module, two
  renderers).
- Look at a contact strip of each film (5+ frames) before it goes on a slide; fix
  collisions, empty halves, tiny type.
