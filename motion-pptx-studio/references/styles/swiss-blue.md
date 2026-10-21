# swiss-blue — white paper, one cobalt, numbers as heroes

**Use for** data stories, research, engineering and public-sector talks; the "white-blue" option.
**Palette** white `#FFFFFF` (with a 0.56 in grid at 3.5%), ink `#0B1B3F`, muted `#3F4B72`, hairline `#D5DEF2`,
ONE cobalt `#1F4BFF`; `#00A3E0` only as a second data series.
**Fonts** Archivo (display) · Inter (text) · IBM Plex Mono (kickers, axis labels).

## Layout grammar
- Strict 12-column grid, flush left, ragged right; asymmetric splits (5 | 7) with a full-bleed cobalt field
  holding one giant white numeral (380 pt), its sentence set small at the bottom of the field.
- Data is drawn by hand from the numbers, not from the bar component: unit grids (10×10 squares = 100%),
  slope charts on an index (2023 = 100) when units differ, a dashed baseline at 100, values set at 88 pt next to
  the end of their line, the unit and period in a caption under them.
- Kicker in mono caps names the measure and the base; the title is the conclusion ("Bán ít hạt hơn…").
- No shadows, no rounded corners, no gradients.

## Signature motion
- `push` (from the right) into the chapter; the cobalt field `wipe`s down, the numeral `fly`s up from the bottom.
- Unit-grid rows `wipe` left-to-right, 90 ms apart.
- Slope chart in two keyframes: the first line `wipe`s in, **Morph** to the second keyframe where the first line
  greys and the second line draws in cobalt; its end dot loops a `pulse`.

## Avoid
Two units on one axis (index them), 3-D, legends far from the data, centred layouts.
