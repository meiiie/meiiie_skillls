# Style packs: the system as data

A style pack is a JSON file in `assets/styles/` that holds the whole set (craft.md §1): palette roles,
fonts, type roles, grid, grounds, chrome, card and screen looks, shadow, photo treatment, motion
tempo and signature ideas. `build_deck.py` applies it to every slide, so a deck written against roles
and components looks designed before any slide-by-slide work.

`assets/reference/styles-gallery.jpg` shows the v4 starter deck in the first five packs (a system check, not a showcase).

## 0. v5.5: packs are families, the deck is routed and then invented

A pack is no longer something a deck "uses". It is a **family**: a starting point with a `fit` block
(`domains`, `tones`, `material`, `avoid` with a written reason per domain) that `route.py` scores against the
brief and the measured pictures (`references/design-space.md`). The router rejects families that are wrong for
the subject (gate 3 fails if the deck is built in one), and the chosen family seeds `design/genome.json`,
where every axis (palette from the photos, type, grid, material, chrome, motion grammar, composition) is
re-decided for this deck. Use `studio.py route WORK --apply` to copy the family as a base; then
`genome.py compile` produces the deck's own `design/style.json`. Never ship a family unchanged.

## 0b. Choose, do not default (v5 creativity rule)

There is no default template. For every deck write `## Style choice` in `design/art-direction.md`: the pack(s)
chosen, the scenes each covers and why the subject asks for it, and at least one pack you rejected and why
(Gate 3 checks it). A deck may change style per chapter (`"style"` on a slide; `"style_overrides"` per pack):
the sample `examples/phin-multistyle` uses six, one per mini-chapter, and keeps the talk one film through a
shared signature (a drop) and a circular close.

**A pack is a layout grammar, not a palette.** The `studio.py new` starter deck is a system check (fonts,
grounds, chrome, contrast) and looks the same in every pack on purpose; never ship it or show it as the style.
Each pack's own compositions and motion are in `references/styles/<pack>.md`; build those, by hand, from
shapes, photos and drawn objects (`make_deck.py`). Fewer styles done well beat many recolours.

## 1. The packs

| Pack | Look | Fonts (display / text / label) | For |
|---|---|---|---|
| `lacquer-heritage` | dark lacquer + red crackle ground, gold hairline frame, gold foil objects | Cormorant / Josefin Sans | heritage, culture, history, craft; measured from the reference deck |
| `noir-product` | near-black stage, one amber signal, cyan for data, top rule + accent square | Space Grotesk / Be Vietnam Pro / JetBrains Mono | product, launch, developer tools, AI |
| `paper-editorial` | warm paper, ink serif, vermilion bar + running head | Fraunces / Inter | reports, essays, keynotes, research, data stories |
| `boardroom-data` | cool light ground with a faint grid, deep teal signal, source line in the chrome | Plus Jakarta Sans / Inter | business reviews, finance, consulting, investor updates |
| `studio-pop` | cream halftone and sun yellow, ink outlines, hard offset shadows, page badge | Bricolage Grotesque / Be Vietnam Pro | education, workshops, youth, events, campaigns |
| `kinetic-type` (v5) | black stage, condensed caps 110–150 pt that are the picture, one signal red | Anton / Inter / Space Mono | hooks, manifestos, chapter cards, the close · `styles/kinetic-type.md` |
| `blueprint` (v5) | drafting-blue sheet with grid, hairline drawings, mono callouts, one amber part | Space Grotesk / Be Vietnam Pro / JetBrains Mono | anatomy, architecture, systems, processes · `styles/blueprint.md` |
| `swiss-blue` (v5) | white paper, one cobalt, full-bleed numeral field, hand-built unit grids and slope charts | Archivo / Inter / IBM Plex Mono | data stories, research, engineering, public sector · `styles/swiss-blue.md` |
| `neo-brutal` (v5) | bone/lime, tilted photo stickers with ink borders and hard shadows, tag strips | Dela Gothic One / Space Grotesk / Space Mono | recipes, how-tos, workshops, youth · `styles/neo-brutal.md` |
| `retro-terminal` (v5) | phosphor on CRT scanlines, prompt chrome, typed commands | VT323 / IBM Plex Mono | credits, developer and computing stories · `styles/retro-terminal.md` |
| `heritage-collage` (v5.4) | aged paper and terracotta gradients, heavy caps titles with a script accent line, object cut-outs, dense bordered photo grids, leader-line callouts, palette swatches, red-node maps | Anton / Be Vietnam Pro / Barlow Condensed + Dancing Script (`script`) | heritage, architecture, museums, travel, school reports, product anatomy · `styles/heritage-collage.md` |

`assets/styles-experimental/` holds three more packs (glass-tech, papercut-collage, desktop-os) that have a
palette, fonts and grounds (`mesh`, `paper`) but no demonstrated composition yet (load one by path, `--style $S/../assets/styles-experimental/glass-tech.json`): design their grammar before
using them, and never with the starter layout.

Every font is OFL with full Vietnamese coverage (checked with `check_fonts.py --lang vi`).
`python3 scripts/fetch_fonts.py --style <pack> --out WORK/fonts --install --check vi` fetches static TTFs
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

**Custom styles inside deck.json (v5.4).** A style does not have to be a file. `"styles": {"<name>": {...}}`
defines one by name; `"extends": "<pack or path>"` starts from a pack and the rest overrides it (a style
without `extends` is a full spec). Use the name as the deck `"style"` or on any slide. A
`"style_overrides"` entry whose name is not a shipped pack is read the same way, so
`"style_overrides": {"zine": {"extends": "neo-brutal", "palette": {...}}}` plus `"style": "zine"` on a
chapter works (before 5.4 it stopped with "style not found"). Shipped packs keep the old meaning:
`"style_overrides": {"paper-editorial": {...}}` tweaks that pack when a slide switches to it.

**Type scale headroom (v5.4).** Every shipped pack uses at most 8 distinct sizes (caption = label = page
number, subtitle = card title), so a deck can add two sizes of its own and still pass the ≤ 10 rule.

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
| `type` | roles: kicker, display, title, subtitle, body, caption, label, numeral, quote, cardtitle, pageno (+ your own: `script`, `callout` in heritage-collage); each {font, size, bold, italic, spacing, line, caps, color, rot (text rotation, v5.4), overlay (may cross other text without an overlap warning, v5.4)} |
| `grid` | cols, left, right, top, bottom, gutter, safe (inches) |
| `default_bg`, `grounds` | ground name for every slide; recipes {kind lacquer/noir/paper/clean/halftone/flat/gradient, base, tone, grain, vignette, crackle, lift, dots, grid, grid_alpha, dot, seed; paper: stains 0..1, fibres; gradient: angle} or file paths |
| `chrome` | {"under": [...], "over": [...]} shapes |
| `card` | fill, fill_alpha, line (null = open card), line_width, radius, lit_fill, lit_line, rule, dim_alpha, shadow, lit_shadow |
| `screen` | bezel, line, line_width, radius, bar |
| `shadow` | blur, dist (pt), dir (deg), color, alpha |
| `photo` | duotone [dark, light], veil |
| `motion` | default_ms, bloom_ms, stagger_ms |
| `signature_ideas` | prompts for the signature, not rules |
| `rules` | optional prose rules the pack's audits enforce (heritage-collage: text on photo, caps, accents, rhythm) |
| deck `styles` | v5.4: inline styles by name, `{"extends": pack, ...overrides}` or a full spec |
