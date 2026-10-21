# Examples

| Example | Style | What it shows |
|---|---|---|
| `catru-mini/` | lacquer-heritage | the reference deck's opening, UNESCO turn, highlight walk and circular close in 7 keyframes; strings computed from the instrument's box; gold-foil drawings from `make_assets_example.py` |
| `product-launch/` | noir-product | a fictional product: a typed line whose cursor grows into a panel and becomes the screen; a stat with bars that grow; a three-step timeline beside a changing screen; a highlight walk; the cursor closes the talk |
| `data-story/` | boardroom-data | a fictional chain's quarter: the headline number as the signature (huge, then parked in the corner, then back); bars grow then highlight; reasons revealed one by one beside a number that morphs letter by letter; a quote; a roadmap rail |
| `phin-multistyle/` | kinetic-type, lacquer-heritage, blueprint, swiss-blue, neo-brutal, retro-terminal | v5: one style per mini-chapter, each with its own grammar — typed hook and hyperlink menu; a camera pan along a year rail; a phin drawn from shapes, assembled then exploded; a brew diagram as MP4 then as editable animated shapes; a unit grid and an index slope chart; photo stickers with a click trigger and click-by-click steps; a terminal credit roll. CC photos from Wikimedia Commons (`assets/CREDITS.md`) |
| `case-catru-heritage.md` | | how the 48-slide reference deck was researched, corrected and built |
| `case-neko-core-product.md` | | a 34-slide product deck from a GitHub repo, with honesty rules |

Each folder: `make_deck.py` (writes `deck.json`), `build.sh` (assets → deck.json → `studio.py build`), `contact.jpg`
(the committed render). Generated assets, decks and renders are not committed; run `build.sh` to get the `.pptx` and
play it in PowerPoint 365 to see the Morph.
- `genome-construct/`: v5.6 worked example of the v5.5+ way: a brief with `tone:`/`domains:`, `design/genome.json`
  (arc as a string, explicit palette, chrome title + source), `design/directions.json`, the written `design/routing.md`
  and `art-direction.md`, and a 3-slide `construct` deck (bars grow, a lit navy capacity line). No photos; numbers fictional.
- `earth-fall/`: v5.2 pro-craft example: 22-slide Powers-of-Ten Earth deck, four sub-styles, variety audit passes.
- `flagship-khi-ap/`: v5.7 flagship under full creative authority: one data-grounded deck-wide concept (the 2026
  economy as a weather chart), six signature films (5 ManimGX + 1 Anatomy) each with an editable native fallback,
  the board, film recipes (`films/kit.py` and one file per film), art direction, film contact sheets and the scored
  critique log (every version, redo until ≥ 8). 30 Vietnamese slides; real IMF/WTO/WB/GSO numbers.
