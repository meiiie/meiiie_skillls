---
name: motion-pptx-studio
description: Build cinematic, professionally designed PowerPoint decks with real native motion — Morph keyframe scenes plus a full library of transitions (push, curtains, fall over, cover…), entrances, emphasis loops, motion paths, letter-by-letter type, click triggers, hyperlink menus and looping video diagrams — plus a timed speaker script, for any kind of talk — product launches and demos, startup and contest pitches, business reviews and data stories, lectures and explainers, events and campaigns, culture and heritage. Use it whenever someone wants a presentation, slide deck or .pptx that must look designed rather than templated ("motion pptx", "Morph", "slide động", "thuyết trình chuyên nghiệp", "pitch deck", "ấn tượng", a contest, broadcast or investor deck), even if they never say Morph. Routes itself: before design it analyses the topic, audience, tone and the real pictures, scores candidate directions, rejects mismatches in writing (gated), then compiles a per-deck genome (palette from the photos, type scale, grid, material, chrome, motion grammar); eleven style families are starting points, not templates. Construction-based diagrams (Anatomy/Manim rules: part-by-part assembly, camera moves, state transforms) are built natively and editable with Vietnamese-ready fonts, a deck engine with components, hand-built signature films (Anatomy isometric machines and ManimGX scenes, embedded as video plus an editable native poster), Codex image generation for labelled AI textures and plates, a three-direction anti-template phase, an architecture-diagram film maker with an editable fallback, a labelled motion-preview simulator, an asset kit, research and licence gates, layout and craft audits, and worked examples measured against an accepted reference deck.
---

# Motion PPTX Studio

Version 5.5.0. Python 3.9+ (`python3`), LibreOffice and poppler; Node 20.10+ and Chrome for Anatomy films, ManimGX for Manim films, Codex CLI for generated assets (each optional, each with a documented fallback); works in any harness with a shell (Claude Code, Codex,
Cursor, Grok Bot, a plain LLM with tools: `references/harness-adapters.md`).

The standard comes from a real user and is kept word for word:

> "Tìm hiểu kỹ văn hoá Ca Trù để tìm và tải backgroud sao cho phù hợp nhé và đảm bảo độ chính xác tuyệt đối"
> "với các pptx chuyên nghiệp tôi đều thấy họ có nhiều cảnh nhiều motion, có khi nhiều slide để phục vụ cho một motion hoàn chỉnh, từng frame và mọi thứ, cần làm chuyên nghiệp nhé"
> "Trông chưa ổn lắm, cần chọn font cần tài nguyên asset, mọi thứ khác nhé" · "Ca Trù phải để tiếng Việt chứ nhỉ ?"

The accepted result of that standard is the reference deck in `assets/reference/` (48 slides, measured in
`references/reference-bar.md`). Look at it before you design anything. Every deck this skill makes should
hold up next to it.

## Skill is a floor, not a ceiling

This skill was distilled from a longer prompt by its author, Darren. In turning that prompt into rules,
its creative core went missing: a v5.2 test deck passed every gate and still looked like a template (one
dark-blue style, text left / photo right thirty times, no visual you would remember). The intent of the
original prompt, restated here (paraphrase, not a verbatim quote; the original text is not in this repo):

