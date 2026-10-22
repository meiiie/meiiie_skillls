#!/usr/bin/env python3
"""Reported fallback only (ManimGX impossible AND the user told, see principles/manimgx-first.md): a pure-Python film. Frames are drawn with Pillow and piped straight into ffmpeg
(no frame files on disk). Works in any harness that has python3 + Pillow + ffmpeg.

  python3 canvas_film.py FILM.py --out assets/film/NAME.mp4 [--w 1920 --h 810 --fps 30]

FILM.py defines   SECONDS = 12            and   def frame(t, c): ...   (t in seconds, c a Canvas below)
Canvas: c.W, c.H (always 1920 wide: design pixels), c.ease(u), c.lerp(a, b, u), c.u(t, t0, t1) (0..1 eased progress between t0 and t1),
        c.line(pts, color, width), c.poly(pts, fill, outline=None), c.circle(x, y, r, fill=None, outline=None, width=2),
        c.rect(x, y, w, h, fill), c.text(s, x, y, size_px, color, font='path.ttf', anchor='la'),
        c.camera(cx, cy, zoom): later calls are in WORLD pixels seen through a camera (move it: that is the motion).
Supersampled 2x for clean edges. Ends with film_check (duration, real motion, poster).
No ffmpeg? Use route 3: native PowerPoint motion paths and Morph (principles/film-is-the-core.md)."""
import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SS = 2


class Canvas:
    """Drawing space is ALWAYS 1920 x (1920 * h / w) design pixels (c.W, c.H), whatever the output size,
    so a quick low-resolution preview (--w 960) shows exactly the final composition."""
    def __init__(self, OW, OH, bg):
        self.OW, self.OH = OW, OH
        self.W, self.H, self.bg = 1920, round(1920 * OH / OW), bg
        self.k = SS * OW / 1920
        self.img = Image.new('RGB', (OW * SS, OH * SS), bg)
        self.d = ImageDraw.Draw(self.img)
        self.cam = (self.W / 2, self.H / 2, 1.0)
        self._fonts = {}

    @staticmethod
    def ease(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)

    @staticmethod
    def lerp(a, b, u):
        return a + (b - a) * u

    def u(self, t, t0, t1):
        return self.ease((t - t0) / max(1e-6, t1 - t0))

    def camera(self, cx, cy, zoom=1.0):
        self.cam = (cx, cy, zoom)

    def P(self, x, y):
        cx, cy, z = self.cam
        return ((x - cx) * z + self.W / 2) * self.k, ((y - cy) * z + self.H / 2) * self.k

    def line(self, pts, color, width=2):
        self.d.line([self.P(*p) for p in pts], fill=color, width=max(1, int(width * self.k)), joint='curve')

    def poly(self, pts, fill, outline=None, width=2):
        self.d.polygon([self.P(*p) for p in pts], fill=fill, outline=outline, width=max(1, int(width * self.k)))

    def rect(self, x, y, w, h, fill, outline=None, width=2):
        (a, b), (c_, d) = self.P(x, y), self.P(x + w, y + h)
        self.d.rectangle([min(a, c_), min(b, d), max(a, c_), max(b, d)], fill=fill, outline=outline, width=max(1, int(width * self.k)))

    def circle(self, x, y, r, fill=None, outline=None, width=2):
        (px, py), rr = self.P(x, y), r * self.cam[2] * self.k
        self.d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=fill, outline=outline, width=max(1, int(width * self.k)))

    def text(self, s, x, y, size, color, font=None, anchor='la', screen=False):
        """size in output pixels; screen=True ignores the camera (titles that must not move)."""
        key = (font, size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(font, max(1, int(size * self.k))) if font else ImageFont.load_default(size * self.k)
        p = (x * self.k, y * self.k) if screen else self.P(x, y)
        self.d.text(p, s, fill=color, font=self._fonts[key], anchor=anchor)

    def out(self):
        return self.img.resize((self.OW, self.OH), Image.LANCZOS).tobytes()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('film')
    ap.add_argument('--out', required=True)
    ap.add_argument('--w', type=int, default=1920)
    ap.add_argument('--h', type=int, default=810)
    ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    if not shutil.which('ffmpeg'):
        raise SystemExit('ffmpeg not found: build this moment with native motion paths + Morph instead (route 3), and say so')
    spec = importlib.util.spec_from_file_location('film', a.film)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bg = getattr(m, 'BG', '#FFFFFF')
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = int(m.SECONDS * a.fps)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{a.w}x{a.h}', '-r', str(a.fps),
                           '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', str(out)],
                          stdin=subprocess.PIPE)
    for i in range(n):
        c = Canvas(a.w, a.h, bg)
        m.frame(i / a.fps, c)
        ff.stdin.write(c.out())
    ff.stdin.close()
    if ff.wait():
        raise SystemExit('ffmpeg failed')
    sys.path.insert(0, str(HERE))
    import film_check
    errs, _ = film_check.check(out)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
