# Art direction: World economy, October 2026 (Vietnamese deck)

Boards: `design/board/directions.png` (3 directions) and `design/board/chosen-A.png` (the system).
Tokens: `design/ds.py`, `design/style.json`. Fonts: `fonts/` (all OFL).

## The brief in one sentence
The IMF's October 2026 framing is *two opposing forces*: a negative energy supply shock centred on the Gulf, and a positive AI-investment demand shock centred on East Asia. World growth eases from 3.5% to 3.1%. The art direction has to make those two forces something the audience can *see*.

## Three directions
**A · Khí áp (pressure chart): CHOSEN.** A synoptic weather chart of the economy. Isobars are real growth contours, interpolated from IMF Table A country forecasts. A deep low (T, vermilion) sits over the Gulf, a high (C, Prussian blue) over East Asia, and the world's 3.1% line is drawn as a thick ink isobar. The metaphor extends naturally across the deck: barometers for policy rates, wind and fronts for trade, a barograph drum for the growth history, a tide gauge for debt.

**B · Mạch và ống (pipes vs circuits).** Night schematic, amber oil/gas pipes against cyan chip traces. Very striking for the trade and AI chapters, but it cannot carry rates, inflation or debt, and it reads as a tech-product launch rather than economic journalism. Kept as a secondary vocabulary for the isometric supply-chain scene.

**C · Trang nhất (front page).** Broadsheet discipline: a huge 3,1%, a serif headline, an annotated line chart. Safe and FT-like, but it has no idea specific to 2026; the same layout would fit any year. Its discipline of direct labels and one big number per slide is folded into A.

## Why A
1. **The metaphor is the data.** Every isobar is computed from published numbers, so it is not decoration. A meteorological "low" is literally a region of below-world growth.
2. **It fits the IMF story exactly:** two pressure centres, two shocks.
3. **It scales to 30 slides without new metaphors:** pressure, then barometer, then wind, then barograph, then tide gauge.
4. **No clichés:** no globes with dollar signs, no scales, no handshakes, no stock photos.
5. **Editorial look.** Warm chart paper, ink, two signal colours and one reserved colour for Vietnam.

## System
- **Palette (each colour has one job):**
  - PAPER #EEEBE3, LAND #E0DCD1, RULE #C9C3B6, SLATE #5E6873, INK #151C26
  - LOW #C0391F: energy shock, below world, negative
  - HIGH #1F4F8F: AI, above world, positive
  - VN #B9850F: Vietnam only, at most once per slide
- **Type:**
  - Source Serif Pro Semibold for headlines and numerals
  - IBM Plex Sans for text and labels
  - IBM Plex Mono for instrument readings and stamps
  - 7 sizes in pt: 132 / 58 / 34 / 23 / 17 / 13 / 10
- **Grid:**
  - 13.333 × 7.5 in, 12 columns, 0.6 in margins, 0.2 in gutter
  - Header: kicker, a title across 8 columns, and a standfirst across 4 columns, with an ink rule at 1.5 in
  - A fixed 64:27 film window (12.13 × 5.12 in, 2560 × 1080 px), so film and native fallback register exactly
  - Sources at 10 pt in the footer
- **Projection:** Equal Earth centred on 150°E, so Asia, the Gulf and the Pacific flows sit in the middle and America is on the right. This is a deliberate Asian-audience choice.
- **One geometry, two renderers:** `pressure_geom.py` and `baro_geom.py` produce the geometry once. Manim renders the film; `make_m1.py` draws the same geometry as editable native pptx shapes.

## Reference comparison (described, not copied)
- **FT / Bloomberg data graphics:** direct labels instead of legends, a warm ground, a single accent per idea, and sources on the page. A matches this; the legend is kept only for the two isobar colours.
- **The Economist "Graphic detail":** one-sentence chart takeaways, set as the end caption and headline in each film. A matches this.
- **Pentagram data work, and meteorological synoptic charts (UK Met Office / JMA surface analysis):** the T/C pressure-centre glyphs, thin isobar families and thick reference isobar are borrowed directly from synoptic convention, re-typeset.
- **Where we fall short of those references:**
  - The ocean isobars are interpolation, not data. This is flagged in the source line.
  - The Asian label cluster is still denser than an FT graphic would allow.
  - The barometer scene is cleaner but less surprising than the map.

## The six films (status 21/10/2026, 22:xx UTC+7)
| # | chapter | instrument | file | length | self-score |
|---|---|---|---|---|---|
| S1 | 01 tăng trưởng | isobar chart 2025→2026, ranked Gulf ledger, Asia HIGH | assets/film/pressure.mp4 | 20.2 s | 8 |
| S3 | 01 lịch sử | barograph drum unrolling into a chart, 2018–2027 vs 2008–17 avg | drum.mp4 | 17.2 s | 8 |
| S2 | 03 lãi suất | three barometers with bezels; push from the Fed gap into its bar | baro.mp4 | 17.6 s | 8 |
| S4 | 04 thương mại | trade winds per region → ranked diverging bars | wind.mp4 | 15.0 s | 7.5–8 |
| S6 | 04 AI | Anatomy chip-to-port line, 4 lit stations + synced native labels | chipline.mp4 | 12 s | 7.5 (8 on slide) |
| S5 | 05 nợ công | stilling wells, 100% flood line, US +22,7 | tide.mp4 | 16.85 s | 8 |
Each has an editable native fallback slide drawn from the same geometry (slides 5, 9, 14, 17, 21, 24) and
slide 22 pushes a native Morph camera into the Anatomy shapes.