> - Use **Codex CLI image generation** to diversify the assets instead of living on whatever stock exists.
> - Use **ManimGX** (https://manimgx.academa.ai/) and **Anatomy** (https://skills.wheresryan.sh/anatomy)
>   to hand-build the architecture animations, with **no AI clichés** (books, scales, lightbulbs…).
> - **Do not lean on the skill too much**: it hard-codes a template, and a template is what we are escaping.
> - Be **creative**: appeal, craft, tech-art. The deck should make people ask how it was made.

So: the gates are the minimum that keeps a deck honest (facts, licences, a render that works) plus a
creative floor (three directions considered, two hand-built signature moments, a style shift on long
decks, no repeated split layout). Everything else in this file is advice that reproduced good decks, not
a recipe. When the subject asks for something the skill does not describe, build it; when a habit here
makes the deck duller, drop it and write why in `notes/`. Passing gates is where the work starts.

## The one idea

**A motion deck is a short film shot on one set.**

1. **The set** stays the same on every slide: a material ground, a chrome (frame, page number, source
   line), a grid, a type system. A style pack holds it; the engine applies it. Morph can only show change
   against things that stay still.
2. **The signature** is one object that belongs to the subject — the instrument's three strings, the
   product's cursor, the headline number — living in the margin on most slides and becoming the hero at
   the hook, the turn and the close.
3. **The camera** moves inside each scene: 3–5 keyframes where the composition really changes (assemble,
   push in, walk the highlight, grow the bars, reveal the list), never one slide per idea with the words
   swapped.

Two ways this fails, both seen in delivered decks: **generic** (a default theme, stock icons, slogans, one
template on every scene) and **static** (Morph as a page turn, one screenshot held still while the words
change). The fix for both is the same: a real system, a real signature, real objects of the subject, and
scenes built as camera moves. `references/craft.md` gives the numbers.

**Creativity rule (v5.5).** There is no default template and no default motion. The deck is **routed** from
its subject, audience, tone and pictures (`route.py`: mismatched families are rejected with a written reason
and a deck built in one fails gate 3), and then **invented**: a genome (`references/design-space.md`) decides
each axis for this deck — palette sampled from its own photos, type pairing and ratio, grid, material, chrome
corners, composition per slide, motion grammar and one signature. A family is where the genome starts, never
the answer. Diagrams are **constructed**, not faded in (`references/construction-motion.md`): base → structure
→ mechanism → controls → one lit subject, strokes drawn, solids grown from what they sit on, labels written,
the camera travels the drawing and parts change state through Morph. If two decks from this skill would look
the same with the colours swapped, the design is not done (`genome.py distance`).

## Size it first

Tell the user the size and a time estimate before any other work.

| Size | Slides | Effort | Do |
|---|---|---|---|
| Short | 8–15 (≤ 5 min talk) | 1–2 h | build it |
| Standard | 20–35 (5–12 min) | 3–6 h | say so, then build it |
| Long | 40+ (12+ min), or several decks | 6 h+ | propose a Standard version that keeps the core; build the Long one only when the user chooses it |

Have a rendered sample (Gate 3) within the first hour, and tell the user when a phase runs past twice its share.

## Non-negotiable rules

1. **No deck before Gate 4.** Brief, research, assets, design and storyboard come first. The sample deck of Gate 3 is the exception: it is how the design is chosen.
2. **Every claim traces to `research/facts.md`; every image to `assets/CREDITS.md`.** No source, no slide. Fact IDs live in the storyboard's `source` column and the notes, never on the slide; a short human source line in the chrome ("Nguồn: 20-F 2025") is welcome on data slides. AI-generated images are labelled AI-generated in CREDITS (and on the slide when they could pass for a photo).
3. **Look at every image and every render yourself.** Titles, tags, file names and passing checks are not evidence.
4. **One system, one signature, many camera moves.** A scene is 3–5 keyframes; a shared subject image must move (box or crop ≥ 10% of the width, or a shared `!!` shape ≥ 6%, or ≥ 30% of pixels); one hold beat per scene at most; some `!!` layer on ≥ 60% of slides. `check_deck.py` measures all of it.
5. **On-slide language follows the audience** (Vietnamese topic, Vietnamese slides), including text inside photos.
6. **Budget speech in words, not seconds per slide** (130 wpm). Measure the script before delivery.
7. **Never overstate.** Status (finished, design-only, planned), results, licences and awards exactly as sourced; illustrative numbers and drawn screens say so.
8. **Ask the user at most once, at the start** (time limit, language, honest status, style if it matters). Otherwise choose a documented default in `brief.md` and tell them.
9. **At least two signature moments** (`references/signature-moments.md`): hand-built animated diagrams of the subject's own mechanism (Anatomy or Manim), embedded as video with an editable poster. Never a stock metaphor.
10. **Never game a check.** Do not edit thresholds, create placeholder files or copy rows to pass. The reference deck must pass every audit (`tests/test_audit.py`); a check that fails it is a wrong check, a deck that only passes checks is not done.

## Setup (once per machine)
```bash
bash scripts/setup.sh            # check: python-pptx lxml Pillow numpy fonttools python-docx cairosvg, LibreOffice, poppler
bash scripts/setup.sh --install  # install what is missing (pip --user, falls back to a venv)
```
Set `S=<absolute path of this skill>/scripts` and `WORK=<project folder>`. Every tool explains itself with `-h`.

## The pipeline

```bash
python3 $S/studio.py new WORK --kind heritage|product|pitch|business|company-profile|education|event|other --title "…" --fonts
# v5.5: no --style. After the brief and the assets: route, then write the genome
python3 $S/studio.py route WORK [--apply]       # → design/routing.md (ranked, rejections with reasons, decision)
python3 $S/genome.py compile WORK/design/genome.json   # → design/style.json + design/art-direction.md
python3 $S/gates.py check WORK --gate N        # N = 0..6; FAIL means stop and do the missing work
python3 $S/gates.py check WORK --upto 6        # all gates, gate 5 for every rendered group
```
Gates have two kinds of row (v5.3). **FAIL** is hard: facts (every fact row sourced, every number on a slide
traces to a fact ID), licences (every image credited, AI images labelled), render integrity (fonts, renders,
check_deck, the films) and the creative floor (3 directions, 2 signature moments, style shift on 20+ slides,
no text-left/photo-right on 4+ slides). **WARN** is advisory: fact counts, domains, kept/candidate counts,
scene and keyframe-run counts, word averages, anchor, colour arc, samples. A WARN never stops you.

### Phase 0 · Brief → Gate 0
Fill `WORK/brief.md`: topic, audience, kind, size, talk_minutes, on-slide language, forbidden items, **honest
status**, presenter, reference talk, user media, style, and **the user's own words verbatim**. Read any video,
form or repo the user gave first.
Ask where it will play: if not surely PowerPoint 365/2019+ (venue PC with 2016, Google Slides, Keynote,
LibreOffice), set `"compat": "safe"` (no Morph, classic motion rebuilt) or `"dual"` (Morph + classic fallback);
see `motion-library.md` §4b. Read the playbook for the kind in `references/genres.md`.

### Phase 1 · Research → Gate 1 (`research-protocol.md`, `cultural-visual-accuracy.md`)
`research/facts.md`: sourced facts, tagged `[verified]` / `[secondary]` / `[claim]` / `[disputed]` / `[uncertain]`,
with a **do-not-say list**. `research/accuracy.md`: the TRUE objects and motifs, the WRONG associations, an anatomy
checklist (heritage, product, education), and an audit of the user's media. Depth scales with the kind
(`genres.md`: heritage 15 facts from 3 domains … event 6 from 2). A reference talk → `research/lessons.md`.

### Phase 2 · Assets → Gate 2 (`asset-sourcing.md`)
Real, licensed images (`fetch_commons.py search/keep` writes CREDITS; keep fixes EXIF rotation, MPO and size),
about twice as many looked at as kept, rejected ones listed. **Second source: generated assets**
(`gen_assets_codex.py`, asset-sourcing §6b): textures, abstract backgrounds, generic object renders and scene
plates from Codex image gen, linted against clichés, logos, real people and fake documents, labelled
AI-generated in CREDITS with a prompt sidecar. No Codex → `make_assets.py` / drawn / `asset_scarcity`. Then make the deck's own materials with `make_assets.py`: `ground` (lacquer, noir, paper,
clean, halftone), `foil` (an SVG drawing of a TRUE object in gold, silver, ink, chalk, neon…), `layers` (one PNG per
moving part on one canvas), `photo` (duotone/sepia/mono + colour pair), `pattern`, `glow`. No openly licensed
imagery → illustrate from the TRUE list (labelled) or set `asset_scarcity` and shrink the deck.

