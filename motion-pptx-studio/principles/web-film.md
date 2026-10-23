# web-film
A portable film route for places where ManimGX or Anatomy truly cannot install (ChatGPT on the web,
locked sandboxes). Films stay mandatory.
- **Tier order:**
  1. ManimGX and Anatomy, whenever installable (manimgx-first, anatomy-first).
  2. web-film.
  3. canvas_film.py.
  4. Native Morph.
  Always report which tier you used and why: tell the user, and write it in NOTES.md.
- **web-film: a page renders the film.** One HTML file per film (SVG, Canvas or DOM, plus JS)
  defines `window.SECONDS` and `window.frame = (t) => {...}`.
  - frame must be a pure function of t: no clocks, no requestAnimationFrame loops, no unseeded random.
  - Use the deck's ds.py palette and local font files.
  - Render: `node scripts/web_film.mjs film.html --out assets/film/NAME.mp4 --fps 30 --w 1920 --h 810`
    (headless Chrome plus ffmpeg). Then run `python3 scripts/film_check.py NAME.mp4`.
  - Smoke test: `scripts/web/smoke.html` takes 3 s and renders in about 8 s.
- **No Chrome, but Python, Pillow and ffmpeg:** draw the same idea with `scripts/canvas_film.py`.
  If ffmpeg is missing, `pip install imageio-ffmpeg` gives you a static binary.
- **No code execution at all (browser-only):**
  - deliver film.html as an HTML animation, plus PNG keyframes;
  - build the slide motion with native Morph across 3-5 slides that redraw the same picture;
  - say clearly that the mp4s are missing and why.
- **The bar is the same in every tier:** a camera that pushes, tracks or pulls, parts that travel,
  10-20 s per film, and an editable end-state slide. It is never a slideshow of stills.
