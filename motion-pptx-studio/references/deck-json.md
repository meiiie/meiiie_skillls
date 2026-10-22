# deck.json reference (build_deck.py)

```
Build a 16:9 motion deck from a JSON spec: a designed system, named shapes ready for Morph.

  python3 build_deck.py deck.json --out deck/build.pptx [--base template.pptx] [--quiet]

Why: the look of a professional motion deck comes from a SYSTEM (ground, chrome, grid,
type roles, palette roles) applied identically on every slide, plus a few components
that move well (headings, cards, stats, screens, timelines, bars, lists, quotes). Write
the system once (a style pack), then write slides as compositions and keyframes.
Units are inches on a 13.333 x 7.5 canvas.

Top level
  "style": "path/to/style.json" (optional)   palette, fonts, type roles, grid, grounds, chrome, card...
  "palette" {key: "#RRGGBB"}  "fonts" {key: family}  "type" {role: {...}}  "grid" {...}  merged over the style
  "grounds": {"main": "assets/ground.jpg" | {recipe}}   "bg": default ground or colour for every slide
  "chrome": {"under": [shapes], "over": [shapes]}       replaces the style's chrome ("chrome_add" appends)
  "title": "Deck title"  (fills {title} in chrome)      "motion": {"default_ms": 1300, "stagger_ms": 220}
  "compat": "morph"|"safe"|"dual"   no-Morph safe mode (compat.py): safe rebuilds every Morph as classic
            transition + motion path/zoom/type effects; dual keeps Morph with a classic fallback
  "safe_transition": "fade"|{"type": "push", "dir": "l"}   transition that replaces Morph in safe mode
Slide keys
  "id", "from": "prev"|id, "set", "drop", "add", "front"   keyframes (see below)
  "bg": ground name | palette key | "#hex" | {"image": path}   "scene": "S3" (slide name, for audits)
  "bookend": true   a declared circular close: this slide may return to the opening image (check_deck allows
                    it on at most 2 slides instead of counting it as image reuse)
  "still": true     a deliberately still page (a printed chapter, a quiet opener): not counted in the moving-depth
                     share (at most a quarter of the deck)
  "chrome": true|false|[names]  "chrome_set": {name: {...}}  "source": "Nguồn: ..." (fills {source})
  "ms": 2000  "morph": "byObject"|"byWord"|"byChar"  "keep_timing": true   -> written to motion.json
  "notes": speaker notes
Shapes (every shape: type, name, x, y, w, h | "col": [start, span] on the grid, rot, alpha, hidden, shadow)
  text     text (str | [paragraph | {text, size, color, ...}]), role (kicker, display, title, subtitle, body,
           caption, label, numeral, quote, cardtitle, pageno...), font, size, bold, italic, color, align l|c|r,
           anchor t|m|b, spacing (pt), line (multiple), caps, fade 0..1 (+ fade_bg: a quiet text as a solid
           colour mixed toward its background; prefer it to alpha, which LibreOffice renders badly)
  image    path, fit cover|contain|stretch, focus [fx, fy], radius, line_color, line_width,
           grayscale, duotone ["#dark", "#light"], brightness, contrast (-1..1)
  rect / ellipse   fill, alpha, gradient [[colour, alpha, pos%]...], angle, line_color, line_width,
           line_alpha, radius (0..0.5), geom (any MSO_SHAPE name: CHEVRON, TRIANGLE, ...)
  line     x1, y1, x2, y2, color, width, alpha, cap round|flat, dash dash|dot
  group    shapes [...]: moves and morphs as one object
Components (expand into named parts; set the component in a keyframe, Morph moves the parts)
  heading  kicker, title, sub, body, title_role, align           parts NAME.kick/.title/.sub/.body
  card     title, kicker, desc, image, icon, state rest|lit|dim    a group NAME with children "NAME title"...
  stat     value, unit, label, src, size, color, label_color        NAME.value/.unit/.label/.src
  screen   image, device browser|phone|plain, url, focus           a group NAME
  timeline nodes [{t, label, desc}], active                        NAME.rail/.prog/.dot{i}/.t{i}/.l{i}/.d{i}
  bars     data [{label, value, display}], max, grow 0..1, highlight   NAME.base/.bar{i}/.v{i}/.k{i}
  list     items [str | {text, sub}], reveal k, focus i, numbered  NAME.n{i}/.i{i}/.r{i}
  quote    text, by, mark_size (pt, default 2.2 x size)              NAME.mark/.text/.by
  callout  at [x, y], x, y, label, desc, color, chip, elbow, dot      NAME.ring/.dot/.lead/.labk/.lab/.desc (v5.4)
  swatch   image | colors, n, dir h|v, hex, labels, vivid            NAME.s{i}/.h{i}: a palette strip sampled from a photo
  photogrid images [path | {path, span [c, r], label, focus}], cols, rows, gap, border, tilt   NAME.f{i}/.p{i}/.t{i}k/.t{i}
  nodemap  nodes [{x, y (0..1), label, desc, side, big}], links [[a, b]], image, dash   NAME.map/.e{k}/.n{i}/.t{i}k/.t{i}/.d{i}
v5 motion and style keys
  slide  "style": "swiss-blue"   switch the whole system (palette, fonts, roles, grounds, chrome) for this
                                 slide and its keyframes: a deck can change style per chapter
         "transition": "curtains" | {"type": "push", "dir": "l", "ms": 800}   any native transition
                                 (motion.py --list); default Morph. "ms" still sets the duration.
  shape  "anim": {"fx": "fly", "dir": "l", "delay": 200, "ms": 600} | [ {...}, ... ]   entrance,
                                 emphasis, exit, path, orbit, letter-by-letter ("fx": "type"), loops
                                 ("loop": true), clicks ("click": 1) and triggers ("trigger": "<name>").
                                 On a component that expands into several top-level parts, the effect is
                                 applied to every part with "stagger" ms between them (default 120).
         "link": "<slide id>"    click the shape in the show to jump there (a hand-made slide zoom)
  line   "arrow": true | "stealth" puts an arrow head at x2,y2 ("arrow_start" at x1,y1)
  types  video  path (mp4), poster (png/jpg; default: first frame via ffmpeg), loop, mute, autoplay
         poly   points [[x, y], ...] (inches), closed (default true; "open": true = closed false), fill, alpha, line_color, line_width: freeform
                shapes for isometric solids, paper-cut layers, arrows and masks
Keyframes: "from": "prev" copies the slide; "set" {name: {keys}} changes shapes and components by
name; "drop" removes names; "add" appends; "front" moves names to the top. Unknown names are errors.
After building: use build.py (build_deck -> unpack -> motion -> pack -> render -> film_check).
```