### Phase 3 · Art direction → Gate 3 (`design-space.md`, `construction-motion.md`, `art-directions.md`, `craft.md`, `styles.md`, `reference-bar.md`)
- **Route first (v5.5, gate)**: `python3 $S/route.py WORK` (or `studio.py route WORK`) reads brief.md (topic,
  audience, tone, kind), facts and CREDITS, and MEASURES the pictures (luminance, saturation, warm/cool, old
  prints, cut-outs, pre-1970 dates). Every family and every direction in `design/directions.json` is scored
  (0.45 subject + 0.20 tone + 0.35 material) and rejected with a written reason when it is wrong for the
  subject (heritage collage for aerospace, a noir product stage for a heritage town…) or fits < 0.40.
  `design/routing.md` records the ranking and the decision; `--choose X --why "…"` overrides with a reason and
  refuses a rejected family. Gate 3 FAILS without routing, or when the deck's style is a rejected family.
- **Genome (v5.5)**: write `design/genome.json` (`genome.py axes` lists the axes; `references/design-space.md`),
  starting from the routed family and re-deciding every axis for THIS deck with a reason: `palette.from_image`
  samples the hook photo, contrast is enforced against the ground as it renders (stained paper edges, glowing
  noir), the type scale comes from a ratio (≤ 8 sizes), chrome corners, grid, material and motion grammar are
  chosen. `genome.py compile` writes `design/style.json` and `design/art-direction.md` from it.
