# boardroom-data — cool light ground, deep teal signal, numbers as heroes

**Use for** economics, finance, business reviews, investor and consulting decks: sourced figures, comparisons and the one line that matters.
**Palette** ground `#F5F7FA`, second ground `#0B1220`, surface `#FFFFFF`, ink `#0F1722`, muted `#4E5A6A`, hairline `#D5DCE4`, accent `#0E7C6B`, second voice `#F2542D` (from the pack, assets/styles/boardroom-data.json).
**Fonts** Plus Jakarta Sans (display) · Inter (text) · Inter (labels).
**Routing fit** (route.py reads it from the pack): domains economy 1, finance 1, business 1, energy 0.5, climate 0.4, technology 0.3; tones calm, precise, analytical, serious, clear.

## Layout grammar
- A cool light ground (`#F5F7FA`) with a navy second ground for chapter openers; deep teal is the signal, coral only for the one warning.
- Plus Jakarta Sans display for numbers and titles, Inter for text and labels; a source line (`!!source`) on every number slide, an accent bar on top.
- Numbers are heroes: one headline figure set huge with its unit and period in a caption; a chart beside it drawn natively (bars, slopes, unit grids).
- Titles are conclusions ("Lạm phát hạ nhưng còn dính"), kickers name the measure and the base year; legends sit at the end of their line.

## Signature motion
- 1.2 s tempo, 200 ms stagger; bars `stretch` from the baseline, lines `wipe` along the stroke, Morph between chart keyframes.
- Signature: the growth curve drawn once and carried through the deck as the horizon.
- A teal bar that is the company (or the economy): it grows, splits into segments and becomes the plan.

## Avoid
heritage, culture and youth subjects (a KPI dashboard reads everything as a quarterly report), 3-D charts, two units on one axis, unsourced numbers.

## Routing rejects it when the deck is about
- heritage: a teal KPI dashboard grammar reads every subject as a quarterly report
- culture: numbers-as-heroes layouts leave no room for people, places and ritual
- youth: a boardroom register talks down to a young audience
