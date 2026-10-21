# Flagship example: "Khí áp 2026" (the world economy, October 2026, Vietnamese, 30 slides)

Built in v5.6→5.7 under the "full creative authority" brief (SKILL.md §Full creative authority). Lightweight copy:
recipes, boards, stills and the critique log. No films, decks or map data are committed (they regenerate).

**Concept.** The 2026 economy as a synoptic weather chart, grounded in the numbers: growth isobars with an energy
LOW over the Gulf and an AI HIGH over East Asia (IMF WEO 10/2026), barometers for policy rates (Fed/ECB/BoJ),
a barograph drum for world growth 2018–2027, trade winds for 2026 export volume by region (WTO), stilling wells
for public debt with a 100% flood line (IMF A8), and an isometric chip-to-port line for AI-enabling goods (Anatomy).
One palette with one job per colour (LOW vermilion, HIGH Prussian blue, ochre for Vietnam only), Source Serif +
IBM Plex, 7 type sizes, a 64:27 film window.

| file | what |
|---|---|
| `art-direction.md`, `board/directions.jpg`, `board/chosen-A.jpg` | three directions, why A, the system |
| `films/ds.py` | design tokens shared by the films and the deck |
| `films/kit.py` | ManimGX helpers: `T()` text in the deck's sizes, `halo()`, `poly()`, `View` (pan/zoom with constant strokes), `fs()` |
| `films/pressure*.py` | S1: isobars 2025→2026 (geometry precomputed by `pressure_geom.py` from Natural Earth into JSON; needs `data/ne_50m_*` and matplotlib in the system python) |
| `films/baro*.py` | S2: three barometers, bezel/knurl/screws/mirror, a continuous push from the Fed gap into its bar |
| `films/drum*.py` | S3: barograph drum (clockwork, aneroid stack, pen) unrolling into a flat chart |
| `films/wind*.py` + `wind_xy.json` | S4: streamlines per region flying into a ranked diverging bar chart |
| `films/tide*.py` | S5: stilling wells, digit-roll years, US +22,7 bracket, wells scale to 0.8 for the headline |
| `anatomy/chipline.mjs` | S6: Anatomy figure, 4 stations lit in turn, anchors for synced native labels |
| `make_m1.py`, `natives.py`, `make_deck.py` | the deck: one geometry drawn twice (film + editable native fallback), Morph camera on the map, native zoom into the Anatomy shapes (`zoom_group`), synced numbered labels (`s6_labels`) |
| `postfix.py` | the theme-effectRef strip for decks built before v5.7 (now built into `build_deck.py`) |
| `stills/S1–S6_contact.jpg`, `contact.jpg` | film contact sheets and the deck contact sheet |
| `critique-log.md` | every version with its score, what was weak and the fix |

Render a film: `manimgx render films/drum.py Drum -r 2560x1080 --fps 30 -o assets/film/drum.mp4` (test at
`-r 1280x540 --fps 15`); the Anatomy film: `python3 $S/anatomy_film.py anatomy/chipline.mjs --name chipline --work WORK
--region 0.6,1.62,12.133,5.119 --fps 25 --scale 1.6`. Quirks: `references/manimgx-quirks.md`.
The scene class names are the `class … (Scene)` in each file.
