# Signature moments (v5.3.1)

A signature moment is a **hand-built animated diagram of the subject's own mechanism**: the press line
that turns a coil into a car, the cells that light in series inside a pack, the request that crosses a
system. It is the slide people remember, and it is the part a template can never give you.
Every deck has **at least two** (gate 4 plans them, gate 6 checks they are embedded and move).

What it is NOT: a stock metaphor (book = knowledge, scales = law, lightbulb = idea, handshake =
partnership, robot = AI, globe in hands = global, puzzle, rocket, chess). If the motion could illustrate
any other company, it is not a signature moment. Draw the thing itself.

## 1. Choose the moment (10 minutes, before the storyboard)

For each candidate write ONE sentence: *what moves = what it means*. Then keep the two or three where
the motion carries a fact you can source:

| bad (decoration) | good (mechanism) |
|---|---|
| gears turning behind the title | a steel coil enters a press, the panel goes to welding, paint turns it blue, wheels drop at assembly: 4 shops, 1,200 robots |
| a glowing battery icon | the lid lifts, modules settle onto the cooling plate, cells light in series: the pack is a structure, not a box |
| a bar chart that grows | plants stacked as 50k-unit slabs on a floor map; the planned US plant is a dashed footprint that gets crossed out |

Write them in `design/signature-moments.md`:

| # | moment | tool | mechanism | facts | film | editable | slides |
|---|---|---|---|---|---|---|---|
| M1 | Dây chuyền Hải Phòng | anatomy | a coil becomes a body in four shops; the lit part is the station that is working | 4.9, 4.10 | assets/film/haiphong-line.mp4 | assets/film/haiphong-line.shapes.json | 9-11 |

`tool` is `anatomy` or `manim`; `diagram_video` counts only with `signature_fallback: <reason>` in brief.md.
`editable` is the shapes file (Anatomy) or a `!!layer` drawn natively on the slide (Manim).

## 2. Anatomy recipe (isometric machines)

**What Anatomy is.** https://skills.wheresryan.sh/anatomy (Ryan, MIT, github.com/wheresryan22/anatomy):
a skill + a small Node kit (`kit/iso-kit.mjs`) that draws a technical idea as a *real machine* in
isometric projection, from many small solid parts, in four tones and one lit accent. Its rules, which
this skill keeps: the object is the explanation; no words inside the drawing; 40+ parts; one accent
colour for the part that matters now; paint back to front.

Setup (once per machine): `bash $S/setup_anatomy.sh` (Node ≥ 20.10, Chrome, ffmpeg; clones into
`~/.local/share/anatomy`, test-builds an example, exits 2 with a fallback note when something is missing).

Write `WORK/design/anatomy/<name>.mjs`:

```js
export default (k) => {               // k = Anatomy's iso-kit
  const W = 1600, H = 560, T = 12;     // canvas px, loop length s
  const P = k.fitProjection(cornersOfEverything, W, H, { pad: 24, azimuth: 76 });  // 76 ≈ a line along x stays flat
  const box = (x, y, w, d, z, h, tone) => k.solidSvg(k.slabOf({ x, y, w, d, r: 2 }, z, h, P, 3, 0.5), { tone });
  return {
    width: W, height: H, seconds: T, theme: 'light',
    tokens: { '--anatomy-card': '#FFFFFF', '--anatomy-lit': '#1464F4' },   // the deck's palette
    poster: 7.2,                                     // the frame that becomes the poster + editable shapes
    anchors: (t) => ({ press: k.iso([120, 0, 40], P) }),   // screen points -> inches in film.json for labels
    frame: (t) => [/* back */ bench(), coil(t), press(t), /* front */ agv(t)].join(''),
  };
};
```

Craft rules that made the VinFast figures read:
- **A clock, not keyframes.** One period (e.g. TC = 3 s per station, DWELL 1.9 s), positions are pure
  functions of `t`; the loop is seamless when `frame(0) == frame(T)`.
- **Depth.** Sort parts by `k.depthOf(point, P)` (larger = nearer) and draw far to near; put objects
  that sit *outside* a case before the case if they are behind it.
- **One lit part at a time.** `tone: 'lit'` on the station that works now; everything else stays in the
  four greys. The accent is the narration.
- **Parts, not blobs.** Bolts (`dotsSvg`), seams (`sideSeam`), rings (`sideRing`), ticks (`topTicks`),
  cable runs (`wireSvg`). 40+ parts is the floor; the battery pack figure has ~1,300 shapes.
- **No words in the SVG.** Labels are slide text placed at `film.json` anchors, so they stay editable,
  translatable and searchable.
- **Anchors and frames are checked (v5.4).** `anchors` may be an object or a function `(t) => ({...})`; values
  are `[x, y]` or `{x, y}` and must be finite numbers. `frame(t)` must return an SVG string (an array is
  joined). A helper given an object where it wants a string (e.g. `topTicks({minor, major})` passed on as
  a path) used to crash with "[object Object]" and a "run setup again" hint; now `film.mjs` stops with
  `FIGURE ERROR: …` naming the anchor or the frame, and `anatomy_film.py` says the figure, not the setup,
  needs fixing. A figure that talks about anchors but exports none gets a WARN.
- **Honest scope.** A generic mechanism (a typical EV pack) is labelled "minh họa / illustration" on the
  slide; never present it as the company's engineering drawing.

