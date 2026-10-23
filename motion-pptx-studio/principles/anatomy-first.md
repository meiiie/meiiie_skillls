# anatomy-first
Anatomy (https://skills.wheresryan.sh/anatomy, MIT, github.com/wheresryan22/anatomy) draws an idea as a
real isometric machine built from many small solid parts. Its rule is "the object is the explanation".
**It is required whenever the topic has any structure or process:** architecture, a system, a machine,
a supply chain, a pipeline, a cycle, an organisation, an isometric scene. Then the deck has at least one
Anatomy film in addition to its ManimGX films.

**Step 0, alongside ManimGX: install it and smoke-test it.** It needs Node 20.10+, Chrome or Chromium
(headless) and ffmpeg. The clone is about 27 MB.
- Install: `bash scripts/setup_anatomy.sh`. This checks node, chrome and ffmpeg, clones the repo to
  ~/.local/share/anatomy, builds the dial example and prints `export ANATOMY_HOME=...`.
- **No GitHub** (ChatGPT: git is blocked, npm goes through a proxy, and the `anatomy-figures` npm
  package has no kit):
  - fetch `https://github.com/wheresryan22/anatomy/archive/refs/heads/main.tar.gz` with
    container.download, or ask the user to upload it;
  - `tar xzf` it, then `export ANATOMY_HOME=$PWD/anatomy-main`.
  - If Chrome is missing, set `CHROME=/path/to/chromium`.
- Smoke test (10 s, 75 frames):
  `python3 scripts/anatomy_film.py scripts/anatomy/smoke.mjs --name smoke --work /tmp/anat-smoke --region 0.6,1.6,12.1,5.1`
  It must print `film`, `motion` and `editable`. The two WARN lines (fewer than 120 solids, low
  contrast) are expected for the smoke test only.

**How anatomy_film.py works:**
- Your FIGURE.mjs is `export default (k) => ({width, height, seconds, theme, tokens, poster, anchors, frame(t)})`.
  `k` is Anatomy's `kit/iso-kit.mjs` (fitProjection, slabOf, cylinder, solidSvg, lineSvg, depthOf).
- scripts/anatomy/film.mjs renders every frame in headless Chrome with the kit's CSS, and ffmpeg
  encodes the result.
- Output in assets/film/: NAME.mp4, poster.png, a .strip.jpg and shapes.json. The shapes.json is the
  editable native group for the end-state slide.
- Flags: `--fps 25`, `--scale 1.25`, `--width 1920` (mp4 px), `--region x,y,w,h` (slide inches),
  `--poster-only`.
- Recipe:
  - 80-150 solids: a bench, stations, a clock and one lit part;
  - paint back to front with `depthOf`;
  - frame(t) is a pure function of t;
  - no words in the drawing (labels are slide text at `anchors`);
  - palette from your ds.py via `tokens`;
  - **hero shot (film_check FAILS otherwise):** 80+ parts, edges >= 4.5:1 against the ground, the machine fills
    >= 50 % of the poster, and the medium visibly flows in >= 60 % of the middle seconds. The camera
    moves too: push in, or re-fit the projection over t;
  - **a visible flowing medium** (water, grains, signal, people) travels through the machine for most of the film;
  - **show the process, not only the build:** after a short assembly (<= 1/3 of the runtime),
    the machine works: particles/drops travel along a path as a function of t, levels fill,
    a dial turns, a lit part moves station to station (film-language).

**If Anatomy cannot run, STOP and tell the user** the exact missing piece (node, chrome or the
archive). Never skip it silently or swap in a diagram without their agreement and a reason in NOTES.md.
