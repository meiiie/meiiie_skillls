# Architecture and process animations (v5)

Hand-built, never clip-art: the structure itself is the picture (books and scales are not an architecture).

## A. `diagram_video.py` (no extra install)
1. Write `design/<name>.json`: region on the slide, palette, font, nodes (`box|pill|db|circle`, one `lit`), edges
   (`straight|hv|vh`, `label`, `flow`, `dash`). Coordinates in inches, relative to the region.
2. `python $S/diagram_video.py design/brew.json --mp4 assets/brew.mp4 --poster assets/brew.poster.png --fragment design/brew-shapes.json`
3. Slide A: `{"type": "video", "path": "assets/brew.mp4", "poster": "assets/brew.poster.png", "loop": false, ...}` at the
   same region. Slide B (or instead, for Google Slides/Keynote/print): paste the fragment's shapes; they carry
   native animation (nodes zoom in staggered, pipes wipe in their direction, flow dots loop a motion path).
The poster is the last frame, so the static render, the print and the editable slide show the same picture.

## B. Manim / ManimGX (maths, physics, algorithms)
ManimGX (https://manimgx.academa.ai/) runs the Manim CE API on a Rust/wgpu renderer (CPU via lavapipe works);
tested on the box (v0.1.1, Python 3.13 venv): `pip install manimgx`, `manimgx render scene.py` → 1080p60 MP4.
Its wheel declares a mixed licence (MIT plus GPL/LGPL/OFL components); producing a video is fine, but
check the licence before redistributing the tool itself, and test Vietnamese text in your font before relying on it. Classic Manim CE (`pip install manim`, needs Cairo/ffmpeg/LaTeX) is the fallback.
```python
from manim import *
class Drip(Scene):
    def construct(self):
        phin = RoundedRectangle(width=2, height=1.2, corner_radius=0.1, color=WHITE)
        drop = Dot(color=YELLOW).next_to(phin, DOWN, buff=0.05)
        self.play(Create(phin))
        self.play(drop.animate.shift(DOWN * 2), run_time=1.2, rate_func=rush_into)
```
Insert the MP4 as a `video` shape with a poster frame; keep an editable static version of the final frame
(shapes) on the next slide. State in the hand-off which slides carry rendered video.

## C. Optional generated imagery
If the harness has an image generator (e.g. Codex CLI), use it only for textures or backgrounds the user approves,
label it as generated in CREDITS, and never for the object being explained.
