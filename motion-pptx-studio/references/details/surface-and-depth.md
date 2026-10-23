# surface-and-depth.md - details (moved from principles/ in v6.22)
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
