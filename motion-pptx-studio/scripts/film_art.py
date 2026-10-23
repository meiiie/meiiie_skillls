#!/usr/bin/env python3
"""v6.21 art quality of a film's stills (toy-render detector). Measures, the eye decides; fails weak films.
  python3 film_art.py FILM.mp4 [...] [--strict]
Per film, 6 stills: flat = share of subject pixels with no light/texture variation in a 5x5 window (flat-shaded
faces = toy blocks); fill = share of frame that differs from the ground. FAIL flat > .30; WARN fill < .30.
Calibrated: Khí áp films .09-.27, SpaceX .09, San hô .05-.22 pass; R14 bike ride .49 / machine .36, coffee
cube banks .34 / .81 fail."""
import sys, subprocess, json
import numpy as np
from PIL import Image, ImageFilter

def stills(f, n=6):
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                             capture_output=True, text=True).stdout or 1)
    out = []
    for k in range(n):
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(d * (k + .5) / n), '-i', f, '-frames:v', '1',
                              '-vf', 'scale=480:270', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        if len(raw) == 480 * 270 * 3: out.append(Image.frombytes('RGB', (480, 270), raw))
    return out

def measure(im):
    a = np.asarray(im, float); g = im.convert('L')
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    s = np.abs(a - np.median(border, 0)).sum(2) > 40; fill = s.mean()
    if s.sum() < 500: return fill, 1.0
    mx = np.asarray(g.filter(ImageFilter.MaxFilter(5)), float); mn = np.asarray(g.filter(ImageFilter.MinFilter(5)), float)
    return fill, float(((mx - mn) <= 3)[s].mean())   # flat = subject pixels with no light/texture variation

def main():
    files = [x for x in sys.argv[1:] if not x.startswith('--')]; bad = []
    for f in files:
        S = stills(f)
        if not S: print('film_art: cannot read', f); continue
        fill, flat = np.median(np.array([measure(i) for i in S]), 0)
        v = 'FAIL' if flat > .30 else ('WARN' if fill < .30 else 'ok')
        print(f"{v:4} {f}: flat-shaded {flat:.2f} (max .30) fill {fill:.2f} (warn < .30)" +
              (' - toy render: light it (key + rim, falloff, shadows), give surfaces a material/texture, push the camera in (cinematic-manimgx)' if v == 'FAIL' else
               (' - small subject: push the camera in' if v == 'WARN' else '')))
        if v == 'FAIL': bad.append(f)
    sys.exit(1 if bad else 0)

if __name__ == '__main__': main()
