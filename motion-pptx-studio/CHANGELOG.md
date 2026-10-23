# Changelog

## 6.10.0 (2026-10-22, iterate round 4, not pushed)
Round 3 (v6.9: giấc ngủ / áo dài / điện mặt trời = 6.5 / 7.5 / 7.0). Root cause: gates did not block delivery. The
sleep deck failed art_check (no bleed, no cut-out, no hero) and was delivered anyway without saying so.
- build.py: a failed film/art gate renames the deck NAME.UNFINISHED.pptx (no deliverable until it passes).
- art_check: a full-bleed film counts as a chapter's bleed (abstract topics with few photos).

## 6.9.0 (2026-10-22, iterate round 3, not pushed)
Round 2 (v6.8: kinh tế / vòng tuần hoàn nước / VF 3 = 7.5 / 7.5 / 8.0). Root causes: default bar/line charts, a film
still or isometric scene reused on neighbour slides, three-column text lists.
- New principle data-as-object (numbers drawn as their thing; default charts and lists at most once per chapter;
  never reuse a picture).
- art_check: FAIL on near-duplicate neighbour slides (perceptual hash, sources pages exempt).

## 6.8.0 (2026-10-22, iterate round 2, not pushed)
Round 1 (v6.7, AI chips / Thăng Long / rừng ngập mặn: 6.5 / 7.0 / 6.5). Root cause: one-type-scale fixed 7 sizes up to
132 pt and a fixed kicker+title strip on every slide; films fixed to a 64:27 band. Every deck became a header template.
- one-type-scale rewritten as a ratio scale (200-400 pt heroes, 15-25x range, no fixed title strip).
- Films are full-bleed 16:9 by default (manim_kit ds.FILM_ASPECT); band is the exception.
- art-direction: editorial illustrations fill the frame (no rows of clip-art icons).
- art_check: FAIL when more than a third of the slides are small top-left headlines; each chapter needs a hero-scale
  slide; cut-outs count only at >= 12 % of the slide or bleeding. build_deck defaults display 120 / numeral 260 pt.

## 6.7.0 (2026-10-22)
- film_check: hard 3-D depth >= 0.10 for non-Anatomy films; Anatomy fails < 80 parts, edges < 4.5:1, mid-film flow < 60 %.
- art_check photo-reading gates wired into build.py: text over busy photo areas, chapter without full-bleed or
  cut-out ("chapter" key in deck.json).

## 6.6.0 (2026-10-22, proposal, not pushed)
**Why.** Codex v6.5 coffee deck ~7/10. Darren: "better but not artistic yet; weakest at image layout". The study is
in /workspace/research-v66/FINDINGS.md.
### Added
- principle photo-arrangement: the photo comes first, and its arrangement follows its job: full-bleed, cut-out,
  bleed crop, pair, sequence or mask.
- scripts/photo_layout.py: analyze (saliency subject box, quiet cells, text tone), crop (subject on a third,
  detail, --focus), cutout (rembg with GrabCut fallback), mask (circle, arch, band, pill, poly).
### Changed
- film_check.py: a combined rule replaces a raw motion floor: motion >= 5, alive >= 35 %, fill >= 30 % (Anatomy
  50 %), and FAIL when depth < 0.10 AND fill < 70 % (a flat move over a sparse frame); a 2-D-only film that fills
  the frame only gets a WARN.
- film-language: at least one 3-D camera move per ManimGX film. anatomy-first: hero shot, camera move, a visible
  flowing medium.
- composition-range: art density at 1x, a bold full-bleed or a dark dramatic slide per chapter, no small icon in
  an empty field. photo-treatment rewritten (light falloff for type, material edges, honest edits).
- surface-and-depth: material visible at 1x. SKILL.md 6.6 (60 lines).

## 6.5.0 (2026-10-22, proposal, not pushed)
**Why.** Codex v6.4 retest (coffee) ~6.5/10: process followed, art not. Its log shows it opened only 2 of 19
principle files (manimgx-first, anatomy-first) and decided materials, directions and films from the SKILL.md
one-liners. Full study: /workspace/research-v65/FINDINGS.md.
### Added
- principles film-language (2+ camera moves over a running process), composition-range (5-7 named compositions,
  rhythm, recolour test), photo-treatment (crop, grade, edge, scale contrast).
- scripts/art_check.py (flat-ground and layout-run warnings from renders + pptx), scripts/embed_fonts.py
  (PowerPoint-style EOT .fntdata embedding).
