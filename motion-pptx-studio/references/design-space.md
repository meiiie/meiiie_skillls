# Design space (v5.5): route the deck, then invent it

v5.4 and earlier shipped eleven style packs and a deck "used" one. Two test decks showed what that costs:
a SpaceX deck in heritage collage (aged paper and a script accent on launch hardware shot at night), and
decks that passed every gate while looking like their pack's starter. v5.5 splits the decision in two:

1. **Routing** (a gate): which *families* fit this subject, audience, tone and these pictures, and which are
   wrong, with a reason a person could argue with.
2. **The genome**: the deck's own decisions, axis by axis, starting from the routed family and changing
   whatever this subject asks for. The family is a starting point; the genome is the design.

## 1. Routing (`route.py`, `studio.py route`)

```bash
python3 $S/route.py WORK                          # auto: highest fit that is not rejected
python3 $S/route.py WORK --choose swiss-blue --why "the story is a timeline of numbers, a white sheet carries it"
python3 $S/studio.py route WORK --apply           # also copies the chosen family into design/style.json (tagged "route")
```

What it reads:
- **Subject**: `brief.md` topic, audience and tone (3× weight) plus `research/facts.md` and `assets/CREDITS.md`
  (support), matched against bilingual domain lexicons (aerospace, technology, software, engineering,
  heritage, history, culture, craft, food, travel, education, youth, business, finance, science, event…).
  The deck kind adds a prior (heritage → heritage/history/culture; product → technology…).
- **Tone**: the brief's `tone:` line (and the user's quoted words): technical, cinematic, warm, nostalgic,
  playful, serious, calm, energetic, elegant, raw…
- **Material, measured from the files** (not their names): share of dark / bright / saturated / muted /
  warm / cool pictures, cut-outs (alpha), archival prints (low saturation, lit, warm or neutral cast) and
  pre-1970 dates in file names or credits.

How it scores each family (`assets/styles*/<pack>.json` → `"fit"`) and each direction in
`design/directions.json` (`"family"`, `"domains"`, `"tones"`): fit = 0.45 subject + 0.20 tone + 0.35 material.
A candidate is **rejected** when one of its `avoid` domains is a leading domain of the deck (weight ≥ 0.5),
with the family's own written reason, or when fit < 0.40 (the weakest axis is named).

`design/routing.md` is the record: the subject profile with the words that produced it, the measured
material, a ranked table with verdicts, every rejection with its reason, and the decision (auto or
`--choose` with an 8+ word reason; a rejected family cannot be chosen).

**Gate 3 rows** (FAIL): routing exists and parses; a direction was chosen; ≥ 1 rejection with a reason; the
deck's style family (style.json `route`/`extends`/`name`, per-slide and chapter styles) is not a rejected one.
(WARN): routing is current (brief/assets fingerprint), the deck uses the chosen family, fit ≥ 0.60.

When the router is wrong, fix its inputs, not its output: say the tone in `brief.md`, add the real pictures,
or write a direction with its own `domains`/`tones`. If you `--choose`, the reason is in the record.

### Writing a `fit` block for a new family
```json
"fit": {"domains": {"heritage": 1.0, "travel": 0.6}, "tones": ["warm", "nostalgic", "calm"],
        "material": {"archival": 1.0, "warm": 0.6, "muted": 0.5},
        "avoid": [{"domain": "aerospace", "reason": "aged paper and a script accent read as nostalgia; launch hardware shot cold against night sky needs precision and scale"}]}
```
Every `avoid` needs a reason a designer would sign; it is printed in the decision and in gate 3.

## 2. The genome (`design/genome.json` → `genome.py compile`)

`python3 $S/genome.py axes` lists the axes. Each one is a decision with a `why`:

| Axis | Decide | Examples from the v5.5 samples |
|---|---|---|
| `route` | the family it starts from | noir-product (SpaceX), heritage-collage (Đồ Sơn) |
| `light` | where the deck lives in luminance | night stage / daylight paper |
| `palette` | ground, ink, accent(s); `from_image` samples the hook photo | ground from a long-exposure landing; sea green of Hòn Dáu |
| `type` | display / text / label faces, `ratio` (scale), `body`, case, tracking | Saira Condensed caps 1.5 / Cormorant 1.333 |
| `grid` | columns, margins, gutter | 12 cols, 0.65 in / 10 cols, 1.0 in (a third left empty) |
| `material` | ground kind (noir, paper, clean, flat, lacquer, halftone, gradient), grain, stains, fibres, vignette | grain 0.05 / stains 0.5 fibres 0.6 |
| `chrome` | page-number corner, rule (top/bottom/left), running head | tr + left rule / bl + top rule |
| `motion` | tempo, stagger, transitions, construction verbs | 1000 ms push/cut / 1500 ms wipe/fade |
| `image` | how pictures enter | full-bleed plates / framed postcards |
| `signature` | the one object | the first stage / the Hòn Dáu lighthouse |
| `arc`, `motifs`, `layers` | colour arc by scene, textures, Morph layers | written into art-direction.md |

`compile` writes `design/style.json` (the engine's style; `"route"` keeps the family for gate 3) and
`design/art-direction.md` (marked `<!-- genome -->`; it is regenerated while that marker is there, so edit the
genome). Guarantees: ink ≥ 7:1, muted ≥ 5:1, the kicker colour ≥ 4.6:1 and accents ≥ 3:1 — measured against the
ground **as it renders** (the darkest stained/vignetted paper edge, the lightest glowing noir), because a paper
ground's corners, where page numbers and sources sit, are much darker than its base colour; a type scale of
≤ 8 sizes from the ratio.

Layouts are not in the genome: they are invented per slide in `make_deck.py` from the grid, with the
composition written in the storyboard. The families' `references/styles/<pack>.md` grammars are examples of
compositions that suited that family, not a menu.

## 3. Proving decks differ (`genome.py distance`)

```bash
python3 $S/genome.py distance A/deck/final.pptx B/deck/final.pptx --renders-a A/renders/final-1 --renders-b B/renders/final-1 --json out.json
```
Compares fonts, size scale, entrance/emphasis techniques, transitions, layout occupancy (4×6 grid of text and
picture boxes) and the rendered colour histogram; 0 = the same deck, 1 = nothing shared. Two decks from the
skill on different subjects should land well above 0.5; two chapters of one deck that are meant to differ,
above 0.3.

## 4. Audit: what used to force fixed output (v5.4) and what replaced it

| Hard-coded in v5.4 | v5.5 |
|---|---|
| `studio.py new --style <pack>` required: the pack was chosen before research and assets | `--style` optional; `studio.py route` after the assets; a rejected family is refused (`--force` to override) |
| 11 packs as the design answer; nothing said a pack was wrong for a subject | packs are families with `fit`/`avoid`; routing gate; genome re-decides every axis |
| Gate 3 rewarded naming a pack and a rejected pack (template compliance) | gate 3 checks the routing decision and that the deck is not in a rejected family; the art direction is compiled from the genome |
| Gate 3 motion vocabulary counted preset names | the genome's construction verbs and their Manim names count (`diagram`, `anatomy`, `manim`, stretch, wipe…) |
| `directions.py` composition was one of six enums | free-text composition, a `sketch` hint, a `family` per direction (directions are routing candidates) |
| Contrast checked against the base colour | contrast held against the rendered ground |
| No construction verbs: diagrams faded or flew in; the wheel was simulated as a fade | `construct` component, stretch/indicate presets, sweep simulation (`construction-motion.md`) |
| `studio.py compare` defaulted to the ca trù reference | (v5.4) by kind; v5.5 decks are compared with `genome.py distance` too |
