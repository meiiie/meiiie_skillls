# Changelog

## 5.5.0
Open-ended by construction: the skill routes each deck to a fitting direction before design, invents the
deck's own system from a genome, and builds diagrams the way Anatomy and Manim do. Darren's v5.4 review ("the
collage style does not fit SpaceX") is now a gate.
- **Self-routing (gate 3)**: new `route.py` / `studio.py route WORK [--choose X --why …] [--apply]` analyses the
  brief's topic, audience, tone and kind, the facts and credits (bilingual lexicons) and MEASURES the pictures
  (luminance, saturation, warm/cool, archival prints, cut-outs, pre-1970 dates). Every family carries a `fit`
  block (domains, tones, material, `avoid` with written reasons) and is scored (0.45 subject + 0.20 tone + 0.35
  material); mismatches are rejected in writing (heritage collage for aerospace, noir/swiss/glass for heritage…);
  `design/routing.md` records the ranking and the decision. Gate 3 FAILs without routing or when the deck's
  family was rejected; WARNs when routing is stale, the deck uses another family, or fit < 0.60.
  `studio.py new` no longer needs `--style` and refuses a rejected one.
- **Genome / design space**: new `genome.py compile|distance|axes`. `design/genome.json` decides each axis
  (palette sampled from the hook photo, type ratio and faces, grid, material, chrome corners, motion grammar,
  image treatment, signature, colour arc, motifs, layers) with a reason and compiles `design/style.json` plus
  `design/art-direction.md`. Contrast is enforced against the ground as it renders (stained paper edges,
  vignette), the type scale stays ≤ 8 sizes. `distance` measures how different two decks are (fonts, sizes,
  effects, transitions, layout occupancy, rendered colour). New `references/design-space.md` (with the audit of
  everything that forced fixed output in v5.4).
- **Construction motion**: new `construct` component (`scripts/construct.py`, `references/construction-motion.md`):
  a part model (rect, ellipse, line, poly, arc, text, image, iso_box, iso_cyl) with layers, `on`, steps, groups,
  states; automatic build order (base → structure → mechanism → controls → subject, labels after their part),
  Manim verbs mapped to native effects (Create → wipe along the stroke, GrowFromEdge → stretch from the
  contact edge, Write → letter type, Circle Create → wheel, LaggedStart fitted to `total_ms`, Indicate, trace),
  a camera (focus/zoom/at) and states that Morph between slides on one rest-geometry fit; one lit part per frame.
- **Engine**: `stretch` (entrance preset 17, from t/b/l/r/h/v) and `indicate` (scale pulse) effects;
  `variety_audit` knows stretch; `preview_motion.py` simulates stretch and draws the wheel as a clockwise sweep.
- **directions.py**: free-text composition with a `sketch` hint and a `family` per direction (directions are
  routing candidates).
- **Fix**: `route.py` read years in file names only before a dot was excluded (`…_1905.jpg` gave no date).
- **Proof**: two 7-slide samples from the same skill, routed automatically: `v55-spacex` (noir-product genome
  "night return", heritage-collage rejected for aerospace) and `v55-doson` (heritage-collage genome "summer
  1905", noir/swiss/glass rejected for heritage), each with construction diagrams, camera moves and state
  transforms; `genome.py distance` between them is reported in the sample notes.
- Tests: `tests/test_v55.py` (15).

## 5.4.0
Fixes every bug, ambiguity and weakness from the SpaceX v5.3.1 test (`spacex-test/NOTES.md` §3, 22 items) and adds a
first-class heritage magazine / collage style measured from the Ôn Lăng reference deck and its public critique.
- **Full-deck builds by default** (bug 1): `studio.py build WORK` without `--group` builds every slide into
  `deck/unpacked` (+ `preview-all.pptx`, `renders/all-N`); a group build works in `deck/unpacked-<group>` and never
  overwrites it, so Phase 6 can no longer pack a 7–9 slide "final". New `studio.py final WORK` runs Phase 6 in one
  step and refuses to pack a deck whose slide count differs from deck.json.
- **Deck-level gate 5** (bug 2): `gates.py check WORK --gate 5 --group all` (and `--upto 5+`) checks
  `preview-all.pptx` (current, complete) with check_deck, so deck-wide layout repetition fails before Phase 6.
  `--upto` ends with a SUMMARY and the first FAIL; `--stop-on-fail` stops there (weakness 22).
- **Bookend reuse** (bug 3): `"bookend": true` on a slide (≤ 2) lets a circular close return to the opening photo.
- **Anatomy** (bugs 4, 5): anchors as a function or an object, `{x, y}` or `[x, y]`, validated; a non-string
  frame or an object passed as a path stops with `FIGURE ERROR` (exit 3), not a "re-run setup" hint.
- **Small fixes**: poly `"open": true` works (bug 6); `motion.py --list` needs no folder (bug 7); gate 2 counts real
  photos with whole words (no more domAIn/trAIn/aperTURE, bug 8); gate 3 reads the "Motifs and textures"
  heading only and drops negated clauses ("never fly") from the motion vocabulary (bug 9); gate 2 names CREDITS rows
  that sit outside the table (bug 10); `contact_sheet.py` and `cutout.py` apply EXIF rotation (bug 11);
  `preview_motion.py --max-seconds` fits every slide (holds shrink first, `--cut` = old behaviour), `--lang vi`
  label, `--label-size` (bug 13); `studio.py compare` picks the reference by deck kind (ca trù only for heritage),
  accepts a folder of reference images and `--layout side` (bug 17).
- **cutout.py rewritten** (bug 12): border-connected background with an edge-detail test (dark object parts stay),
  closing + hole fill, a background halo peel, `--defringe` (outline un-mixed from the old background, default 6 px),
  `--bridge` for wide dark bays, scipy with a PIL fallback.
- **Custom styles** (bug 14): `"styles": {"name": {"extends": pack, ...}}` in deck.json, and `style_overrides` entries
  that are not packs define styles too; experimental packs load by name.
- **One number for keyframe runs** (bug 15): "at least half of the scenes" everywhere (SKILL.md, storyboard template,
  pro-craft, gate 4).
- **Type-scale headroom** (bug 16): every pack ≤ 8 sizes (caption = label = page number, subtitle = card title).
- **Moving depth that means something** (bug 18): the plate must be a picture, video or textured/gradient shape and
  the moving layer ≥ 1% of the slide and over it; `"still": true` pages (≤ a quarter) leave the share.
- **Gate 4 layout note** (bug 19) says the storyboard label count is advisory and check_deck's geometry decides.
- **Size headroom** (weakness 21): gate 5 warns above 80% of the limit, gate 6 fails above it and warns above 85%.
- **heritage-collage pack** (weakness 20 + the collage brief): aged paper (`paper` ground `stains`, `fibres`) and
  `gradient` grounds; Anton caps titles with 1–2 accent runs, a `script` role (Dancing Script, rotated, may cross
  a title: role-level `rot` and `overlay`), a `callout` role; components `callout` (dot + leader + chip),
  `swatch` (palette sampled from a photo or a cut-out), `photogrid` (bordered prints, spans, tilt, chip labels),
  `nodemap` (red nodes, links, chip labels). `references/styles/heritage-collage.md` documents the grammar.
- **Legibility audit** (`scripts/legibility_audit.py`, the critique's two rules): a paragraph of 12+ words in ALL CAPS
  below 28 pt is an ERROR in check_deck and a FAIL row in gates 5/6; text on a photo without a band, chip, gradient or
  toned photo is a WARN (`--scrim strict` = ERROR; a FAIL row for heritage-collage decks). Transparent cut-outs do
  not count as photos.
- Proof: `/workspace/collage-v54` (7-slide collage sample), `/workspace/smoke40-v54` (40-slide full build).
- Tests: `tests/test_v54.py` (35 tests).

## 5.3.1
Review fixes before the 5.3 push: every weakness found in the VinFast v5.3 proof deck becomes a rule or a check.
- **Anatomy density and contrast**: `anatomy_film.py` audits the poster (solids, share of the frame width and area,
  edge and face contrast against the card) and writes it to `film.json` → `audit`. Floors: ≥ 120 solids, ≥ 70 % width /
  40 % area, edges ≥ 4.5:1, faces ≥ 2.2:1 on dark cards. Gate 4/6 turn audit findings into WARN rows and fail edges
  below 3:1. `references/signature-moments.md` §2 "Density and contrast" says how to fix each one.
- **Film and page colour**: films are tagged BT.709 (Anatomy and diagram_video), and `check_deck.py --renders DIR`
  compares the poster border with the rendered page ring around each video (ERROR > 6 levels, WARN > 2).
  Rule: a film slide gets a solid `bg` equal to the film card.
- **No label under a film**: `check_deck.py` errors on text that sits below a video in z-order and overlaps it
  (`scripts/film_audit.py`).
- **Manim films with an exact editable twin**: the recipe now puts geometry in one `<name>_geom.py` shared by the
  scene and the deck, so the editable slide equals the film's last frame; render at the slide box's aspect and
  take the poster from the last real frame.
- **Build speed**: python-pptx's shape-id scan (O(n²)) and per-child group extent recalculation are patched;
  the 30-slide VinFast deck builds in about 6 s instead of 133 s. Ids stay unique (tested).
- **Small fixes**: effect `dir` accepts `u`/`d` (as transitions do) instead of raising KeyError; `quote` takes
  `mark_size` so the mark can sit on the deck's type scale; SKILL.md craft rules add a ≤ 10-size type scale and
  the film rules; qa-checklist adds the film checks.
- Tests: `tests/test_v531.py` (11 tests).

## 5.3.0
Floor, not ceiling. The v5.2 VinFast test passed every gate and still looked like a template (14 slides of text left,
photo right on one dark pack). This release adds hand-built signature moments, a second asset source, an
anti-template phase, slimmer gates and fixes all nine bug groups from that test.
- **Signature moments (mandatory)**: ≥2 hand-built animated diagrams of the subject's own mechanism per deck
  (`references/signature-moments.md`, template `assets/templates/signature-moments.md`). Tools: **Anatomy**
  (isometric machine kit, MIT; `setup_anatomy.sh`, `anatomy_film.py` + `anatomy/film.mjs` film it headless over
  CDP and convert the poster into native freeforms for an editable keyframe) and **ManimGX**. Gate 4 checks the
  plan (mechanism sentence, no stock clichés, cited facts, poster, editable part); gate 6 checks the films are
  embedded (sha256 in the pptx media), at least 3 s long and actually move. `signature_fallback: <reason>` in
  brief.md allows a diagram_video.
- **Codex image generation** as the second asset source (`gen_assets_codex.py`): textures, grounds, generic objects
  and plates only; logos, real people, clichés and fake factual images are refused by a prompt lint. Every file
  lands in `assets/gen/` with a JSON sidecar and an "AI-generated" CREDITS row; gate 2 fails unlabelled ones. When
  Codex is unavailable the script says so and the deck falls back to licensed photos and procedural grounds.
- **Anti-template phase**: `directions.py` renders three art directions as thumbnails (`design/directions.jpg`);
  gate 3 fails unless they are three real alternatives (palettes differ, ≥25 words each) and one is chosen with a
  reason. Decks of 20+ slides must shift style at scene level (gate 4). `variety_audit.py` gains a geometry
  fingerprint: text-left/photo-right (or the mirror) on 4+ slides is an ERROR in every mode, and one
  fingerprint on more than 30% of a 10+ slide deck is an ERROR. The fingerprint also records full-bleed plates and
  big native drawings, so a diagram slide is not mistaken for a bare title.
- **Slimmer gates**: hard rows (FAIL) are kept for facts and sources, licences and labels, and render integrity;
  counts, quotas and freshness are advisory (WARN, `Gate.want()`). SKILL.md gains "Skill is a floor, not a ceiling".
- **Fixes from the v5.2 test (NOTES.md, all with tests in `tests/test_v53.py`)**: markdown tables with escaped `\|`
  and rows broken across lines are reported, and gate 4 fails malformed rows; a scene column no longer counts as a
  source ID; on-slide numbers must cite a fact; the do-not-say list no longer counts as facts; unsourced fact rows
  fail; `company-profile` deliverable kind; `latest_round` picks rounds numerically; `studio.py build --group`
  sequences and cleans each group and gate 5 runs for every rendered group (`--upto`); contact sheets write a
  manifest so freshness is checked by content; `fetch_commons.py` defaults to Commons, has short Openverse
  timeouts and normalises MPO/EXIF/CMYK/huge images on keep; `build_deck.py` converts PowerPoint-unsafe images;
  `preview_motion.py --max-seconds`; `python` → `python3` across docs and scripts.
- New references: `signature-moments.md`, `art-directions.md`; updates to asset-sourcing (Codex §6b, logos §6c),
  genres (company profile), research-protocol, craft (fonts), pro-craft (Morph share applies to scene cuts only).
- Proof: a 30-slide VinFast company profile rebuilt with v5.3 (three directions, three signature films).

## 5.2.0
Pro craft: variety, composition and flavour. The phin sample was judged "better, but not truly professional" (too
little animation variety, weak composition, too little flavour, too little overall variety); this release turns those
four gaps into rules and measurements.
- **`references/pro-craft.md`** (new, cited: Kurzgesagt, Eames *Powers of Ten*, Duarte, Fluent 2 motion, Microsoft
  Learn easing, BrightCarbon and CreativePro parallax, Microsoft Morph tips, NASA media guidelines). Covers the
  motion verb per scene, the cut grammar, eight composition systems, three planes and parallax, sub-styles, the
  narrative device and the harsh-critique ritual.
- **`scripts/variety_audit.py`** (new): names every effect node's technique, counts transition types, composition
  signatures per scene cut and moving depth/parallax. Thresholds: ≥10 techniques, top ≤35%, ≥5 transitions,
  ≥60% compositions, no 3 equal in a row, ≥20% moving depth (decks of 15+ slides).
- **`check_deck.py --variety {warn,strict,off}`** (default warn) prints the variety line and census; strict makes
  misses errors. Calibration: Earth deck passes (18 techniques, top 28%, 11 transitions, 12/14, depth 13/22). The
  phin sample warns on depth. The catru reference warns 4 times (3 techniques, fade 73%, 1 transition) and still exits 0.
- **Rotation-aware layout checks**: `build_deck.py` safe-area and collision checks and `craft_audit.py` safe area
  use the rotated box for `rot` text. The overflow check still uses the unrotated box the text is set in. Vertical
  numerals no longer raise false warnings.
- **`preview_motion.py`**: sprite crop is clamped to the image bounds (fixes DecompressionBombError on huge
  Morph zoom shapes).
- **`gates.py` gate 6**: `talk_minutes: 6 (default chosen …)` is parsed to the number. Before, the free text
  made `words_budget.py` fail and gate 6 reported a false time overrun.
- `qa-checklist.md` §4b variety gates; SKILL.md reference map row; `examples/earth-fall` (22-slide Vietnamese
  Powers-of-Ten deck, four sub-styles, two Manim films).

## 5.1.0
No-Morph safe mode. Morph plays only in PowerPoint 365/2019+; 2016, Google Slides, Keynote and LibreOffice fell
back to a plain fade where shared shapes jump.
- **`compat`** deck key (`morph` default | `safe` | `dual`) and `safe_transition`, written to motion.json
  (`build_deck.py`), documented in SKILL.md, motion-library.md §4b, build-engine.md A.3c, qa-checklist.md §4.
- **`compat.py`**: Morph → classic rebuild from the geometry of shared `!!` shapes: moved → appear/zoom + motion
  path from the old place (`from_offset` paths in `motionlib.py`), resized → zoom, changed text → type/word,
  new layer → fade; `dual` keeps Morph with a push/wipe/fade `mc:Fallback` (`transition_xml` `fallback`).
  Applied by `motion.py`; authored entrances/paths are never overwritten.
- **No-Morph gate** (`check_deck.py --compat`, auto from motion.json; `--nomorph-render DIR`): ERROR on Morph left
  in safe mode and on Morph-authored shared moves with no classic replacement; renders a Morph-stripped copy and
  compares each slide's end state with the intended render; WARN on overlapping end-state text. `studio.py build`
  runs it when the deck sets compat.
- Example: `examples/phin-multistyle/build-safe.sh` (`make_deck.py safe`). Tests: `tests/test_compat.py`.

## 5.0.0
v4 made decks look designed, but with one motion (Morph) and five packs that a starter deck showed as recolours of
one layout. v5 widens the motion vocabulary to what professional motion decks actually use (research: slidewppt.vn
decks, Office transition/animation XML, ManimGX, the "anatomy" idea), makes each style a layout grammar, and adds
hand-built architecture films with an editable fallback. Backward compatible: v4 specs build unchanged.

- **Creativity rule** (SKILL.md, styles.md §0): no default template or motion; `## Style choice` (with a rejected
  pack) and `## Motion vocabulary` (≥ 2 techniques beyond Morph/fade) in art-direction.md, checked by Gate 3.
- **Motion library** (`motionlib.py`, `references/motion-library.md`): 49 transitions (core, p14, p15 prstTrans,
  morph) with fallbacks; effects entrance (fade, fly, drop, float, wipe, split, zoom, wheel, type, word), emphasis
  (pulse, grow, spin, teeter, blink), exit, motion paths and orbits, loops, click groups, triggers, media.
  Player support table and fallbacks for PowerPoint 365/2019/2016, Google Slides, Keynote, LibreOffice.
- **Engine** (`build_deck.py`): slide `transition` and `style` (per-chapter packs, `style_overrides`); shape `anim`
  (staggered over component parts), `link`; `poly` freeforms; `video` with poster and duration; line arrows;
  explicit transition ms wins over template durations (`motion.py`).
- **Styles**: five new packs with their own grammar docs (`references/styles/`): kinetic-type, blueprint,
  swiss-blue (the white-blue option), neo-brutal, retro-terminal; three palette-only packs in
  `assets/styles-experimental/`. All fonts OFL with Vietnamese coverage checked. New grounds `blueprint`, `mesh`,
  `scanline` (`make_assets.py`).
- **Diagram films** (`diagram_video.py`, `references/diagram-video.md`): nodes and edges JSON → MP4 (pop in, draw
  on, flowing dots, breathing lit node) + poster + an editable shape fragment with native effects; ManimGX route.
- **Verification**: `check_deck.py` effect census, ERROR on effects targeting missing shapes or duplicate ids, WARN on
  motion monotony; `verify_motion.py` (LibreOffice round trip of authored effects); `preview_motion.py` (a labelled
  SIMULATION MP4 from per-shape sprites and the parsed timing: entrances, emphasis, paths, iterate, morph
  interpolation, transition approximations).
- **Example** `examples/phin-multistyle` (18 slides, six styles, CC photos, drawn phin, diagram film).
- Tests: `tests/test_motionlib_v5.py`.

## 4.0.0
v3 blocked decks that were wrong (unsourced, unlicensed, the wrong instrument, over time, a photo held still) but did
not teach or produce decks that look designed, and its own `check_deck.py` failed the accepted ca trù deck
(slides 31→32, a deliberate question beat). v4 adds the craft: a system the engine applies, a signature, components
that move well, an asset kit, a reference to compare against, and audits recalibrated so the reference passes and the
failure modes still fail. It also stops being a heritage-and-product skill: seven kinds of deck share one pipeline.

- **The one idea** (SKILL.md): a motion deck is a short film shot on one set: the set (ground, chrome, grid, type),
  one signature object, and scenes built as camera moves. Size the job first (Short / Standard / Long).
- **Style packs** (`assets/styles/`): lacquer-heritage (measured from the reference deck), noir-product,
  paper-editorial, boardroom-data, studio-pop. OFL fonts with full Vietnamese coverage, contrast checked on renders.
  `references/styles.md`; `assets/reference/styles-gallery.jpg`.
- **Engine** (`build_deck.py`, backward compatible with v3 specs): `style`, chrome on every slide with `{n}`,
  `{total}`, `{title}`, `{source}`; text `role`s; grid `col`; material grounds generated from the style; shadows;
  image duotone/grayscale/brightness/radius/border; groups; components `heading`, `card`, `stat`, `screen`,
  `timeline`, `bars`, `list`, `quote` that keyframes drive by setting their keys; per-slide `ms`, `morph`,
  `keep_timing` written to motion.json; scene ids in slide names. Layout warnings measured with the real font
  (`typeset.py`): overflow, a word wider than its box, an orphan word, outside the safe area, texts that overlap,
  text running over a card or screen. Quiet text as a mixed solid colour (`fade`), because LibreOffice misplaces
  Vietnamese marks on transparent text.
- **One-command loop** (`studio.py`): `new` (style + starter deck), `build` (build → motion → pack → render → audit
  with renders, a new render folder each round), `compare` (your contact sheet above the reference), `fonts`.
- **Asset kit** (`make_assets.py`): grounds (lacquer with crackle, noir, paper, clean grid, halftone, flat), foil
  finishes for SVG/PNG drawings, SVG layers for Morph assembly, photo grading with mono/colour pairs, glows,
  patterns. `fetch_fonts.py` gets static TTFs from the npm registry or google/fonts.
- **Audits**: `craft_audit.py` (no persistent system is an error; overflow into other text, safe area, type scale,
  flat grounds and contrast are warnings). `visual_audit.py` allows a hold beat (at most one per scene and 10% of
  transitions), reads scene ids from slide names, ignores pictures parked off-slide, and treats fact IDs on slides as a
  warning (sources trace through the storyboard `source` column and the notes). The reference deck passes
  (`tests/test_audit.py`, `MOTION_REF_DECK`); the Genshin pattern (6 still pairs in 22, two in one scene) still fails.
- **Gates**: kinds heritage, product, pitch, business, education, event, other with their own research and imagery
  minimums; Gate 3 needs a style, a signature and a compare sheet; Gate 4 reads fact IDs from a source column and
  reports repeated layout names as a note; per-slide `ms` in deck.json counts as planned durations.
- **References**: new `craft.md` (the system with numbers, composition library, anti-patterns, the critic's pass),
  `genres.md`, `styles.md`, `reference-bar.md`; motion-grammar gains camera language, byChar/byWord, bar grow,
  reveal, screen tour and hold; build-engine, art-direction, qa-checklist, storyboard-template updated.
- **Examples** built with the engine, each with `make_deck.py`, `build.sh` and a committed contact sheet:
  `catru-mini` (7 keyframes rebuilt from the reference's own drawings), `product-launch` (11, a fictional product with
  drawn screens), `data-story` (11, a fictional chain with illustrative numbers).
- **Tests**: 70+ pytest checks (`tests/`).
- `setup.sh`: numpy, cairosvg (or rsvg-convert) and fontconfig are required.

## 3.0.0
A 23-slide Genshin Impact deck passed every v2 gate. Research, credits and the fan-concept disclaimer were real. The pictures were not: about 7 screenshots, one of them dominant on 6 slides, keyframe pairs inside a scene that only slid the words (the photo did not move), one text-left/image-right template for 12 slides, one font family (Noto Sans and Noto Sans Display), a near-uniform navy, slogan lines. Gates 2–4 checked that files and `!!` names were *declared*. They did not measure whether anything changed.

`scripts/visual_audit.py` is the measurement. `check_deck.py` runs it on a `.pptx`, an unpacked deck, or a PDF (rendered pages and embedded images, so a reviewer can audit an output that has no project folder). `gates.py` runs the same rules on the storyboard and the art-direction file. Failure is an error, not a printout.

Thresholds, and why they are not the round examples in the request (a global "30% of pixels or 10% of width on every shared `!!` pair" rule also fails the two decks the owner already accepted):

| Check | Threshold | Why |
|---|---|---|
| Subject photo stuck | box or crop ≥ 10% of slide width, **or** a shared `!!` shape ≥ 6% of slide width, **or** ≥ 30% of pixels changed (200×112, channel delta > 24) | 10% on every shape false-fails ca trù list-reveal callouts at 6.2% and the neko cat grow at 9.8%. 30% on every pair false-fails dark fields and counters. The Genshin failure is a photo that does not move. |
| Image reuse | dominant subject on at most 4 slides; on a photo-led deck (≥ 40% of slides have a subject photo) distinct images ≥ consecutive runs | Ca trù's most reused photo is on exactly 4 slides. Neko is 18% subject photos, so the cat's circular close (3 slides, 2 runs) is not "one screenshot stretched across the talk". Genshin is 100% photo-led, 7 images, 8 runs, and one hash on 6 slides. |
| Layout | each storyboard `layout` value in at most 3 scenes; on a finished deck the editorial-left template (section kicker, left title, bottom caption, image right or full-bleed) in at most 3 scenes | The column rule was prose only. Coarser buckets ("text left" vs "full bleed") also flag the accepted decks. This template is the one Genshin repeats on 5 scenes. |
| Art direction | ≥ 2 font families; every palette hex sourced on its own line; colour arc names ≥ 2 hexes and ≥ 2 scene ids | Counting any 3 hexes and any 2 font files let a default navy theme through. Noto Sans Display folds into Noto Sans. Office defaults do not count. |
| Content | on-slide words average ≥ 8; ≥ 40% of rows cite a fact ID from `facts.md` | The word floor does **not** fail the Genshin PDF (22.7 words/slide of slogans). Fact IDs do, when `facts.md` is in play. A bare audit of the accepted decks does not invent fact IDs they never stamped on the slide. |
| Scarcity | `asset_scarcity: <reason>` in the brief | Real-photo minimum becomes 0. The deck may shrink to the distinct visuals (at least 2 scenes). Illustrations from the TRUE list, labelled as illustrations, with CREDITS rows. Never one screenshot across a scene. |

Calibration (`check_deck.py` / `visual_audit.py`):

- `other.pdf` (23 slides) **FAIL**. Image `1f4144af` on slides 1, 2, 3, 19, 20, 21. 7 distinct < 8 runs. Editorial-left on 5 scenes (slides 4–6, 9, 10–12, 13–15, 16–18). Keyframe slides 4→5 (box 5%, pixels 23%), 13→14 (6%, 29.7%), 14→15 (5%, 28%), 16→17 (5%, 17%), 17→18 (6%, 20%), 22→23 (0%, 14%). One font family. Words average 22.7.
- `NEKO_CORE_motion.pptx` (34 slides) **PASS**. 6/34 subject photos, max reuse 3, editorial-left on 0 scenes, cat on slides 2→3 moves 9.8%, words average 59.5, JetBrains Mono + Be Vietnam Pro. Pre-existing warnings only (lonely `!!` names, font not installed on the audit machine).
- `NEKO_CORE_CaTru_motion.pptx` (48 slides) **FAIL on one real defect**. 22/48 subject photos, 9 distinct = 9 runs, max reuse 4 (slides 37–40), editorial-left on 0 scenes, words average 49.9, Josefin Sans + Cormorant. Slides 31→32 share screenshot `52e451c0` with a 1.3% shape move and 2.8% pixel change: the two frames are nearly the same slide. The 6% floor is what reports it. Pairs at 6.2% pass. The threshold was not lowered to hide this.

Research and credits gates are unchanged.

## 2.0.0
Rebuilt after the user's review: "other models and agents don't research images, sources and assets, so the result lacks
visual richness and pull."
- **Hard gates** (`scripts/gates.py`, Gates 0–6): no slide before brief, research, assets, art direction and storyboard pass.
- **Research protocol** and **cultural visual accuracy** references: source ladder, tags, do-not-say list, TRUE/WRONG motif lists,
  object anatomy checklist, user-media audit.
- **Asset sourcing with licences**: `fetch_commons.py` (Commons + Openverse, quoted and ASCII-folded queries, NC/ND excluded, keep → CREDITS),
  `contact_sheet.py`, `cutout.py`, `inpaint_text.py`, `video_frames.py`.
- **Harness-independent build**: `build_deck.py` (JSON spec with keyframe inheritance) + `ooxml.py`; no dependency on a managed slide service.
- **motion.py rewrite**: lxml-based stripping (no stacked or empty AlternateContent), `@blink`, `keep_timing`, motion.json
  (found in the unpacked folder, deck/ or WORK), duplicate-name warnings; idempotent.
- **Timing by words**: `words_budget.py` plan/measure; script_docx shares its counting rules.
- **QA**: `check_deck.py`, `check_fonts.py` (Vietnamese coverage, variable-font warning), `render.sh`; QA checklist reference.
- **Delivery**: `deliver.py` (static fonts + install README + CREDITS + zip).
- Case studies (ca trù heritage, neko-core product), harness adapters (Claude Code, Codex, Cursor, Grok Bot, plain LLM), companion skills.

## 1.0.0
First version: Morph naming conventions, motion.py, roles.py, finish_dedupe.py, script_docx.py, make_assets_example.py; it relied on
a managed slide workflow for building and had no research or asset rules.