**Density and contrast (v5.3.1).** Anatomy's own examples (the desk computer is ~110 solids) read because
they are dense, fill the card and have crisp edges. A figure that is half empty or dim reads as clip art.
`anatomy_film.py` audits the poster and writes `film.json` → `audit` (gate 4/6 warn, edges < 3:1 fail):

| measure | floor | how to fix |
|---|---|---|
| solids (`iso-solid` count) | ≥ 120 | add the parts a technician would name: straps, terminals, bolts, ports, harness, cabinets, fences, racks |
| figure width / area of the frame | ≥ 70 % / ≥ 40 % | turn `azimuth` until the long axis lies across the frame (64–76 for a long object), cut `pad`, crop `--region` to the figure |
| edge contrast (97th pct vs card) | ≥ 4.5 : 1 | `--anatomy-hi` near white on dark cards, near ink on light; `--anatomy-weight` ≥ 1.1 px |
| face contrast on a dark card | ≥ 2.2 : 1 | lift `--anatomy-top` / `--anatomy-shade-*` (VinFast pack: top #2A4C8C, shades #142B57…#234781 on #0A1A33) |

Explode layers with gaps that grow upward (`GAP = [0, 10, 22, 34, …]`) rather than one big lift: the eye
reads the build order and the frame stays full. LOOK at `.strip.jpg`; the audit is a floor, not taste.

Render:

```bash
python3 $S/anatomy_film.py WORK/design/anatomy/line.mjs --name haiphong-line --work WORK \
        --region 0.87,2.6,11.6,4.06 --fps 25 --scale 1.25
```

Outputs `assets/film/<name>.mp4` (H.264, faststart, tagged BT.709 so players do not shift the whites), `.poster.png`, `.strip.jpg` (8 frames: LOOK at it),
and `.shapes.json` (a deck.json `group` of native freeforms, minimum line 0.35 pt). Build time is about
15 ms per shape in build_deck; keep `--max-shapes` ≤ 4000.

## 3. Manim recipe (data and space)

ManimGX (Manim CE API on a Rust/wgpu renderer; CPU via lavapipe works headless):

```bash
manimgx render design/manim/capacity.py Capacity -r 1920x1080 --fps 30 -o assets/film/capacity.mp4
manimgx inspect design/manim/capacity.py Capacity     # storyboard frames: LOOK before the full render
ffmpeg -sseof -0.1 -i assets/film/capacity.mp4 -frames:v 1 assets/film/capacity.poster.png
```

- Use it for quantities in space: stacked slabs = units, an arc = a supply flow, a dashed footprint = a plan.
- White or deck-ground background; fonts the deck ships (`Text(..., font='Be Vietnam Pro')` renders Vietnamese).
- `ThreeDScene` has no fixed-in-frame labels in ManimGX 0.1: put labels flat on the floor or set them on
  the slide. `FadeIn(m, shift=UP*0.3)` instead of FadeIn + `.animate` in one `play` (that left slabs
  translucent).
- Editable version: **one geometry module, two renderers.** Put coordinates (in slide inches), colours and
  text sizes in `design/manim/<name>_geom.py`; the Manim scene maps inches to units and the deck calls
  `<name>_geom.editable_shapes()` for the native shapes. The editable slide is then the film's last frame by
  construction, not a hand redraw. Name one group in the `editable` column.
- Fill the frame: render at the slide box's aspect (`-r 2360x1000` for an 11.5 × 4.87 in box), labels at the
  deck's sizes (scale text from a reference glyph so 18 pt in the scene is 18 pt on the slide), 2D and upright.
  Grab the poster as the last real frame: `ffmpeg -i f.mp4 -vf "select=eq(n\,N-1)" -fps_mode passthrough`
  (`-sseof` can land past the last frame of a Manim file).

## 4. Put it on the slide

```json
{"type": "video", "name": "!!film-line", "path": "assets/film/haiphong-line.mp4",
 "poster": "assets/film/haiphong-line.poster.png", "x": 0.87, "y": 2.6, "w": 11.6, "h": 4.06,
 "loop": true, "mute": true, "autoplay": true}
```

- **Film and page colour.** The film's card colour must be the slide's ground: give film slides a solid
  `bg` equal to the card (`"#FFFFFF"`, `"#0A1A33"`), not a gradient or texture ground, and keep the BT.709
  tags. `check_deck.py --renders DIR` compares the poster border with the rendered ring around the video:
  a difference > 6 levels is an ERROR, > 2 a WARN.
- **Labels never sit under a film.** Pass `--region` = the video box, then place station labels outside it
  (above, with leaders that stop at the figure) or in z-order above the video. `check_deck.py` errors on
  any text below a video in z-order that overlaps it.
- Keyframe K1 shows the **editable shapes** (the poster as freeforms) and the labels; K2 plays the film in
  the same box (Morph or fade between them); K3 zooms one station with a Morph of the shapes group.
- Labels and numbers are slide text next to the film, each with its fact ID in the source column.
- A film never carries the only copy of a fact: the poster/shapes and the notes say it too.

## 5. Fallback (honest)

If Node/Chrome or ManimGX cannot run: write `signature_fallback: <what failed>` in brief.md and build
the moments with `diagram_video.py` (drawn SVG frames) or as Morph keyframes of native shapes. Tell the
user which tool failed. Never fill the slot with a stock clip or a generated "explainer" image.
