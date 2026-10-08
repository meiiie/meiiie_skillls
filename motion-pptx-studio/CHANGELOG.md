# Changelog

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
