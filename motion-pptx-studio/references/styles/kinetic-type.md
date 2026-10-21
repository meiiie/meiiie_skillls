# kinetic-type — the words are the picture

**Use for** hooks, manifestos, chapter cards, the close. Rarely a whole deck: 2–4 slides that open and close a talk.
**Palette** stage `#0B0B0C`, ink `#F4F1EA`, one signal `#FF4D33` (accent), `#FFD400` only for a warning beat.
**Fonts** Anton (display, caps, condensed) · Inter (text) · Space Mono (labels). All OFL, Vietnamese PASS
(`check_fonts.py --lang vi`). Anton's stacked marks (Ộ, Ọ) need line ≥ 0.86 and a box ≥ 1.8 × size.

## Layout grammar (what makes it this style, not a recolour)
- One idea per slide, set at 110–150 pt, flush left, two lines max; the second line carries the accent.
- The type touches the safe area on the left and runs long on the right: the line is a horizon, not a centred title.
- No cards, no charts, no photos except under the final line (duotone, ≤ 50% luminance).
- A single numeral can replace the headline (`numeral` 240+ pt) with one sentence under it.
- A menu is a stacked list of 54 pt caps with accent numerals, each a `link` to its chapter (the slidewppt.vn
  "bấm để nhảy" pattern).

## Signature motion
- `type` (letter by letter, `step` 12–15%) for the first line, the accent line 0.9 s later.
- `word` for a sentence under a numeral; `zoom` for the numeral; `cut` between kinetic slides on the beat.
- One small accent object (a drop, a dot) with `drop` then a looping `path` or `pulse`.
- Close with `fallover` or `fade` onto the same grammar over a photo (circular close).

## Avoid
Centred titles; more than one accent colour on a slide; body paragraphs; letter-by-letter on more than one
line at a time (it gets slow: n letters × step × ms).