- **Three directions first (anti-template)**: sketch THREE genuinely different art directions (free-text
  composition, `family`, ground, palette, type, motion, signature visual) as thumbnails
  (`python3 $S/directions.py WORK` → `design/directions.jpg` + `directions.md`), choose one, write why.
  20+ slides: plan scene-level style shifts (a second direction for named chapters). Gate 3 fails without it.
- **Signature moments**: pick the two or three mechanisms worth a hand-built film and write them in
  `design/signature-moments.md` (`references/signature-moments.md`: Anatomy machines via
  `setup_anatomy.sh` + `anatomy_film.py`, Manim scenes via ManimGX). Gate 4 checks the plan, gate 6 the films.
- **Style**: the compiled genome is the style (fonts must pass `check_fonts.py --lang vi`). Packs in
  `assets/styles/` are families to start from; never ship one unchanged.
- **Construction diagrams (v5.5)**: at least one mechanism, map or object per deck is a `construct` component
  (`references/construction-motion.md`): parts with `layer`/`on`, built in order with Create/Grow/Write verbs,
  then travelled with `camera` and changed with `states` across Morph slides; exactly one lit part per frame.
- **Signature**: write it under `## Signature` in `art-direction.md` — what it is, where it rests, what it
  becomes at the hook, the turn and the close, which `!!` parts it has.
- **Colour arc**: two grounds or a bloom, written as `S1-S4 #0E0A07 → S6-S11 #F1E4C8`.
- **Sample and compare**: turn the starter into your direction, `studio.py build WORK --group sample`, copy
  title and body renders to `design/samples/`, then `studio.py compare WORK WORK/renders/sample-1` and answer
  its questions. Change direction now, not after 40 slides.
- **Style choice and motion vocabulary**: `## Style choice` (chosen, per chapter, and ≥ 1 rejected with the
  reason) and `## Motion vocabulary` (≥ 2 techniques beyond Morph/fade) in `art-direction.md`; Gate 3 checks both.

### Phase 4 · Storyboard → Gate 4 (`storyboard-template.md`, `motion-grammar.md`, `speech-craft.md`)
```bash
python3 $S/words_budget.py plan --minutes 6 --slides 34     # → ~754 words total, ~22 per slide
```
`WORK/storyboard.md`: one row per slide — scene, keyframe role, composition (`layout`), `!!` layers, a real visual,
on-slide text, `source` (fact IDs), words, morph ms. 8+ scenes for talks of 5 min or more; at least half of the scenes
are runs of 3+ keyframes (a gate 4 habit, WARN; v5.4: one number everywhere), each a recipe from `motion-grammar.md` §4; distinct visuals ≥ scenes, none on more than 4 rows;
an anchor phrase on 3 slides; a colour arc; a circular close (reusing the opening photo there: `"bookend": true` on the slide). Keep each row on one line (gate 4 fails a broken
table loudly). Rows with a number on the slide must cite a fact ID; the signature-moment slides use
`film:assets/film/<name>.mp4` as their visual; a `style` column names the direction of each scene.

### Phase 5 · Build in groups of 2–4 scenes → Gate 5 (`build-engine.md`, `qa-checklist.md`)
Write `WORK/deck.json` against the style: components (`heading`, `card`, `stat`, `screen`, `timeline`, `bars`,
`list`, `quote`, and v5.4's magazine set `callout`, `swatch`, `photogrid`, `nodemap`, v5.5's `construct`), roles instead of sizes, `col` instead of x/w, keyframes as `"from": "prev"` + `set`, `"scene"`,
`"ms"`, `"morph"`, `"transition"` and `"style"` on the slides, `"anim"` (effects) and `"link"` on shapes, `poly`
and `video` shapes for drawn objects and diagram films (`diagram_video.py`, `references/diagram-video.md`). When parts must line up (strings on a neck, a cursor that becomes the screen),
generate deck.json from a `make_deck.py`, as the examples do.
```bash
python3 $S/studio.py build WORK --group g1         # only the slides of g1 ("group" on slides or "groups" in deck.json), full-deck page numbers
python3 $S/studio.py compare WORK WORK/renders/g1-1 [--ref FOLDER] [--layout side]
python3 $S/gates.py check WORK --gate 5 --group g1 --deck WORK/deck/preview-g1.pptx
python3 $S/verify_motion.py WORK/deck/preview-g1.pptx          # LibreOffice round trip: authored vs imported effects
python3 $S/preview_motion.py WORK/deck/preview-g1.pptx --out WORK/preview/g1-SIMULATION.mp4 [--max-seconds 60] [--lang vi]   # optional; keep it out of renders/
# before Phase 6: the whole deck, checked as one (deck-wide layout repetition, reuse, variety, legibility)
python3 $S/studio.py build WORK                    # no --group = all slides -> deck/unpacked, preview-all.pptx, renders/all-N
python3 $S/gates.py check WORK --gate 5 --group all   # or --upto 5 (adds the whole-deck check; prints a SUMMARY; --stop-on-fail)
```
A group build works in `deck/unpacked-<group>` and never touches `deck/unpacked`, which always holds the last
full build. `--max-seconds` fits every slide into the budget (holds shrink first, then transitions; `--cut` is the
old hard stop); `--lang vi` labels the frames in Vietnamese.
Fix every layout warning first, then look: contact sheet, the comparison, every changed slide, 4× crops where
things meet (`craft.md` §12). Write defects in `notes/g1.md`, fix them in one pass, rebuild into `g1-2`.
Naming: `!!name` persists (Morph pairs it), `@fade|float|wipe<N>-label` enters, `@blink<N>-label` loops; any
effect can instead be written as `"anim"` on the shape. The preview MP4 is a simulation and must be labelled so;
it never replaces playing the deck in PowerPoint.

