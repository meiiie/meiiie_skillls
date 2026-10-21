# Storyboard (Phase 4 → Gate 4)

The storyboard is where research, assets, motion and speech meet. Write it fully **before** building;
the gate checks it.

## 1. Header (top of `WORK/storyboard.md`)
```
- target: 6 min · budget: 754 words   (python3 $S/words_budget.py plan --minutes 6 --slides 34)
- anchor: "Hỏi trước, rồi mới làm." (on 3 slides: setup / middle / end)
- colour arc: S1-S4 #0E0A07 → S5-S8 #F1E4C8 (two backgrounds, two scene spans; "muted then bloom" alone fails)
- circular close: slides 33–34 = title and boot keyframes again; the cat shrinks back into the cursor
  (v5.4: a close that reuses the opening photo declares it: `"bookend": true` on that slide in deck.json. At most
  2 bookend slides; check_deck then does not count the return as a reused image. Any other reuse still fails.)
```

## 2. Table: one row per SLIDE
| # | scene | keyframe role | layout | layers | visual | on-slide text | source | words | morph ms |
|---|---|---|---|---|---|---|---|---|---|
| 1 | S1 Hook | K1 one string in darkness | void | !!str1-3 | drawn:string | Nghe bằng cả trái tim. | — | 17 | 1300 |
| 2 | S1 Hook | K2 three strings + small photo | split | !!str1-3 !!photo | 01_catru_trio_clean.jpg | Hà Nội · biểu diễn ca trù | 2.1 | 10 | 1300 |
| 3 | S1 Hook | K3 photo bloom + title | full-bleed | !!photo !!title | 01_catru_trio_clean.jpg | Ca trù | 1.1 | 19 | 2000 |
Rules checked by `gates.py`:
- `scene` starts with a scene ID (S1, S2…). Rows with the same ID form one keyframe run.
- At least half of the scenes have 3 or more rows (gate 4 habit; the same number as SKILL.md and pro-craft.md). At least 8 scenes for talks of 5 minutes or longer. With `asset_scarcity` set in the brief, the minimum drops to the number of distinct visuals (never below 2).
- `layers` names the `!!` objects (at most 10% of rows without any). Consecutive keyframes that share a subject image must actually move it: box or crop ≥ 10% of slide width, or another shared `!!` shape ≥ 6%, or the renders differ by ≥ 30% of pixels. `check_deck.py` errors otherwise.
- `visual` is a kept file in `assets/`, `drawn:<motif>` from art-direction, or `frame:<file>` graded OK in the media audit. Never empty. Distinct visuals ≥ the number of scenes. No file or `drawn:` motif is named on more than 4 rows (a 5-slide run cannot keep one image on every frame).
- `layout` names the composition (craft.md §6: void, hero, split, full-bleed, numeral, walk, rail, screen, chart, reveal, quote, book, close). A value used in more than 3 scenes is reported as a note: one system, varied compositions.
- `on-slide text` averages at least 8 words per row. At least 40% of rows cite a fact ID defined in `research/facts.md` (a source id such as `(S1)` or a table id such as `1.1`) in the `source` column: the claim traces to a source; the ID stays off the slide.
- `words` is the spoken budget for that slide (0 allowed for a silent keyframe). The total stays within the budget.
- The anchor phrase appears in 3 or more rows.
- `colour arc` names at least 2 background hexes and at least 2 scene ids (`S1-S4 #0E0A07 → S6-S11 #F1E4C8`).

## 3. A dependable scene structure for a 5–15 minute pitch
| Scene | Purpose | Typical recipe |
|---|---|---|
| S1 Hook | a sense or a question, not a title slide | assemble / one object in darkness |
| S2 Problem | why it matters (muted colours) | counter 1→2→3, or a big number |
| S3 Context | the true objects, people and places (heritage) or how it works (product) | highlight walk / zoom to detail |
| S4 Turn | anchor phrase #1, the hero appears | colour bloom |
| S5–S8 The work | what you made, demonstrated with real screens and frames | book, timeline walk, push-in |
| S9 Proof | evidence with its caveat | counter / donut + caveat line |
| S10 Honest status | finished vs planned | timeline with "done" and "next" |
| S11 Close | anchor phrase #3, call to action | circular close |
| S12 Credits | sources and image credits | static, small type |
Use the user's chapters if they have them (the ca trù video had Chapter 1 history and Chapter 2 traditional
music, so the deck mirrored them).

## 4. Variety rules
- Keep one system (ground, chrome, grid, type roles, signature) and vary the composition between scenes; a layout name in more than 3 scenes is a note at Gate 4, the editorial-left template in more than 3 scenes is an error on the built deck.
- At most **one** text-only slide in the whole deck.
- Real visuals: photos or screens in at least half the scenes. Drawn motifs fill the rest, never stock icons.
- Team or user frames: inside a framed "screen" at ≤45% of the slide width, never as a cultural close-up.

## 5. From storyboard to build
Copy `layers`, `visual` and text into `WORK/deck.json` (see build-engine.md), one scene id per slide (`"scene": "S3"`).
Put the planned durations on the slides (`"ms"`, `"morph"`); `build_deck.py` writes motion.json. Write the speaker notes per
slide inside the spec (`"notes"`), already within the words budget, with the fact IDs the slide relies on.
