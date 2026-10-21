# Design space (v5.5, routing v5.6): route the deck, then invent it

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

What it reads (v5.6: the subject is judged by where the words are and how much they weigh, not by any hit):
- **Subject, by zone.** The topic's head (before the first dash, colon or bracket) weighs ×4 for a strong
  term / ×1 for a weak one; the rest of the topic ×2.5 / ×0.5; the user's quoted words ×1.5 / ×0.3; the
  audience ×0.6 / ×0.1. `research/facts.md` adds support normalised by its length and capped (strong ≤ 3,
  weak ≤ 0.6), so a long fact file cannot outvote the topic. `assets/CREDITS.md` is **not** subject
  evidence (a NASA credit on a wafer photo says nothing about the deck). Each domain has STRONG terms
  (kinh tế, lạm phát, Falcon 9, di sản…) and WEAK ones (AI, growth, trade, bank, rocket…). The kind adds a prior.
- **About vs mentioned.** A domain is what the deck is ABOUT when the topic (or the user's words, backed by
  ≥ 2 strong fact terms) carries it AND it has ≥ 25% of the leading domain's weight. Everything else is
  "mentioned" and capped at 0.35, so "làn sóng đầu tư AI" in an economics brief stays a sub-theme.
- **Declared domains win.** `- domains: economy, trade` in brief.md (or `design/subject.json`
  `{"domains": {...}, "why": "..."}`) replaces the lexicon's guess; the lexicon is still printed as a
  cross-check and unknown names are a WARNING. `auto` / template guidance in brackets declares nothing.
- **Tone, by register.** Every tone word is a vector on four axes (energy, warmth, formality, drama):
  serious, analytical, sober and authoritative land next to calm/precise families, not only the word "calm".
  tone fit = mean over the deck's tones of the best cosine to the family's tones. "không …" / "not …" /
  "avoid …" words are excluded; unrecognised words are listed in routing.md.
- **Material, measured from the kept files** (not their names): the files the CREDITS tables list (stopping
  at "Rejected"/"loại"/"candidates" headings), else assets/** minus candidates/, rejected/, _uncertain/,
  raw/, thumbs/, grounds/, cut/, film/, drawn/, samples/, contact sheets. Share of dark / bright / saturated
  / muted / warm / cool pictures, cut-outs, archival prints and pre-1970 dates (URLs and pixel sizes such as
  1965×1474 are not dates).

How it scores each family (`assets/styles*/<pack>.json` → `"fit"`) and each direction in
`design/directions.json` (`"family"`, `"domains"` as a dict or a ranked list, `"tones"`):
fit = 0.45 subject + 0.20 tone + 0.35 material. A candidate is **rejected** when one of its `avoid` domains
is a leading domain the deck is about (or declared), or when fit < 0.40.

**Reasons are composed, never copied.** A subject rejection reads: the family's own `because` clause +
"this deck is about {domain} ({weight}: the words that produced it), which needs {what that domain needs}"
+ a material clash when there is one. A low-fit rejection names the weakest axis with specifics (the family's
subjects vs the deck's, register vs register, or the material). No two rejections in one routing are equal.

`design/routing.md` is the record: about / mentioned-only domains with their evidence and zone, declared
domains, tones recognised and excluded, the measured material, a ranked table with verdicts, every rejection
and the decision (auto, with "highest fit X: covers …, register near …, material …", or `--choose` with an
8+ word reason; a rejected family cannot be chosen).

**Staleness is semantic (v5.6).** routing.json stores a hash per input (brief fields, user's words, facts,
kept images, directions, subject.json). Gate 3 names the inputs that changed and re-decides in memory: the
row stays green when the decision is the same (adding assets/cut/, assets/film/ or a fact does not force a
re-route) and WARNs only when the decision would change.

**Gate 3 rows** (FAIL): routing exists and parses; a direction was chosen; ≥ 1 rejection with a reason; the
deck's style family (style.json `route`/`extends`/`name`, per-slide and chapter styles) is not a rejected one;
v5.6: ≥ 2 rendered samples in design/samples and a design/compare*.jpg.
(WARN): routing is current (semantic, see above), the deck uses the chosen family, fit ≥ 0.60.

When the router is wrong, fix its inputs, not its output: declare `- domains:`, say the tone in `brief.md`,
add the real pictures, or write a direction with its own `domains`/`tones`. If you `--choose`, the reason is in
the record.

### Writing a `fit` block for a new family
```json
"fit": {"domains": {"heritage": 1.0, "travel": 0.6}, "tones": ["warm", "nostalgic", "calm"],
        "material": {"archival": 1.0, "warm": 0.6, "muted": 0.5},
        "avoid": [{"domain": "aerospace", "because": "aged paper and a script accent read as nostalgia"}]}
