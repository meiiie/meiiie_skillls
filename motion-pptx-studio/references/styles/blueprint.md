# blueprint — how a thing works, drawn as a drafting sheet

**Use for** product anatomy, architecture, systems, processes, "how it works" chapters.
**Palette** sheet `#0D2D52` with a 1/4 in minor grid and a major line every inch (`make_assets.py` ground `blueprint`),
hairlines `#E8F1FF`, labels `#B4CAE8`, ONE lit part `#FFB627`.
**Fonts** Space Grotesk (display) · Be Vietnam Pro (text) · JetBrains Mono (labels, sheet number).

## Layout grammar
- The object is the explanation (the "anatomy" idea, https://skills.wheresryan.sh/anatomy): draw it with
  `poly`, `rect`, `ellipse` and `line` shapes (never clip-art); parts are top-level groups named `!!part`.
- Left 55%: the object. Right 45%: callouts at the height of the part they name, joined by dotted leader lines.
- Words never sit inside the drawing; one amber part per frame, the one the speaker is talking about.
- Chrome is a title block bottom right (`SHEET 07/16`) and the scene name in mono top left.
- Processes are node-and-pipe diagrams (`diagram_video.py`): boxes, pills, cylinders for stores, arrows,
  dashed lines for optional inputs, amber dots for flow.

## Signature motion
- Assembled view (parts `drop` in, bottom first) → **Morph** to the exploded view (parts pull apart along the axis)
  → callouts `wipe` in along their leader lines, staggered 200 ms.
- The lit part breathes (`pulse` 1.06, loop). A drop or a flow dot runs a looping `path`.
- A process slide: the animated MP4 from `diagram_video.py` (nodes pop, pipes draw on, dots flow), then the
  same diagram as editable shapes with native effects on the next slide.

## Avoid
Isometric clip-art, icons standing in for parts, more than one lit colour, labels inside shapes.