### Changed
- SKILL.md: read every bracketed principle at its step; directions differ in composition; art_check after build;
  compare image in look-then-fix; font embedding at delivery.
- film_check.py: motion floor 1 -> 5 and a new "alive" share (>= 50 % of seconds change).
- three-directions (recolour test, no single colour-argument board function), surface-and-depth (visible at 2x,
  chapters differ in layers), anatomy-first (process after assembly), look-then-fix (score beside the yardstick).

## 6.4.0 (2026-10-22)
**Why.** Darren: decks still lack artistic surfaces (textured, grainy "nhám" grounds). We studied
the SpaceX deck, the Trái Đất deck and 28 slidewppt.vn templates, and set them against weak decks:
the Codex coffee deck, the ChatGPT Cây đa deck and the mít test. The full study, with annotated
boards, is in /workspace/art-research (not shipped).

What the study found:
- Great decks look like made objects: one material per chapter, light falloff, grain, and
  textured panels. Weak decks are flat screens.
- Great decks shift temperature between chapters. Each uses one accent with one job.
- Their type scale reaches 15-25x, with three voices. Their crops are bold and the negative space
  points somewhere. Their photos are graded or cut out.
- The rhythm changes on every slide.
- slidewppt is meaningful when the surface is the subject (a case-file kraft, a scroll and ink
  wash). It is cliché when the texture is decoration (gingham, stickers, glow frames, grunge).
  Its typography is weak.

### Added
- **scripts/surface.py:** procedural grounds tinted to any palette. Layers:
  - tone: mottle, paper tooth, fibres, laid lines;
  - light: light pools, directional falloff, vignette;
  - pattern: halftone of the light field, riso misregistration;
  - midtone grain and dither.
  It also has a `photo` command (duotone, lift/gamma/gain, grain). Both work from the CLI and as a
  Python API.
- **principles/surface-and-depth.md:** material per chapter, texture on every surface including
  panels, calm areas under text, bake to JPEG, and five starting recipes.
- **principles/art-analysis.md:** study references for why and how, never copy. Annotated
  GOOD/WEAK/DECOR boards and a fixed question list, re-run on the contact sheet.

### Fixed
- A recipe dict in deck.json `"grounds"` imported make_assets.py, which was deleted in 6.0. It now
  builds with surface.py, and references/deck-json.md documents the keys.
- build_deck.py's closing hint named the removed studio.py and check_deck.py. It now names build.py.

### Changed
- SKILL.md 6.4: step 3 names one material per chapter. The index gains art-analysis and
  surface-and-depth; paired rows keep it at 60 lines.
- art-direction.md: points to surface-and-depth.

## 6.3.0 (2026-10-22)
**Why.** Darren asked for real variety and for films that work everywhere. A Codex CLI test of 6.2
("Lịch sử cà phê Việt Nam", 26 slides, gpt-6.1-sol) followed step 0 correctly: it smoke-tested
ManimGX and Anatomy and made 2 ManimGX films and 1 Anatomy film. The problems were elsewhere:
- it picked one direction, the coffee cliché (cream, roast brown, leaf green);
- the board was drawn after the build;
- the films were chart animations (a growing bar, a timeline) with no camera moves.

### Added
- **principles/three-directions.md:** three radically different directions every time, from the
  topic, audience and imagery. Write the cliché down and reject it, reject anything that looks
  like examples/, board all three, then pick one with reasons.
- **principles/web-film.md:** a portable tier for ChatGPT web and locked sandboxes. The order is
  ManimGX/Anatomy, then web-film, then canvas_film, then native Morph. The tier is always
  reported, and the motion bar is the same in every tier.
- **scripts/web_film.mjs + scripts/web/smoke.html:** a page that defines
  `window.frame(t)` becomes an mp4 through headless Chrome and ffmpeg. The 3 s smoke film
  renders in about 8 s.
- **build.py:** a soft WARN when the work folder has no directions.md.

### Changed
- **SKILL.md:** step 0 names web-film as the reported next tier; step 3 requires three
  directions; the films step lists the tiers; the index has the new rows.
- **film-is-the-core:** the tiers, plus "a growing bar is a chart animation, not a signature film".
- **manimgx-first:** points to the web-film tiers.

## 6.2.0 (2026-10-22)
Anatomy is now as strict as ManimGX.

### Added
- **principles/anatomy-first.md:**
  - when Anatomy is required (any structure or process: at least one Anatomy film per deck);
  - install with `setup_anatomy.sh`, plus the GitHub-tarball route for sandboxes with no git access;
  - the smoke test, how anatomy_film.py works, its flags and the figure recipe;
  - the rule: stop and report, never skip silently.
