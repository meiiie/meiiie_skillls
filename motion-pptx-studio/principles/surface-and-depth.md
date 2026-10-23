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
- **Bake the texture.** Render it into the JPEG background with `scripts/surface.py`: about 0.8 MB
  for each 2400 px ground. Do not use stacked transparent PNGs. Reuse one ground per chapter.
- **Don't let texture become the content.** It should be felt at thumbnail size and seen up
  close. Grunge, scratches, gingham or stickers that are unrelated to the subject are cliché
  (no-ai-cliche).

Starting recipes. Tint them to your palette and tune them by looking:
| material | surface.py ground layers |
|---|---|
| letter paper | `--mottle .07,500 --tooth .08 --fibers 10 --laid .03,7 --light .22,.12,.9,.07 --vignette .18,2.2 --grain .035` |
| night sky | `--mottle .10,700 --light .85,.12,.5,.55,#<cool lift> --vignette .45 --grain .035` |
| printed chart | `--mottle .06,600 --light .92,.5,.55,.35 --halftone .9,18,30,#<ink> --vignette .3 --grain .03` |
| lab / clean | `--falloff .10,20 --light .5,0,1,.05 --tooth .02 --vignette .10 --grain .02` |
| ember / heat | `--mottle .10,600 --light .5,1.1,.7,.55,#<warm> --riso .25,#<hot>,9,-6 --vignette .45 --grain .05,1.6` |
A deck.json `"grounds"` entry can be a recipe dict with the same keys (references/deck-json.md).
