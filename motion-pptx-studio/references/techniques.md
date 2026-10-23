# techniques (native, no Morph required) - pick by the slide's purpose, verify in the render
| technique | use when | how | verify |
|---|---|---|---|
| full-bleed photo + falloff | a place, a scale, an opener | background picture + gradient on the type side (photo-treatment) | type contrast 4.5:1 |
| cut-out over type | an object is the hero | photo_layout.py cutout; picture above a 250-400 pt word, overlapping it | edge clean at 2x |
| image-filled word | the word IS the subject (SAN HÔ, TẾT) | pptx_fx.text_fill_image on >= 200 pt heavy type | PowerPoint only: LibreOffice renders solid, so also give it a photo behind |
| shape mask | a portrait, a porthole, a sequence | pptx_fx.mask_picture (ellipse, hexagon, flowChartDelay) or photo_layout mask | subject inside the mask |
| depth parallax (classic) | a landscape with depth, once per deck | 3 oversize layers bg/mid/cut-out fg; pptx_fx.parallax_effects -> motion paths 1:2.5:6 | no edge shows at path end |
| Ken-Burns push-in | a quiet hero photo while you speak | pptx_fx.push_in_effects (grow 1.08-1.15 over 6-10 s) | stays sharp (source >= 2x) |
| keyframe sequence | every slide | each component its own entrance/path/emphasis in story order (native-keyframes) | anim_check |
| embedded film | the mechanism, the process | ManimGX / Anatomy mp4 full-bleed or >= 50 % (film-language) | film_check |
| typographic poster | abstract hero | one word/number 250-400 pt cropped by the frame ON a photo/material | reads in 3 s |
| lit 3-D still | abstract structure | ManimGX 3-D scene rendered as a still with light | not iso blocks |
| Morph (optional only) | 365 audiences, extra polish | compat "dual"; the slide must still read without it | open in safe mode |
| GLB 3-D model (optional) | a product the audience should turn | PowerPoint Insert > 3D Model; poster image fallback for other apps | poster present |
Sources: support.microsoft.com Morph tips; kevinstratvert.com parallax; stylus.co.za text mask; Microsoft 3D guidelines.