- **scripts/anatomy/smoke.mjs:** a 10-line figure that renders a 3-second test film.

### Changed
- **SKILL.md:** step 0 now sets up ManimGX AND Anatomy; the films step, index and description
  are updated.
- **film-is-the-core:** Anatomy is required for any structure or process.
- **manimgx-first:** points to anatomy-first.
- **setup_anatomy.sh:** documents the tarball route. Its failure message now says stop and report,
  and no longer points to the deleted v5 diagram_video.py.
- **anatomy_film.py:** dead links to the v5 signature-moments.md now point to anatomy-first.

## 6.1.0 (2026-10-22)
**Why.** In a ChatGPT test the agent built a 30-slide deck with no films and delivered it as a PDF.
v6.0 treated Manim as optional and gave no install path. The agent ran `pip install manimgx` on
Python 3.11 and got "no matching distribution" (ManimGX needs Python 3.13 or newer), so it quietly
fell back.

### Added
- **principles/manimgx-first.md:**
  - links to the docs and to llms.txt;
  - three install routes (venv with Python 3.13+, uv tool, or the standalone offline binary);
  - a 10-line smoke scene and the render flags;
  - the rule: install and smoke-test first, and if ManimGX is impossible, stop and report it.
- **Anatomy docs link** for isometric machine films.

### Changed
- **ManimGX is mandatory.** This is now in SKILL.md (a new step 0, step 5, the index), in
  film-is-the-core and in the film_check message.
- **canvas_film and native motion are reported fallbacks only.** They need the user to have been
  told and the reason in NOTES.md.
- **Deliverable:** a .pptx with the mp4 films embedded plus the mp4s alongside. Never a PDF only.

## 6.0.0 (2026-10-22)
Rewritten as a compressed skill: principles first, tools second.

### Changed
- **SKILL.md** is now about 50 lines: a 5-step workflow and an index.
- **Principles:** 13 short files (10–20 lines each) replace the long rulebook.
- **Films are mandatory.** Each film is the deck's core and has a route fallback: Manim, then
  the pure-Python canvas (`canvas_film.py`), then the Anatomy isometric machine.
- **Native fallbacks** stay editable.
- **One-command build:** `scripts/build.py` runs build_deck → motion → pack → render →
  `film_check`. It writes each render to a new `renders/rN` folder.

### Added
- **principles/art-direction.md:** chapter palettes, a background on every slide, a picture
  for every hero number, type roles, one motif, and a board critiqued before building.
- **principles/examples-are-a-yardstick-not-a-mold.md.**
- **Examples:**
  - `examples/reference-trai-dat` (the yardstick contact sheet);
  - `examples/space-buu-dien-anh-sang-v2` (art direction, board and contacts).
- **references/manimgx-quirks.md:** Typst resolves fonts by typographic family plus weight.

### Removed
- Gates, the design genome, the router and the test suites from v5.x.
- **House style:**
  - `DEFAULT_PALETTE` is now neutral greyscale, and `DEFAULT_FONTS` is DejaVu.
  - The film fonts come from each deck's `ds.py` and fall back to ManimGX-shipped faces.
  - `assets/styles/` is gone. The old paper-editorial pack now lives in
    `examples/flagship-khi-ap/` as `style-pack.optional-illustration.json`, labelled as an
    optional illustration only.

## 6.11
- Independent critic: scripts/critic.sh + references/critic-prompt.md run a FRESH codex session against
  examples/yardsticks (Trái Đất ref + Hội An / VF3 8/10 decks + flagship, credited); principle independent-critic;
  step 7 is now a mandatory redesign loop on the critic's 5 weakest slides. Self-scores no longer count.
- Real photos: art_check.real_photo() (colour count + flat-area share) tells photographs from renders/illustrations;
  PHOTOS gate fails a deck with fewer than max(3, n/5) photo slides unless deck.json "no_photo_reason".
  BLEED now needs a real photo or full-bleed film. Tested on 10 past decks (tmdt/giấc ngủ 0, Hội An 11, VF3 10).
- abstract-illustration principle: photo of the physical thing, macro, collage, type, ManimGX 3-D stills; default
  isometric mint blocks banned.
- Relaxed: CUTOUT-per-chapter is a note, not a fail (it produced tiny quota cut-outs).

