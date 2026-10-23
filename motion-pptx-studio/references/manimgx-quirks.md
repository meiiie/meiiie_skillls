# ManimGX quirks and fixes (learned on the "Khí áp" flagship, 6 films; install: principles/manimgx-first.md)

Render: `manimgx render film.py Scene -r 1920x1080 --fps 30 -o assets/film/name.mp4`
(tests: `-r 1280x540 --fps 15`, ~4x faster). A 16:9 film is full-bleed (default, ds.FILM_ASPECT 16/9); a 64:27 film fills a 12.133 × 5.119 in band
at x 0.6, y 1.62 on a 13.333 in slide; scene units 18.963 × 8.

| Quirk | Symptom | Fix |
|---|---|---|
| **Fonts resolve by nameID 1** (the legacy family name), not by the full name | `Text(font='IBM Plex Sans Medium')` silently falls back | Use the nameID-1 names: `'IBM Plex Sans Medm'`, `'IBM Plex Sans SmBld'`, `'Source Serif Pro Semibold'`. Check with `fc-query -f '%{family}\n' font.ttf`. |
| **Typst text engine reads typographic families** | `font='Fraunces SemiBold'` or `'Barlow Condensed'` silently falls back to a serif | Use family + weight: `font='Fraunces', weight='SEMIBOLD'`; a file named Barlow Condensed is family `'Barlow'` (+ `weight=BOLD`). Test-render one frame first. |
| **No matplotlib in ManimGX's python** | `import matplotlib` (e.g. a contour helper) fails inside the render | Precompute geometry in the system python (contours, streamlines) to JSON (`pressure_geom.json`, `wind_xy.json`) and only load JSON in the film. |
| **Output is VFR** | `ffmpeg -ss` stills land on the wrong frame | Grab stills by frame index (`select=eq(n\,N)`), see `examples/flagship-khi-ap/films/sheet.py`. |
| **Stroke widths scale with the camera frame** | A camera push makes hairlines thick, a pull makes them vanish | Good for a real push (lines get closer). For pans where line weight must stay, use `kit.View` (moves the content, not the frame). |
| **`self.play` re-adds animated mobjects on top** | After a scale/move animation, an `always_redraw` layer (water, fill) disappears behind the tube that was animated | Order the play: animate the back layer too, or add `UpdateFromFunc(mob, lambda m: None)` for the always_redraw mobject after the others in the same `play` so it is re-raised. |
| **Text in per-frame redraws is slow** | `always_redraw` that builds `Text` each frame takes minutes | Build the Text objects once (a dict keyed by string, outside the redraw) and only move or recolour them inside it. |
| **Exceeding a tool timeout loses unwritten files** | Long heredocs in a call that hits the harness limit are not written | Write the film files first, render in the background (`> log 2>&1 &`), poll the log. |

## The editable native fallback
Every film's last frame is also drawn natively from the SAME geometry module (`*_geom.py`): the film imports
it for ManimGX, the deck script imports it for python-pptx. `make_m1.I(x, y)` maps scene units to slide inches and
`W(sw)` maps ManimGX stroke widths to points, so the native slide matches the poster pixel for pixel.

# LibreOffice grey bands (theme effectRef) — fixed in build_deck 5.7
python-pptx autoshapes/freeforms carry `<p:style>` with `effectRef idx=2`; LibreOffice and some PowerPoint
themes then paint the theme's soft shadow under every hairline, which turns a map of 1 000 thin polys into
grey bands. `build_deck.strip_theme_style()` (v5.7) removes `<p:style>` from every text-less drawn shape
before saving; shapes with text keep it (their fontRef supplies the default text colour). For decks built
with an older engine: `python3 examples/flagship-khi-ap/postfix.py deck.pptx`.


## v6.21 notes (peer test)
- ManimGX has `add_fixed_in_frame_mobjects` but no `remove_fixed_in_frame_mobjects`: `self.remove(mob)` it, or
  fade its opacity to 0, then re-add a new one.
- Lights: `SunLight`, `SpotLight`, `PointLight`, `EnvironmentLight`; surfaces take `set_material(Material(...))`.
- Fonts: `embed_fonts.py DECK --font "Family=Regular.ttf,Bold.ttf,Italic.ttf"` (one --font per family). Variable
  fonts (`[wght]`) do not embed reliably: download or instance static files first (fonttools `varLib.instancer`).
- **Size:** every film renders `-r 1920x1080` (16:9, full-bleed); test at `-r 960x540 --fps 15`. film_check's
  depth metric is resolution/fps-normalised, so a test render and the final measure alike.
- `from manimgx import *` exports a geometry `Path` that shadows `pathlib.Path`: `import pathlib` and write
  `pathlib.Path(...)` (or import pathlib after the star import as `from pathlib import Path as FPath`).
- `ImageMobject` has no `set_height`/`set_width`: use `img.scale(h / img.get_height())` or `stretch_to_fit_height`.
- Dense particle fields (> 5k dots) need some larger lit structure (planet, grid, ground texture) in frame so the
  depth metric can track the camera.
