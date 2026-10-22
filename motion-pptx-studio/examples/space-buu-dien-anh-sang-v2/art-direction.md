# Art direction v2 — "Bưu điện ánh sáng"  (22/10/2026, UTC+7)

**Idea in one line.** Every sky image is a letter that arrived late; its postmark says when its light
left. The deck travels from the newest letters (Moon, Sun) to the oldest (the CMB), so **the deck
itself redshifts**: each chapter's ground is redder/darker than the last, the way old light is.

## Chapter palettes (role names fixed in design/ds.py; one theme per chapter)
| chapter | theme | ground | ink | accents | why |
|---|---|---|---|---|---|
| Prologue + close | night | navy #0B1324 | cream #EEE7D8 | vermilion #F0643A, earth blue #8DB8E3 | the Pale Blue Dot's sky; home |
| 1 Người đưa thư | paper | sunlit cream #EFE6D2 | navy #16213A | vermilion, sun gold #D49A1E | sunlight, airmail paper, the nearest letters |
| 2 Thư từ hàng xóm | indigo | starlight indigo #151A3D | cream | lavender-blue #A9B6FF, vermilion | stars and galaxies; the blue end |
| 3 Phong bì kéo giãn | lab | spectrograph white #E6E9EC | ink #121826 | full spectrum, crimson #C42A2A | a lab plate: where light is measured |
| 4 Hòm thư mới (Webb) | gold | infrared black #0E0C08 | cream | Webb gold #E2B045 | gold mirrors, infrared |
| 5 Bức thư cổ nhất | lava | lava brown #2A0E08 | cream | orange #E8541F, amber #FFC15A, cold blue | WMAP's warm map; microwave |
| 6 Thư chưa đọc được | dark | near-black #0A0A10 | pale violet | only vermilion for the 4.9% | colour drains away: we can't read it |

## Type (chosen for the concept, 4 roles, 8 sizes: 10/12/16/22/32/54/96/150)
- **Fraunces** SemiBold/Light/Italic — the *letter's voice*: titles, quotes. A soft old-style
  letterpress serif, like stationery; full Vietnamese.
- **Barlow Condensed ExtraBold** — *franking-machine numerals*: every hero number, set huge (96–200 pt).
- **IBM Plex Mono** — *the postmark ink*: kickers, dates, coordinates, rail labels, letter-spaced caps.
- **IBM Plex Sans** — body and captions only.

## One recurring motif: the lookback rail (the postmark scale)
A thin vertical rail at the right edge (x 12.88 in) with log ticks of light-travel time, from
"BÂY GIỜ" (top) to "13,8 TỶ NĂM" (bottom). A vermilion postmark (dot + ring + mono value) marks how
long *this slide's* light travelled. It descends through the deck. A small postmark ring is the
secondary device; photos used as insets get perforated "postage-stamp" edges.

## Background strategy (no empty slide)
Every slide has either a full-bleed NASA/ESA photograph (cover, Voyager, Sun, Gaia, Andromeda,
MoM-z14, Webb deep field, WMAP, Pale Blue Dot) or a flat editorial illustration filling the frame
(Earth wound 7.5 times by light, Earth–Moon pulse, departure board, light-year ruler, top-down
galaxy, stretched envelope, spectrum band, mirror hexes, sunshield kite, Earth–L2 strip,
lookback-shell cutaway, cosmic-day clock, pie wedge, two disagreeing postmarks). Films sit on a
ground of their own chapter colour so they merge with the slide.

## Hero number → visual metaphor
24 giờ → 24-h dial around Voyager · 17.971 ngày → 17,971 dots, 1 lit · 299.792.458 m/s → Earth
wound 7.5 times · 1,3 giây → pulse Earth→Moon · 8 phút 20 giây → the Sun itself · 4,25 năm →
light-year ruler · 27.000 năm → ring on the galactic centre · 100.000 năm ánh sáng → galaxy
diameter bar · 2,5 triệu năm → Andromeda · z = 14,44 → envelope stretched 15,44× · 1.877 nm → eye
vs Webb band · 6,5 m → 18 hexes · 21 × 14 m → sunshield kite · 1,5 triệu km → Earth–Moon–L2
strip · 4,6 tỷ năm → deep field as postage stamp · 380.000 năm → outermost shell · 2,725 K →
WMAP · cosmic day → clock dial · 4,9% → wedge · 67,4 vs 73,0 → two postmarks that don't line up ·
0,12 pixel → ring on the dot.

## Composition plan (vary: full-bleed / split / diagram band / big-number / board / dial)
See design/board/board.png (30 wireframe tiles in chapter colours). Rules: hero numbers 96–200 pt
condensed, never two equal-weight elements; text blocks ≤ 3 lines on photo slides; at most one
paragraph per slide; the rail and a mono kicker are the only chrome.