### Phase 6 · Finish and deliver → Gate 6 (`delivery.md`)
```bash
python3 $S/studio.py final WORK      # full build -> finish_dedupe -> clean -> pack deck/final.pptx -> renders/final-N -> check
# (by hand: finish_dedupe.py WORK/deck/unpacked; ooxml.py clean/pack WORK/deck/unpacked WORK/deck/final.pptx; render.sh)
python3 $S/words_budget.py measure WORK/deck/final.pptx --target 6:00
python3 $S/deliver.py WORK --deck WORK/deck/final.pptx --name Project_Motion --title "Kịch bản thuyết trình"
python3 $S/gates.py check WORK --gate 6
```
`deliver/` = `.pptx` + speaker-script `.docx` + `fonts/` (static TTF, OFL, install README) + `CREDITS.md` + `.zip`.

## Craft rules (short form; `references/craft.md` has the reasons and numbers)

- **Ground is a material**, never a flat fill; a second ground or a bloom marks the turn.
- **Chrome never moves**: frame or rule, page number, source line, at the same place on every slide.
- **One signature**, several `!!` parts, parked off-slide between appearances, paying off in the close.
- **Text on a photo sits on something**: a colour band or chip, a gradient scrim, or a toned picture; capitals are
  for headlines, kickers and labels, never for a paragraph (`legibility_audit.py`: caps body = ERROR, a missing
  scrim = WARN, ERROR in `heritage-collage`).
- **Type roles only**: kicker 11–13 tracked caps · title 40–56, ≤ 8 words, the conclusion · body 15–17, ≤ 3 lines ·
  display/numeral for one word or one number. Two or three families; a chapter pack inherits them and may add one display face. No orphan word on a title's last line.
- **One lit accent per frame**; contrast 4.5:1 for anything read; quiet text as a mixed solid colour (`fade`).
- **Composition varies, the system does not**: pick from the composition library; one focal point; a third of the frame empty. check_deck fingerprints the rendered geometry: text left + photo right on 4+ slides fails.
- **Words**: the slide shows, the speaker tells. ≤ 30 words per keyframe; numbers with unit, period and source.
- **Imagery**: real → drawn from the TRUE list → nothing. Photos graded into the palette; drawn objects in one finish; screens in a device with a shadow.
- **Detail belongs to something**, ends on something, and rewards a 4× look; nothing floats.
- **Motion**: one primary move per transition; 1300 ms default, 2000 for assemblies, blooms and the close; ≤ 3 entrances, only for new information.
- **Players**: Morph needs PowerPoint 365/2019+; for 2016, Google Slides, Keynote or an unknown venue PC build with `"compat": "safe"` or `"dual"` (`compat.py`, gate in `check_deck.py`).
- **Type scale**: one deck scale of ≤ 10 sizes (e.g. 10 12 14 18 24 36 48 64 96 150); snap every explicit `size` to it. `check_deck.py` prints the scale it found.
- **Signature films**: Anatomy figures dense and bright (≥ 120 solids, ≥ 70 % of the frame width, edges ≥ 4.5:1; `film.json` audit); the film slide's `bg` is the film's card colour; no label under a video (`check_deck.py` errors; `--renders` checks the edge colour). See `references/signature-moments.md` §2 and §4.
- **Vocabulary**: Morph for change inside a scene, a real transition between scenes (push, cover, curtains…), 2–4 signature effects repeated with intent; no deck that is only Morph (`check_deck.py` warns).

