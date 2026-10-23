# sample-chapters
A mood board promises; three rendered chapters prove. Decide the look on real slides, not on words.
- **After the photo library (photo-library-first), build three sample chapters** from DIFFERENT library picks, one per direction, 3-4 finished slides each,
  through build.py with real photos, real type and one real data slide: samples/A, samples/B, samples/C,
  each with renders/*/contact-1.jpg. Same chapter content in all three, so only the art direction differs.
- **Radically different on four axes:** layout rhythm (full-bleed/poster vs. editorial grid vs. collage),
  type voice (serif display, grotesk 300 pt, condensed, mono), image strategy (full-bleed photo, cut-out
  collage, macro texture, type-as-image, 3-D still) and light (dark, light, mixed). Two directions that
  share two axes are one direction. **Different photos or crops and different slide layouts in each**: a
  recolour of the same slides is one direction.
- **The independent critic picks** (`scripts/critic.sh --pick samples`): it compares A/B/C with the
  yardsticks and writes pick.md: the winner or an ordered hybrid, and why the others lose.
- **pick.md + the winning slides are the binding style sheet** (style.md): grid, type sizes, palette,
  image strategy, the 5-7 compositions with their order. Every later slide cites one of them; changes go
  through style.md, never ad hoc. The winning sample slides go into the deck, the losers do not.
- **Sandboxed (critic.sh cannot start):** spawn a fresh subagent with references/critic-pick-prompt.md and the
  images; it ends pick.md with `<!-- signed: critic.sh subagent -->`. Never edit build.py or copy it to pass the gate.
- **Hard stop.** build.py refuses any deck over 8 slides without a pick.md signed by critic.sh. If the
  critic cannot start, END YOUR TURN: tell the user the three samples are ready for an independent pick.
  Writing or signing pick.md yourself is forbidden.
