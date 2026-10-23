# manimgx-first
Films are rendered with ManimGX (docs: https://manimgx.academa.ai, for agents: /llms.txt).
**Install it and pass the smoke test BEFORE you start designing.** It is not the `manim` package.
ManimGX needs Python 3.13 or newer. It does not need LaTeX, ffmpeg, cairo, pango or a GPU: the Linux
wheel brings its own CPU Vulkan renderer (lavapipe). The install is ~330 MB.
Try these in order and stop at the first one that works:
1. `python3 -V` is 3.13+: `python3 -m venv .mgx && .mgx/bin/pip install manimgx`, then `PATH=$PWD/.mgx/bin:$PATH`.
2. Python is older (ChatGPT ships 3.11, where pip finds "no matching distribution"):
   `pip install uv && uv tool install --python 3.14 manimgx` (uv fetches its own Python).
3. Still blocked (no internet for uv's Python download): use the standalone binary, which has
   its own Python, needs no network and needs glibc 2.28+. Fetch `manimgx-linux-x86_64.tar.gz`
   (238 MB) from github.com/academa-labs/manimgx/releases (the latest release), with
   container.download, curl, or ask the user to upload it. Then
   `tar xzf manimgx-linux-x86_64.tar.gz && export PATH=$PWD:$PATH`. Its first run unpacks
   ~0.9 GB into ~/.cache/pyapp.
Smoke test: save the scene below as smoke.py, then run `manimgx render smoke.py -r 1280x720 --fps 30`.
It should write Smoke.mp4 in about 2 s.
```python
import manimgx as m
m.config.background_color = "#101418"
class Smoke(m.Scene):
    def construct(self) -> None:
        t = m.Text("ManimGX OK", font_size=72, color="#F2EDE4")
        bar = m.Rectangle(width=6, height=0.3, fill_opacity=1, color="#E8743B").next_to(t, m.DOWN)
        self.play(m.Write(t), m.GrowFromEdge(bar, m.LEFT), run_time=1.5)
        self.wait(0.5)
```
Render settings:
- **Drafts:** `-r 1280x540 --fps 15`.
- **Final:** `-r 2560x1080 --fps 30 --preset veryfast -o assets/film/NAME.mp4`.
- **Check layout:** `manimgx inspect film.py` (exit 1 means problems).
- **Time limit per call:** render one film per call, or run it in the background (`nohup`) and poll.
**If every route fails, STOP and tell the user.** Report the exact error and what you need from them
(an upload of the binary, or a Python 3.13 host). Only go on with the web-film tiers
if the user agrees, and write the reason in NOTES.md. Never fall back silently.
Set up Anatomy in the same step 0 (anatomy-first, https://skills.wheresryan.sh/anatomy).
