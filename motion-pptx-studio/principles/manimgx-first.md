# manimgx-first
Films are rendered with ManimGX (docs: https://manimgx.academa.ai, for agents: /llms.txt).
**Install it and pass the smoke test BEFORE you start designing.** It is not the `manim` package.
ManimGX needs Python 3.13 or newer. It does not need LaTeX, ffmpeg, cairo, pango or a GPU: the Linux
wheel brings its own CPU Vulkan renderer (lavapipe). The install is ~330 MB.
Try these in order and stop at the first one that works:
1. `python3 -V` is 3.13+: `python3 -m venv .mgx && .mgx/bin/pip install manimgx`, then `PATH=$PWD/.mgx/bin:$PATH`.
2. Python is older (ChatGPT ships 3.11, where pip finds "no matching distribution"):
   `pip install uv && uv tool install --python 3.14 manimgx` (uv fetches its own Python).
- **Size:** every film `-r 1920x1080 --fps 30` (16:9 full-bleed); tests at `-r 960x540 --fps 15`.
- **Smoke test first** (install fallbacks, smoke scene, flags): see the details file. Never fall back to `manim`.
- More: references/details/manimgx-first.md (commands, flags, edge cases).
