# Art direction (Phase 3 → Gate 3)

"Cần chọn font cần tài nguyên asset": fonts, palette and motifs are chosen deliberately, from the research,
and proven with renders before the storyboard.

## 1. Fonts
- **Two families, not two files of one family.** Gate 3 reads the name table (typographic family, else family) and folds it: weight, width, and the words Display / Condensed / Text are stripped. Noto Sans and Noto Sans Display count as one family. Noto Sans Mono does not. Calibri, Arial, Times New Roman, Cambria and Aptos do not count toward the two. A deck whose only faces are a regular and a display cut of the same family fails.
- **Coverage first.** Vietnamese needs ă â đ ê ô ơ ư plus 5 tone marks on every vowel, including stacked marks (ẫ ỡ ự).
  `python $S/check_fonts.py WORK/fonts/*.ttf --lang vi --png WORK/design/font-sample.png > WORK/design/font-check.txt`
  then **look at the sample**: marks must not collide or fall back to another font.
  - Rejected in practice: Bodoni Moda (no ơ ư ỹ ẫ); Great Vibes (marks clash with the swashes). JetBrains Mono lacks ✓, so write "ok".
  - Proven pairs: Cormorant (Garamond) + Be Vietnam Pro or Josefin Sans (heritage, calligraphic contrast);
    JetBrains Mono + Be Vietnam Pro (developer product); Fraunces + Alegreya Sans; Charm as a Vietnamese script accent.
- **Static instances only.** PowerPoint handles variable fonts badly (wrong weights, fallback). Google Fonts often
  ships only `Family[wght].ttf`; make static files:
  ```bash
  curl -sSfL -o "CormorantGaramond[wght].ttf" "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
  python -m fontTools.varLib.instancer "CormorantGaramond[wght].ttf" wght=600 -o CormorantGaramond-SemiBold.ttf --update-name-table
  ```
  Use the instance's family name in the deck (here "Cormorant Garamond SemiBold"). Ship the OFL text with the fonts.
- Install the fonts locally before rendering (`~/.local/share/fonts` + `fc-cache -f`, or `~/Library/Fonts`), otherwise
  LibreOffice renders a fallback and you judge the wrong thing. `check_deck.py` warns when a font in the deck is not installed.
- Monospace headings break words mid-word in narrow template boxes; shorten the words, reduce the size or widen the box.

## 2. Palette
- 1 background, 1 text colour, 1 muted colour, **1 accent** (2 at most). Write the hex code and **where it comes from**, on the same line as the hex (a URL, or the words from / source / brand / photo / lacquer / sample / pixel / board / dossier / measured / nguồn). A line that is only `#0A0B0D background` fails. At least 3 hexes.
  Heritage example: `#0E0A07` lacquer ground, sampled from the dossier photo; `#F1E4C8` dó paper, measured from the sample; `#C79A3B` gold leaf, from the lacquer sample; `#8C7B63` muted ink, sampled from the same photo.
  Product example (neko-core): `#0A0B0D` from the brand board; `#F4F5F7` from the brand board; `#F0A030` amber, from the brand board. No purple and no glow, because the board said so.
- Contrast: body text at least 4.5:1 against its actual background. Over photos, use a veil rectangle or a gradient scrim.

## 3. Motifs and textures
Only motifs from the TRUE list in `research/accuracy.md`. Generic decoration (sơn mài texture, cloud scrolls) is
allowed as background texture, never as content. Generate textures procedurally (CC0) or use verified photos.

## 4. Layered objects (what will move)
Decide which objects carry the motion through the deck and split them into parts:
- ca trù: đàn đáy as `ddHead / ddNeck / ddBody` on a 600×2400 canvas; strings as live lines (`!!str1-3`) locked to
  the neck coordinates; a thẻ trù medallion in three rings (`!!medW / !!medT / !!medC`) that rotate and bloom.
- neko-core: the block cursor `!!cursor`, which hides a tiny `!!cat` that grows out of it; the terminal `!!panel`.
These objects become the `!!` layers in the storyboard. One strong recurring object beats ten decorations.

## 5. Colour arc (the "bloom")
Plan where colour arrives: muted (sepia or duotone, a veil rectangle at 45–70%) for the problem or history part,
then a **bloom slide** with a long Morph (2 s) when the hero appears (the mascot, the product, the solution),
then full colour. The idea comes from the reference talk's "muted to colour" moment.

Write the arc in `design/art-direction.md` **and** on the storyboard header, with at least two different background hexes and at least two scene ids:

```
- colour arc: S1-S4 #0E0A07 → S6-S11 #F1E4C8
```

"Navy throughout", a single hex, or a TODO line fails Gate 3 and Gate 4. Backgrounds in the accepted decks are pictures, not a solid `p:bg` fill, so the gate checks this declaration rather than counting solid fills in the pptx. The two hexes are the two backgrounds you will actually use.

## 6. Family samples (Gate 3)
Build a 2–4 slide family deck (title + body + one keyframe pair) with `build_deck.py`, render it and copy the
title and body renders to `WORK/design/samples/`. If two directions are plausible, render both and choose, or
show both to the user. The ca trù user rejected the first family ("Trông chưa ổn lắm"), and the second family
came from research, not from taste.
