# Storyboard (Gate 4)
- target: TODO min · budget: TODO words (python3 words_budget.py plan --minutes M --slides N)
- anchor: "TODO phrase" (on 3 slides: setup / middle / end)
- colour arc: TODO (replace this whole line; e.g. S1-S4 #0E0A07 → S6-S11 #F1E4C8 — two hexes, two scene spans)
- circular close: TODO (last scene returns to the opening image; reusing the opening photo there needs `"bookend": true` on that slide in deck.json)

One row per SLIDE. Several rows = one motion (keyframes). `visual` names a kept asset file,
`drawn:<motif>` from art-direction, or `frame:<file>` marked OK in the media audit.
`layers` lists the !! names that persist/move (the signature too). `layout` names the composition
(references/craft.md §6). `source` holds the fact IDs behind the slide (they stay off the slide).
`words` = spoken-word budget for that slide. `style` names the direction/pack of the scene (a 20+ slide deck
changes it at least once). `visual` may be `film:assets/film/<name>.mp4` for a signature moment. Keep every
row on ONE line (a newline inside a cell breaks the table; gate 4 fails it); write a literal | as \|.

| # | scene | keyframe role | style | layout | layers | visual | on-slide text | source | words | morph ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S1 Hook | K1 one string in darkness | TODO | void | !!str2 | drawn:string | — | — | 18 | 1500 |
