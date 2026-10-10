# Style packs: the system as data

A style pack is a JSON file in `assets/styles/` that holds the whole set (craft.md §1): palette roles,
fonts, type roles, grid, grounds, chrome, card and screen looks, shadow, photo treatment, motion
tempo and signature ideas. `build_deck.py` applies it to every slide, so a deck written against roles
and components looks designed before any slide-by-slide work.

`assets/reference/styles-gallery.jpg` shows the same starter deck in all five packs.

## 1. The packs

| Pack | Look | Fonts (display / text / label) | For |
|---|---|---|---|
| `lacquer-heritage` | dark lacquer + red crackle ground, gold hairline frame, gold foil objects | Cormorant / Josefin Sans | heritage, culture, history, craft; measured from the reference deck |
| `noir-product` | near-black stage, one amber signal, cyan for data, top rule + accent square | Space Grotesk / Be Vietnam Pro / JetBrains Mono | product, launch, developer tools, AI |
| `paper-editorial` | warm paper, ink serif, vermilion bar + running head | Fraunces / Inter | reports, essays, keynotes, research, data stories |
| `boardroom-data` | cool light ground with a faint grid, deep teal signal, source line in the chrome | Plus Jakarta Sans / Inter | business reviews, finance, consulting, investor updates |
| `studio-pop` | cream halftone and sun yellow, ink outlines, hard offset shadows, page badge | Bricolage Grotesque / Be Vietnam Pro | education, workshops, youth, events, campaigns |

Every font is OFL with full Vietnamese coverage (checked with `check_fonts.py --lang vi`).
`python scripts/fetch_fonts.py --style <pack> --out WORK/fonts --install --check vi` fetches static TTFs
(npm registry first, then google/fonts) and installs them for rendering.

## 2. Using and changing a pack

`studio.py new WORK --style <pack>` copies the pack to `WORK/design/style.json` and points `deck.json`
at it. Change the copy, never the pack:

- **palette**: keep the role names; change values to the subject's own colours and write where each
  comes from in `art-direction.md` (`#0E7C6B accent, from the brand board`). Re-check contrast.
- **fonts**: replace a family only with one that passes `check_fonts.py` for the on-slide language;
  add it to `font_files` so `fetch_fonts.py` and `deliver.py` ship it.
- **type**: change sizes by whole steps; keep 8-10 roles. Add a role (e.g. `"code"`) rather than
  sizing text by hand on slides.
- **grounds**: tune `base`, `tone`, `grain`, `vignette`, `crackle`; or point a ground at a file:
  `"grounds": {"main": "assets/my-ground.jpg"}` in deck.json.
- **chrome**: shapes on every slide. Text may use `{n}`, `{total}`, `{title}`, `{source}`, `{scene}`.
  Slides opt out with `"chrome": false`, keep some with `"chrome": ["!!pageno"]`, adjust with
  `"chrome_set": {"!!frame": {"alpha": 0.3}}`. A text that resolves to empty is left out.

Deck-level keys override the pack: `"palette"`, `"fonts"`, `"type"`, `"grid"`, `"card"`, `"screen"`,
`"shadow"`, `"motion"`; `"chrome"` replaces the pack's chrome, `"chrome_add"` appends to it.

## 3. A style from a brand board

1. Sample the brand's colours (logo, site, guidelines) into the roles: ground, surface, ink, head,
   muted, faint, accent (the brand colour), accent2 (a data colour that is not red/green only).
2. Fonts: the brand's if they are licensed for the deck and cover the language; otherwise the nearest
   OFL pair (geometric sans → Plus Jakarta Sans or Be Vietnam Pro; grotesk → Space Grotesk or
   Bricolage Grotesque; serif → Fraunces or Cormorant).
3. Chrome: one quiet brand mark (a bar, a square, the icon small), a page number, and a source
   line when the deck carries numbers.
4. Signature: an element of the product or brand that can move (craft.md §2).
5. Render the starter deck (`studio.py build`) and compare it with the brand's own material.

## 4. Keys reference

| Key | Contents |
|---|---|
| `palette` | ground, ground2, surface, ink, head, muted, faint, accent, accent2, lit, veil |
| `fonts` | display, text, label (family names as installed) |
| `font_files` | `[{"family", "weights": "400,700,400i"}]` for fetch_fonts / deliver |
| `type` | roles: kicker, display, title, subtitle, body, caption, label, numeral, quote, cardtitle, pageno (+ your own); each {font, size, bold, italic, spacing, line, caps, color} |
| `grid` | cols, left, right, top, bottom, gutter, safe (inches) |
| `default_bg`, `grounds` | ground name for every slide; recipes {kind lacquer/noir/paper/clean/halftone/flat, base, tone, grain, vignette, crackle, lift, dots, grid, grid_alpha, dot, seed} or file paths |
| `chrome` | {"under": [...], "over": [...]} shapes |
| `card` | fill, fill_alpha, line (null = open card), line_width, radius, lit_fill, lit_line, rule, dim_alpha, shadow, lit_shadow |
| `screen` | bezel, line, line_width, radius, bar |
| `shadow` | blur, dist (pt), dir (deg), color, alpha |
| `photo` | duotone [dark, light], veil |
| `motion` | default_ms, bloom_ms, stagger_ms |
| `signature_ideas` | prompts for the signature, not rules |
