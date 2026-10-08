# Storyboard (Phase 4 → Gate 4)

The storyboard is where research, assets, motion and speech meet. Write it fully **before** building;
the gate checks it.

## 1. Header (top of `WORK/storyboard.md`)
```
- target: 6 min · budget: 754 words   (python $S/words_budget.py plan --minutes 6 --slides 34)
- anchor: "Hỏi trước, rồi mới làm." (on 3 slides: setup / middle / end)
- colour arc: S2 slides 4–7 muted (amber removed) → slide 8 bloom 2 s → full colour
- circular close: slides 33–34 = title and boot keyframes again; the cat shrinks back into the cursor
```

## 2. Table: one row per SLIDE
| # | scene | keyframe role | layout | layers | visual | on-slide text | words | morph ms |
|---|---|---|---|---|---|---|---|---|
| 1 | S1 Hook | K1 one string in darkness | void | !!str1-3 | drawn:string | Nghe bằng cả trái tim. | 17 | 1300 |
| 2 | S1 Hook | K2 three strings + small photo | split | !!str1-3 !!photo | 01_catru_trio_clean.jpg | Hà Nội · biểu diễn ca trù | 10 | 1300 |
| 3 | S1 Hook | K3 photo bloom + title | full-bleed | !!photo !!title | 01_catru_trio_clean.jpg | Ca trù | 19 | 2000 |
Rules checked by `gates.py`:
- `scene` starts with a scene ID (S1, S2…). Rows with the same ID form one keyframe run.
- At least 60% of scenes have 3 or more rows. At least 8 scenes for talks of 5 minutes or longer.
- `layers` names the `!!` objects (at most 10% of rows without any).
- `visual` is a kept file in `assets/`, `drawn:<motif>` from art-direction, or `frame:<file>` graded OK in the media audit. Never empty.
- `words` is the spoken budget for that slide (0 allowed for a silent keyframe). The total stays within the budget.
- The anchor phrase appears in 3 or more rows.

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
- Each layout appears in **at most 3 scenes** (repeats *inside* a keyframe run don't count).
- At most **one** text-only slide in the whole deck.
- Real visuals: photos or screens in at least half the scenes. Drawn motifs fill the rest, never stock icons.
- Team or user frames: inside a framed "screen" at ≤45% of the slide width, never as a cultural close-up.

## 5. From storyboard to build
Copy `layers`, `visual` and text into `WORK/deck.json` (see build-engine.md). Put the planned durations into
`WORK/motion.json` (slide file numbers = positions when you use `build_deck.py` without `sequence`). Write the
speaker notes per slide inside the spec (`"notes"`), already within the words budget.
