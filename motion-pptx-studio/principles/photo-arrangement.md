# photo-arrangement
A photo is a space the viewer enters, not a rectangle next to the text. The photo comes first; the type fits into it.
- **Ask what the photo is for**, then pick an arrangement. Is it evidence, a place, an object, texture or a sequence?
  - **place → full-bleed.** Type sits in the photo's own quiet area, behind a light falloff.
  - **object → cut-out on the chapter material**, at hero scale, overlapping or in front of display type.
  - **texture or detail → extreme crop that bleeds off two edges.** The numeral goes on its quiet side.
  - **scale or change → a pair:** a detail next to the wide shot. The pair can come from one photo.
  - **time or process → a sequence:** a strip of 3-5 same-sized frames on one baseline.
  - **a meaning shape → a mask from the subject:** a cup rim, an arch, a field strip.
- **Gated per chapter** (`"chapter"` key in deck.json; build.py runs art_check): at least one full-bleed REAL photo
  (or a full-bleed film); cut-outs where an object earns one, not by quota; no text over a busy photo area; few slides more than half empty field.
- **Bleed and scale contrast.** Every chapter has at least one full-bleed. No photo floats at about 40 % width in
  a margin. Neighbouring photos differ in scale by 3x or more.
- **Find the subject and the quiet space before placing type:** `photo_layout.py analyze`.
  - Saliency can mistake paving or foliage for a subject, so check its box by eye. Pass `--focus` when it is wrong.
  - Crop the subject onto a third (`crop --subject-at`) and leave the opposite side for the words.
- **Cut-outs:** `photo_layout.py cutout` (rembg, with GrabCut as fallback). Add a soft contact shadow in the
  ground's colour. Look at the edge at 2x.
- **No photo for an idea?** Make a dark or bold slide instead. Use a numeral that bleeds off the frame, or a
  drawn object at hero scale. Never put a small icon in a large empty field.