```
`because` says what the FAMILY does to a subject; route.py adds what the deck is about and what that domain
needs (`DOMAIN_NEEDS`), so one clause serves every deck without becoming a copied template.

## 2. The genome (`design/genome.json` → `genome.py compile`)

`python3 $S/genome.py axes` lists the axes. Each one is a decision with a `why`:

| Axis | Decide | Examples from the v5.5 samples |
|---|---|---|
| `route` | the family it starts from | noir-product (SpaceX), heritage-collage (Đồ Sơn) |
| `light` | where the deck lives in luminance | night stage / daylight paper |
| `palette` | ground, ink, accent(s), optional `lit`; `from_image` samples the hook photo, explicit hexes override it (art-direction.md says which key came from where) | ground from a long-exposure landing; sea green of Hòn Dáu |
| `type` | display / text / label faces, `ratio` (scale), `body`, case, tracking | Saira Condensed caps 1.5 / Cormorant 1.333 |
| `grid` | columns, margins, gutter | 12 cols, 0.65 in / 10 cols, 1.0 in (a third left empty) |
| `material` | ground kind (noir, paper, clean, flat, lacquer, halftone, gradient), grain, stains, fibres, vignette | grain 0.05 / stains 0.5 fibres 0.6 |
| `chrome` | page-number corner, rule (top/bottom/left), running head (`true`/`"title"` = the deck title, `"scene"` = the scene id, or a `{token}` template), `source` line (default on: the slide's `source`) | tr + left rule / bl + top rule |
| `motion` | tempo, stagger, transitions, construction verbs | 1000 ms push/cut / 1500 ms wipe/fade |
| `image` | how pictures enter | full-bleed plates / framed postcards |
| `signature` | the one object | the first stage / the Hòn Dáu lighthouse |
| `arc`, `motifs`, `layers` | colour arc by scene, textures, Morph layers: lists of strings; a string is split (arc on → / -> / ; / commas, the others on ; / newlines) | written into art-direction.md |

`compile` writes `design/style.json` (the engine's style; `"route"` keeps the family for gate 3) and
`design/art-direction.md` (marked `<!-- genome -->`; it is regenerated while that marker is there, so edit the
genome). Guarantees: ink ≥ 7:1, muted ≥ 5:1, the kicker colour ≥ 4.6:1 and accents ≥ 3:1 — measured against the
ground **as it renders** (the darkest stained/vignetted paper edge, the lightest glowing noir), because a paper
ground's corners, where page numbers and sources sit, are much darker than its base colour; a type scale of
≤ 8 sizes from the ratio.

Layouts are not in the genome: they are invented per slide in `make_deck.py` from the grid, with the
composition written in the storyboard. The SpaceX and Đồ Sơn columns above were test runs and are not shipped;
the shipped worked example is `examples/genome-construct/` (brief with `tone:`/`domains:`, genome.json with an
arc string, directions.json, routing.md, art-direction.md and a `construct` deck; `build.sh` runs it, a test builds it).
The families' `references/styles/<pack>.md` grammars are examples of
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
