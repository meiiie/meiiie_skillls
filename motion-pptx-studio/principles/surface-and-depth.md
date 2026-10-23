# surface-and-depth
Great decks feel like made objects: paper, print, film or glass under a light. Weak decks look
like flat screens. The surface carries meaning, so choose it from the subject, never as decoration.
- **Visible at 1x.** Start from the recipe table, then push until the material reads on the
  contact sheet, not only at 2x zoom (`art_check.py` fine sigma >= 4 on empty areas). Do not weaken recipes "to be safe":
  quiet text areas are made with lighter layers locally, not by flattening the whole ground.
- **Chapters differ in layers, not only base colour:** e.g. paper tooth + laid lines, then halftone
  print, then light pool + riso. One recipe recoloured four times is one material.
- **Use one material per chapter.** Pick it from the subject's world: letter paper for the post,
  a printed star chart for the sky, lab glass for the experiment. Change the material or the
  temperature at chapter turns. Never change it slide by slide.
- **Texture every surface.** Panels, cards and bands get the SAME material as the ground in a
  shifted tone (`surface.ground` at the panel's size). A flat fill on a grainy ground reads as pasted on.
- **Light, not gradients.** One light source per slide: a light pool or a falloff from one side,
  and a soft vignette. Light makes depth and gives the eye a path to the hero.
- **Grain unifies the layers.** Put a faint grain on grounds, photos (`surface.py photo --grain`) and
  film frames, so everything sits in one world.
- **Keep text calm.** Lower the halftone, riso and mottle where text sits (about 0.3 under text
  panels). Body text needs contrast of 4.5:1 or more, so check it in greyscale.
- More: references/details/surface-and-depth.md (commands, flags, edge cases).
