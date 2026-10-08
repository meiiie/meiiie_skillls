# Case study B: Neko Core product pitch from a GitHub repo (34 slides, 10 scenes)

**Brief.** "Use the skill to make a deck about https://github.com/meiiie/neko-core": a local-first coding agent in the terminal
(one binary, any model, "asks before it acts"). About 6 minutes, Vietnamese on slides with English technical terms; the presenter
introduces his own team.

## Research (product version of Gate 1)
- `neko_facts.md`: README, CHANGELOG, releases (GitHub API), LICENSING/NOTICE/TRADEMARKS, docs/process, the site and the company
  site, tagged [verified] / [claim-in-README] / [verified-in-CHANGELOG] / [uncertain]. 55 fact rows.
- **Do-not-overstate list (§10)**, enforced on every slide:
  - the HardMix-12 result is a **single run** by the owner (auto 12/12 vs --yolo 11/12, glm-5.3), always with its caveat;
  - no stars, forks or downloads;
  - no "won" for the hackathon origin;
  - "sdk/ is Apache-2.0", but no separately published SDK;
  - auto mode is an **allow-list + seatbelts**, not an LLM classifier;
  - the OS sandbox is opt-in;
  - offline only with a local model;
  - Anthropic only via an API key;
  - the old social-preview image still says MIT (the licence is AGPL-3.0 or commercial), so don't use it.
- `brand_notes.md`: the palette is fixed (#0A0B0D / #F4F5F7 / one amber #F0A030), with no purple and no AI glow; the pixel logo is used as-is, never
  redrawn; the cat sits **beside** the logo.

## Assets
Official logo PNG, one **real** TUI screenshot (labelled "ảnh thật · v0.11.5, trước 1.0"), the Excel demo poster from the repo,
a hand-built neutral grid background, and the site mascot keyed out of its background. The mascot is AI-made by the owner and
credited as such. Terminal sessions drawn on slides are labelled "Minh hoạ".

## Art direction
JetBrains Mono (headings, terminal, labels: the brand's display face is monospace) + Be Vietnam Pro (Vietnamese body).
JetBrains Mono lacks ✓, so the deck writes "ok". Template headings broke mid-word in mono, so those layouts were rebuilt.
Lesson at delivery: the fonts were **variable** TTFs, and PowerPoint showed wrong weights. Ship static instances.

## Motion
- Hero objects: the block `!!cursor` hides a tiny `!!cat`. On slide 2 the cursor collapses to an underscore and the cat grows out of it (1.6 s).
  On the last slide the cat shrinks back into the cursor (2 s) and the cursor blinks forever (`@blink`).
- Scenes: S1 Boot (cursor → title → presenter) · S2 Problem (muted counter 1→2→3: "VỘI / KHOÁ / MẤT") · anchor #1
  "Hỏi trước, rồi mới làm." · S3 Meet Neko (**bloom**: amber returns, 2 s) · S4 Harness (agent loop ring, process line) · S5 Governed
  action (anchor #2; four permission modes as a highlight walk) · S6 Any model (11 routes, counter) · S7 Durable + extensible (real
  screenshot, demo poster) · S8 Evidence (two donuts + caveat slide) and shipping cadence · S9 Open & honest (licence; honest limits) ·
  S10 Journey (timeline walk, no "won") · S11 Close (anchor #3 + install line → title again → boot again).
- motion.json `dur` = {2: 1600, 40: 1600, 7: 2000, 3: 1400, 43: 1400, 50: 2000}, keyed by file numbers after `sequence`.
- The blink was hand-made and erased each time motion.py rebuilt timing. v2 fixes this: `@blink<N>-label` names, or `keep_timing`.

## QA findings worth remembering
Ghost words too bright (dimmed to #22252B); dark text on a dark circle (contrast); a chart's embedded workbook still held template
numbers (updated it so "Edit Data" keeps 16/78); `a:spcBef` in the wrong order inside `a:pPr` (29 hits, reordered); the
Morph pair audit showed 0 duplicates and 0 kind mismatches.

## Result
1.56 MB, 34 slides, one Morph per slide, script 1088 words = **8:28** against a ~6:00 plan (scenes 5 and 8 were the trim candidates).
With `words_budget.py plan --minutes 6 --slides 34` the budget would have been ~754 words (~22 per slide) from the start.

## What to copy
For products, the honesty list matters as much as the design: say what is finished, label illustrations, keep caveats on the slide,
and use the brand's own assets untouched. One playful hero object (cursor ↔ cat) carries the whole deck.
