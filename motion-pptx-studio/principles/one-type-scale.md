# one-type-scale
One type scale per deck, built as a RATIO from the deck's hero size. It is not a fixed list of sizes.
- **Choose the hero first.** The numeral or word that carries a chapter is 200-400 pt, and it may bleed
  off the frame. From there, step down by a constant ratio (about 1.6-2) to body 16-20 pt and source
  10 pt. The range from the biggest to the smallest type is 15-25x. A deck that tops out at about 130 pt
  is a report, not a stage.
- **Use 6-8 sizes in all**, named by role in ds.py, and use the same ones in the films.
- **Chrome is minimal and quiet:** a kicker or chapter mark, a page number and a source line. There is no
  fixed title strip. The title moves with the composition (composition-range). At most a third of the slides
  have a small top-left headline; hero, photo and film slides let the image or number speak.
- **One grid** of 12 columns with about 0.6 in margins. Breaking the grid on purpose (a bleed, a
  numeral off the edge) is part of it.
- Body text is 40 words or fewer per slide; the rest goes in the notes.
- A label never sits on a line, a stamp or another label. Check the renders, not the JSON.
- art_check FAILS a deck where more than a third of the slides share the small top-left headline.