## Final message to the user (always)
Files delivered; slide and scene count; measured speaking time against the target; fonts to install;
**what must be checked in PowerPoint 365** (Morph, Office 2013 transitions, triggers, links and video autoplay; LibreOffice renders are static and `preview_motion.py` is only a simulation);
decisions taken without asking; claims left out because they could not be verified; the audit's remaining warnings
and why they are deliberate.

## Reference map

| File | Read it when |
|---|---|
| `references/design-space.md` + `scripts/route.py`, `scripts/genome.py` | Phase 3, first: routing (fit scores, rejections, the gate), the genome axes, compiling a deck's own style, measuring that two decks really differ |
| `references/construction-motion.md` + `scripts/construct.py` | Phases 3–5: Anatomy/Manim rules as native motion — part model, build order, verbs, camera, states, one lit part |
| `references/signature-moments.md` | Phases 3–5: choosing mechanisms, the Anatomy recipe, the Manim recipe, video + editable poster on the slide, fallback, banned clichés |
| `references/art-directions.md` + `scripts/directions.py` | Phase 3: three directions as thumbnails, choosing, style shifts, geometry variety |
| `references/craft.md` | before Phase 3 and before every review: the set, signature, grid, type, colour, compositions, words, imagery, depth, data, anti-patterns, the critic's pass |
| `references/reference-bar.md` + `assets/reference/` | before Phase 3: what the accepted deck does, measured; how to compare |
| `references/genres.md` | Phase 0: arc, signature, evidence, research depth and traps for each kind of deck |
| `references/styles.md` + `references/styles/<pack>.md` | Phase 3: the creativity rule, the eleven families (genome starting points, each with a `fit` block) and each one's layout grammar and signature motion, changing one, a style from a brand board, all keys |
| `references/research-protocol.md` | Phase 1: source ladder, tagging, do-not-say list, product research |
| `references/cultural-visual-accuracy.md` | any cultural or heritage topic: true and wrong motifs, anatomy, user-media audit |
| `references/asset-sourcing.md` | Phase 2: where to search, query tips, licences, keep/reject, Codex generated assets (§6b), third-party logos, the asset kit |
| `references/art-direction.md` | Phase 3: style, signature, fonts, palette, motifs, layered objects, colour arc, samples |
| `references/motion-grammar.md` | Phases 4–5: camera language, Morph pairing, keyframe recipes, durations, entrances |
| `references/motion-library.md` | Phases 3–5: every transition and effect, recipes beyond Morph, player support and fallbacks, verify |
| `references/diagram-video.md` | architecture, process, maths: diagram films with an editable fallback, Manim/ManimGX |
| `references/storyboard-template.md` | Phase 4: table format, scene structure, worked example |
| `references/speech-craft.md` | Phases 1/4: hook, anchor, pauses, circular close, word budget |
| `references/build-engine.md` | Phase 5: deck.json, components, generator scripts, OOXML editing, gotchas |
| `references/qa-checklist.md` | every render: layout warnings, audit, visual, accuracy, motion, language, licence, timing |
| `references/pro-craft.md` + `scripts/variety_audit.py` | Phases 3–5: the four pro gaps (animation variety, composition, flavour, overall variety) as rules: motion verb per scene, cut grammar, eight composition systems, three planes and parallax, sub-styles; measured by `check_deck.py --variety` |
| `references/delivery.md` | Phase 6: package, fonts, credits, the hand-off message |
| `references/harness-adapters.md` | installing the skill; harness differences; weak-model mode |
| `examples/catru-mini`, `examples/product-launch`, `examples/data-story`, `examples/phin-multistyle`, `examples/earth-fall` | before building: the same bar in nine styles (phin: six styles, one per chapter, each with its own grammar), each with `make_deck.py`, `build.sh` and a contact sheet |
| `examples/case-catru-heritage.md`, `examples/case-neko-core-product.md` | the two delivered decks and every correction the user made |

Companion skills (optional, same repo): `heritage-visual-research` (Phases 1–2 alone) and `presentation-speech-craft`
(the script and the talk). Anthropic's `pptx` and `docx` skills are optional alternatives, never required.
