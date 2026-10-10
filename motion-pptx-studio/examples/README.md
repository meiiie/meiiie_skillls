# Examples

| Example | Style | What it shows |
|---|---|---|
| `catru-mini/` | lacquer-heritage | the reference deck's opening, UNESCO turn, highlight walk and circular close in 7 keyframes; strings computed from the instrument's box; gold-foil drawings from `make_assets_example.py` |
| `product-launch/` | noir-product | a fictional product: a typed line whose cursor grows into a panel and becomes the screen; a stat with bars that grow; a three-step timeline beside a changing screen; a highlight walk; the cursor closes the talk |
| `data-story/` | boardroom-data | a fictional chain's quarter: the headline number as the signature (huge, then parked in the corner, then back); bars grow then highlight; reasons revealed one by one beside a number that morphs letter by letter; a quote; a roadmap rail |
| `case-catru-heritage.md` | | how the 48-slide reference deck was researched, corrected and built |
| `case-neko-core-product.md` | | a 34-slide product deck from a GitHub repo, with honesty rules |

Each folder: `make_deck.py` (writes `deck.json`), `build.sh` (assets → deck.json → `studio.py build`), `contact.jpg`
(the committed render). Generated assets, decks and renders are not committed; run `build.sh` to get the `.pptx` and
play it in PowerPoint 365 to see the Morph.
