# Art direction (Phase 3 → Gate 3)

"Cần chọn font cần tài nguyên asset": style, signature, fonts, palette and motifs are chosen deliberately,
from the research, and proven with renders next to the reference before the storyboard. Read
`craft.md` first; this file is the procedure.

## 1. Style (start from a pack)
Choose the pack closest to the kind and the subject (`styles.md`, `genres.md`), then make it the
subject's own:
```bash
python3 $S/studio.py new WORK --kind heritage --style lacquer-heritage --title "…" --fonts
```
`design/style.json` is your copy. Change palette values to sourced colours, swap a font only for one that
passes the glyph check, keep the roles. Write `- style: <pack>` and every change in `art-direction.md`.

## 2. Signature
Name ONE object that carries the deck (craft.md §2): where it rests, what it becomes at the hook, the
turn and the close, how it is split into `!!` parts. Write it under `## Signature` in
`art-direction.md`. Gate 3 fails without it.

## 3. Fonts
- **Two families, not two files of one family.** Gate 3 reads the name table (typographic family, else family) and folds it: weight, width, and the words Display / Condensed / Text are stripped. Noto Sans and Noto Sans Display count as one family. Calibri, Arial, Times New Roman, Cambria and Aptos do not count.
- **Coverage first.** Vietnamese needs ă â đ ê ô ơ ư plus 5 tone marks on every vowel, including stacked marks (ẫ ỡ ự).
  `python3 $S/studio.py fonts WORK --style <pack>` (fetch + install + `check_fonts.py --lang vi` → `design/font-check.txt`),
  then **look at the sample**: marks must not collide or fall back to another font.
  - Rejected in practice: Bodoni Moda (no ơ ư ỹ ẫ); Great Vibes (marks clash with the swashes). JetBrains Mono lacks ✓, so write "ok".
  - Proven pairs (all in the packs): Cormorant + Josefin Sans; Space Grotesk + Be Vietnam Pro (+ JetBrains Mono);
    Fraunces + Inter; Plus Jakarta Sans + Inter; Bricolage Grotesque + Be Vietnam Pro.
- **Static instances only.** PowerPoint handles variable fonts badly. `fetch_fonts.py` gets static TTFs
  (npm `@expo-google-fonts/<family>` or google/fonts `static/`). By hand:
  ```bash
  python3 -m fontTools.varLib.instancer "Family[wght].ttf" wght=600 -o Family-SemiBold.ttf --update-name-table
  ```
  Use the instance's family name in the deck. Ship the OFL text with the fonts.
- Install the fonts locally before rendering, otherwise LibreOffice renders a fallback, the layout warnings
  are skipped ("font not installed"), and you judge the wrong thing.

## 4. Palette
- Roles, not colours: ground, ground2, surface, ink, head, muted, faint, accent (one), accent2 (data).
  Write each hex with **where it comes from** on the same line (a URL, or from / source / brand / photo /
  lacquer / sample / pixel / board / dossier / measured / style pack / nguồn). A line that is only
  `#0A0B0D background` fails. At least 3 hexes.
  Heritage: `#140B08` lacquer ground, sampled from the reference deck's ground; `#D9B26A` gold, measured from its frame.
  Product: `#0A0B0D` from the brand board; `#F0A030` amber, from the brand board. No purple and no glow, because the board said so.
- Contrast: body text ≥ 4.5:1 against what is really behind it; `check_deck.py --renders` measures it.
  Over photos, a veil or a scrim.

## 5. Motifs, grounds and textures
Content motifs come only from the TRUE list in `research/accuracy.md`. Generic decoration (lacquer,
paper, grain, halftone) is allowed as a ground or a band, never as content.
```bash
python3 $S/make_assets.py ground --style lacquer-heritage --name alt --out WORK/assets/ground-alt.jpg
python3 $S/make_assets.py foil drawings/hero.svg --finish gold --out WORK/assets/hero.png
python3 $S/make_assets.py layers drawings/hero.svg --finish gold --out-dir WORK/assets/hero   # one PNG per <g id>
python3 $S/make_assets.py photo raw/place.jpg --mode duotone --colors "#140B08,#E2BE7C" --aspect 16:9 --pair --out WORK/assets/place.jpg
python3 $S/make_assets.py pattern --kind woven --finish gold --size 2400x300 --out WORK/assets/band.png
```

## 6. Layered objects (what will move)
Decide which objects carry the motion and split them into parts on one shared canvas:
- ca trù: đàn đáy as `ddHead / ddNeck / ddBody` on 600×2400; strings as live lines (`!!str1-3`) locked to
  the neck coordinates (computed in `make_deck.py`); a medallion in three rings (`!!medW / !!medT / !!medC`).
- product: the cursor `!!cursor` that becomes the panel; the `!!screen` group.
- data: the headline `stat` `!!k` that shrinks into the corner.
These become the `!!` layers in the storyboard. One strong recurring object beats ten decorations.

## 7. Colour arc (the "bloom")
Plan where colour arrives: muted (sepia or duotone, a veil at 45–70%) for the problem or history, then a
**bloom** with a long Morph (2 s) when the hero appears, then full colour. Or two grounds: the style's
`main` and `alt` (the reference's red lacquer for the turn; the data story's dark slate for the headline).
Write it in `art-direction.md` **and** on the storyboard header, with at least two background hexes and
two scene ids: `- colour arc: S1-S4 #0E0A07 → S6-S11 #F1E4C8`.

## 8. Samples and the comparison (Gate 3)
`studio.py new` writes a five-slide starter (a title, a highlight walk pair, a bar grow pair). Edit it into
your direction: real title, your signature, your ground, one real visual. Then:
```bash
python3 $S/studio.py build WORK --group sample
cp WORK/renders/sample-1/slide-01.jpg WORK/renders/sample-1/slide-03.jpg WORK/design/samples/
python3 $S/studio.py compare WORK WORK/renders/sample-1
```
Answer the compare questions in `art-direction.md` (`reference-bar.md` §3). If two directions are
plausible, render both and choose, or show both to the user. Change direction now, not after 40 slides.