## 6.12
- Critic orders 8 slides (was 5), one deck-wide order applied to every slide, and a repetition list (motif/layout on >3 slides). Round 5 showed a 5-slide loop leaves split-layout sameness and repeated motifs.

## 6.13
- sample-chapters: 3 fully rendered sample chapters (one per direction, 4 axes apart); critic.sh --pick writes pick.md
  (winner or hybrid + binding style sheet); style.md binds the deck. No critic -> ask the user, never self-pick.
- Critic adds a per-slide rhythm map, an isometric/pastel-block list and a card-number list.
- art_check ISO: share of edges at +-30 deg on renders/illustrations; >= 4 slides fails, fewer is a LOOK note
  (heuristic: catches tmdt/laikep/Hội An blocks, misses some native-shape scenes).
- data-as-object: no number on an empty card.

## 6.14
- Hard gate: build.py refuses > 8-slide decks without a critic.sh-signed pick.md; critic.sh signs its output. Builder must end its turn after samples if the critic cannot start. (R7: 2 of 3 builders self-picked or skipped samples.)

## 6.15
- Samples must differ in photos/crops and layouts, not just palette/type (R8 boards were recolours); the pick critic scores look-alike samples <= 5.
- Sanctioned sandbox route: fresh subagent critic signs pick.md; editing/copying build.py to pass the gate is forbidden (R8 battrang did that).

## 6.16
- photo-library-first: per-chapter credited photo library (8-15 candidates, licence+url, jobs) BEFORE samples/slides;
  abstract concepts mapped to physical things; samples use different picks.
- scripts/photo_library.py board|check; build.py runs check for decks > 8 slides (no library = UNFINISHED).
  Check calibrated on R9: VF3 (8.5) passes; Mekong (6/26 photo slides) and Dữ liệu (7/26) fail.

## 6.17
- stagecraft principle (Duarte glance test + sparkline, Reynolds signal/noise + picture superiority, Apple one number per slide, OpenPresentation optical craft). Critic rhythm map adds a glance pass/fail per slide and lists decorative photos and multi-number slides.
- (late) photo_library check: VARIETY gate (>= 4 distinct subjects per chapter via subject-word clusters; <= 1/3 look-alike pairs). All 3 R10 libraries fail (2-3 subjects in their worst chapters).
- art_check CARDS gate: card = no real photo/film/cut-out/type >= 150 pt (sources slide excluded); fail > max(2, n/6). Calibrated: R10 three decks fail (5/10/9 cards), r9-vf3b (4) and r8-battrang (4) pass; Hội An r4 fails at 5 (borderline). 250 pt cutoff rejected (fails battrang).
- abstract-illustration rewritten: three hero types only, diagrams for mechanism, <= 1 app screen. Critic item 7 lists every card with an order.

## 6.18
- concept-art-direction: signature device + one-page treatment before looks; direction A deliberately extreme (Pentagram/Duarte).
- through-line: design/story.md (through-line, arc, one purpose line per slide); deck.json "purpose" required (anim_check).
- per-slide critic: `critic.sh --slides` scores every slide vs Trái Đất + SpaceX yardsticks (examples/yardsticks/1-spacex.jpg added),
  orders a fix for each < 8, CUT/REWORK slides without a purpose or with animation that doesn't serve it; 2-3 loops to median >= 8.5, min >= 7.
- native-keyframes: compat default "safe" (no Morph; Morph pairs rebuilt as classic paths/zooms); every component animated (anim_check.py gate, >= 70 %).
- references/techniques.md + scripts/pptx_fx.py (text_fill_image, mask_picture, parallax_effects, push_in_effects) - all without Morph.
- unity: one image treatment per deck; renders/diagrams in that treatment or not at all.
- CARDS (art_check) and VARIETY (photo_library) downgraded to WARN (gamed in R11); the per-slide critic is the bar.

## 6.19.0 (2026-10-23, stable)
- Persistent art-director critic (R12 root cause: fresh critics re-invented metaphors, ~22 orders/loop, non-existent photos): DECK score + fixed PLAN, <= 5 orders tied to library files, follow-up sees before/after of ordered slides and marks DONE; re-issues undone orders verbatim. Keep the better render; stop when gain < 0.5.
- Stable release. Sample contact sheets built by Codex using only this skill: `samples/r12-sanho.jpg` (coral reef, 8.0), `samples/r9-vf3b.jpg` (VinFast VF3, 8.5), `samples/r13-bachdang.jpg` (Bạch Đằng 1288), `samples/r11-tet.jpg` (Tết).
