# Routing (v5.6) — written by route.py; re-run after the brief or the kept assets change

- kind: business; about: economy 1.00 (cảng (head), sản lượng (topic), container (topic), cảng (audience)), business 0.85 (kind prior), finance 0.35 (kind prior)
- mentioned only (no evidence in the topic or the user's words, capped at 0.35): none
- declared domains: {'economy': 1.0, 'business': 0.85} (declared in brief.md (- domains:)); lexicon cross-check: economy 1.00, business 0.71, finance 0.43
- tone: analytical, calm, precise; excluded (negated): ['không cổ động']
- material: 0 kept images (0 photos, 0 generated); dark 0%, bright 0%, saturated 0%, muted 0%, warm 0%, cool 0%, cut-outs 0%, archival 0%

| rank | candidate | fit | subject | tone | material | verdict |
|---|---|---|---|---|---|---|
| 1 | boardroom-data | 0.77 | 1.00 | 1.00 | 0.35 | **chosen** |
| 2 | direction:A | 0.77 | 1.00 | 1.00 | 0.35 | fits |
| 3 | swiss-blue | 0.72 | 0.88 | 1.00 | 0.35 | fits |
| 4 | paper-editorial | 0.61 | 0.64 | 1.00 | 0.35 | fits |
| 5 | direction:B | 0.61 | 0.64 | 1.00 | 0.35 | fits |
| 6 | noir-product | 0.39 | 0.19 | 0.89 | 0.35 | REJECTED: fit 0.39 < 0.40, weakest on subject (0.19): its subjects ['technology', 'aerospace', 'engineering'] do not cover what this deck is about ['economy', 'business'] |
| 7 | blueprint | 0.38 | 0.00 | 1.00 | 0.50 | REJECTED: fit 0.38 < 0.40, weakest on subject (0.00): its subjects ['engineering', 'aerospace', 'technology'] do not cover what this deck is about ['economy', 'business'] |
| 8 | direction:C | 0.38 | 0.00 | 1.00 | 0.50 | REJECTED: fit 0.38 < 0.40, weakest on subject (0.00): its subjects ['engineering', 'aerospace', 'technology'] do not cover what this deck is about ['economy', 'business'] |
| 9 | glass-tech | 0.28 | 0.35 | 0.00 | 0.35 | REJECTED: fit 0.28 < 0.40, weakest on tone (0.00): its register (bold, cinematic) is far from this deck's (analytical, calm, precise) |
| 10 | retro-terminal | 0.27 | 0.00 | 0.74 | 0.35 | REJECTED: a hacker-terminal register speaks to the wrong audience; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 11 | lacquer-heritage | 0.22 | 0.00 | 0.51 | 0.35 | REJECTED: gold-on-lacquer ceremony makes a data briefing look like a ritual object; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 12 | kinetic-type | 0.19 | 0.14 | 0.00 | 0.35 | REJECTED: a type-only show of one huge word per slide cannot carry many sourced figures; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 13 | heritage-collage | 0.12 | 0.00 | 0.00 | 0.35 | REJECTED: collage softness, tilted prints and a script accent make figures look approximate; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 14 | neo-brutal | 0.12 | 0.00 | 0.00 | 0.35 | REJECTED: sticker shadows and lime blocks make inflation and debt look like a joke; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 15 | studio-pop | 0.12 | 0.00 | 0.00 | 0.35 | REJECTED: cartoon outlines and sun yellow trivialise inflation and debt; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 16 | desktop-os | 0.12 | 0.00 | 0.00 | 0.35 | REJECTED: a fictional desktop makes official statistics look like a game; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |
| 17 | papercut-collage | 0.12 | 0.00 | 0.00 | 0.35 | REJECTED: craft paper and torn edges make figures look homemade; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one |

## Decision
- chosen: boardroom-data (auto)
- why: highest fit 0.77: covers economy, business (subject 1.00), register near analytical, calm, precise (tone 1.00), no kept pictures yet (material 0.35)
- runners-up: direction:A, swiss-blue, paper-editorial
- next: the chosen family is where the genome STARTS (references/design-space.md); the deck still invents its own palette from its pictures, its layouts and its motion grammar.
- if the subject analysis above is wrong, declare it ("- domains: economy, finance" in brief.md or design/subject.json) and re-run; never edit the scores.
