# Construction motion (v5.5): Anatomy and Manim rules as native PowerPoint

A diagram that fades in says "here is a picture". A diagram that is **built** says "this is how it is
made", and the build order is the explanation. v5.5 takes the rules of two tools the skill already used
for films, Anatomy (isometric machines, https://skills.wheresryan.sh/anatomy) and Manim/ManimGX (animated
mathematics), and applies them to native, editable slide shapes through the `construct` component
(`scripts/construct.py`, spec in `build-engine.md` A.3b2). Films (`signature-moments.md`) are still the tool
for continuous motion; `construct` is for the many diagrams that should stay editable and Morph.

## 1. The rules

From **Anatomy**:
1. **The object is the explanation.** Draw the real thing (a stage, a lighthouse, a peninsula), not a metaphor.
2. **Every part sits on another** (`on`). Nothing floats; a label belongs to the part it names.
3. **Build order = how it is made**: base → structure → mechanism → controls → the one lit subject
   (`layer`), then labels. `step` groups parts that are made together (nine engines at once).
4. **One camera** (isometric 30°, `iso_box` / `iso_cyl`), solids in **four tones by facing** (top light,
   left mid, right dark, line darkest), so form reads without outlines or gradients.
5. **Exactly one lit accent per frame** (`lit`; parts sharing a `group` count as one). The build stops if there are two.
6. **No words inside the drawing**: labels sit beside it, aligned in a column, in the label role.
7. **Detail rewards a 4× look**; lines end on something; motion is calm and time-based.

From **Manim** (the verbs, and how each becomes native PowerPoint):

| Manim | Meaning | `construct` verb | PowerPoint |
|---|---|---|---|
| `Create` | a stroke is drawn along its path | `create` (lines, open polys, arcs) | Wipe from the stroke's start side |
| `Create(Circle)` | a ring is swept | `sweep` (unfilled ellipse) | Wheel, 1 spoke (simulated as a clockwise sweep) |
| `GrowFromEdge` | a solid grows out of what it rests on | `grow` (solids) | Stretch (preset 17) from the contact edge |
| `GrowFromCenter` | a part inside another appears from its centre | `zoom` | Zoom |
| `Write` | text is written | `write` (labels) | letter-by-letter type |
| `LaggedStart(lag_ratio)` | parts follow each other, overlapping | automatic | delays fitted to `total_ms` |
| `Indicate` | point at a part | `indicate: [ids]` | scale 1.14 pulse, auto-reverse |
| `MoveAlongPath` | an object travels a drawn path | `trace` | motion path in model units |
| `Transform` | a part changes shape or place | `states` on the next slide | Morph (same `!!` names) |
| `MovingCamera` | the frame moves over a still drawing | `camera` on the next slide | Morph: every part moves and scales together |

The verb is chosen from the part (`choose_verb`); set `verb`/`dir` only to override it.

## 2. Camera and states are slides

Write the same component on consecutive slides with `"morph": "byObject"` (or the Morph transition):
```json
{"type": "construct", "name": "f9", "parts": PARTS, "state": "rest", "reveal": true, "total_ms": 5200}
{"type": "construct", "name": "f9", "parts": PARTS, "state": "fins", "camera": {"focus": "inter", "zoom": 3.4}, "indicate": ["finx", "finy"]}
{"type": "construct", "name": "f9", "parts": PARTS, "state": "land", "camera": {"focus": [0, -2], "zoom": 1.9}}
```
The fit is computed from the **rest** geometry, so every state and camera shares one coordinate system and
Morph moves only what changed (a fin opening) or everything together (the camera). A part's `states` entry
can change `box`/`at`/`points`, `lit`, `fill` or `hide`.

Off-frame parts are not clipped by PowerPoint. Design for it: give the base (sea, ground plate) a large
extent so a zoom keeps the page covered, and put the words on a card above the drawing.

## 3. Choosing what to construct

- **A machine or product**: built bottom-up, then the camera visits the parts that change.
- **A place**: the sea, the land, the coast drawn, the hills grown, the route, then the camera sails to the subject.
- **A building or monument**: courses stacked with their years written as each lands; the light last.
- **A process or a path**: the path is drawn, the stages are dotted on it, then the object flies it (`trace`).
- **Data**: bars grow from the axis, the axis is drawn first, the one number is lit.

Every deck carries at least one; a deck with a mechanism story carries the build, a camera move and a state change.

## 4. Simulation and limits

`preview_motion.py` renders stretch (anchored one-axis growth), the wheel as a sweep, letter typing and
Morph as an interpolated cross-fade of matched shapes; label the video as a SIMULATION. LibreOffice renders
show the end state only. Check the real timing in PowerPoint 365.
