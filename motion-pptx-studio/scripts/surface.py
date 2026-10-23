#!/usr/bin/env python3
"""Surfaces: procedural grounds and photo treatments, tinted to YOUR palette (no colours live here).

  python3 surface.py ground --base '#0B1324' [layers...] --out assets/grounds/night.jpg [--w 2400 --h 1350 --seed 1]
  python3 surface.py photo IN.jpg --out OUT.jpg [--duotone '#0B1324,#F2C14E'] [--grade lift,gamma,gain] [--grain 0.04]
Layers (each optional; strengths 0..1; order of application is fixed: tone -> light -> pattern -> grain):
  --mottle A[,SCALE]        low-frequency tonal unevenness (paper, plaster, sky): A~0.03-0.08
  --tooth A                 fine paper tooth (anisotropic, a little horizontal)          ~0.03-0.06
  --fibers N                N sparse paper fibres per megapixel                          ~4-12
  --laid A[,PITCH]          laid/chain lines of writing paper (horizontal, PITCH px)    ~0.02
  --light X,Y,R,A[,#hex]    soft light pool at (X,Y) in 0..1, radius R (x width), lift A, optional tint
  --falloff A[,ANGLE]       directional light falloff (a lamp off one side), ANGLE deg (0 = from left)
  --vignette A[,POWER]      darkened corners; POWER 2 soft .. 4 tight
  --halftone A,CELL,ANG[,#ink]  dot screen of the LIGHT field (pools + falloff) in ink: print, star chart, newsprint
  --riso A,#ink[,DX,DY]     a misregistered second-ink glow (two-colour risograph feel)
  --grain A[,SIZE]          film/print grain, strongest in the midtones; SIZE>1 clumps it  ~0.02-0.06
Every ground is dithered (no banding on gradients) and saved as JPEG q90 (or PNG by extension).
Python: from surface import ground; ground(W, H, base, seed=1, mottle=(0.05, 300), grain=(0.04, 1), ...) -> PIL.Image
"""
import argparse
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def soft(a, k):
    """Blur a float field by about k px (down- then up-sampling; PIL cannot filter float images)."""
    H, W = a.shape
    k = max(1.0, k)
    small = Image.fromarray(a.astype(np.float32), 'F').resize((max(2, int(W / k)), max(2, int(H / k))), Image.BOX)
    return np.asarray(small.resize((W, H), Image.BICUBIC))


def fbm(H, W, scale, rng, octaves=4):
    """Fractal value noise in -1..1 (sum of upsampled gaussian fields, halving the scale each octave)."""
    out, amp, tot = np.zeros((H, W)), 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        n = rng.normal(0, 1, (H // s + 3, W // s + 3)).astype(np.float32)
        im = Image.fromarray(n, 'F').resize((W + 2 * s, H + 2 * s), Image.BICUBIC)
        a = np.asarray(im)[s:s + H, s:s + W]
        out += amp * a
        tot += amp
        amp *= 0.5
    out /= tot
    return np.clip(out / (3 * out.std() + 1e-9), -1, 1)


def ground(W, H, base, seed=1, mottle=None, tooth=None, fibers=None, laid=None, light=(), falloff=None,
           vignette=None, halftone=None, riso=None, grain=None):
    rng = np.random.default_rng(seed)
    b = to_lin(rgb(base))
    img = np.broadcast_to(b, (H, W, 3)).copy()
    lum = np.ones((H, W))                                   # multiplicative light field (1 = base)
    field = np.zeros((H, W))                                # light only (pools + falloff): drives the halftone
    if mottle:
        a, sc = (mottle + (W / 6,))[:2] if isinstance(mottle, tuple) else (mottle, W / 6)
        lum *= 1 + a * fbm(H, W, sc, rng)
    for L in light:
        x, y, r, a = L[:4]
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.hypot((xx - x * W) / (r * W), (yy - y * H) / (r * W))
        pool = np.exp(-d ** 2 * 2.2)
        if len(L) > 4 and L[4]:
            img += to_lin(rgb(L[4]))[None, None, :] * (pool * a * 0.35)[..., None]   # tinted light (warm lamp, cold sky)
        lum *= 1 + a * pool
        field += pool
    if falloff:
        a, ang = (falloff + (0,))[:2] if isinstance(falloff, tuple) else (falloff, 0)
        yy, xx = np.mgrid[0:H, 0:W]
        t = (math.cos(math.radians(ang)) * xx / W + math.sin(math.radians(ang)) * yy / H)
        t = (t - t.min()) / (np.ptp(t) + 1e-9)
        lum *= 1 + a * (0.5 - t) * 2 * (0.5 + 0.5 * (1 - t))
        field += 1 - t
    if vignette:
        a, p = (vignette + (2.5,))[:2] if isinstance(vignette, tuple) else (vignette, 2.5)
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / math.sqrt(2)
        lum *= 1 - a * np.clip(r, 0, 1) ** p
    img *= lum[..., None]
    if tooth:
        n = rng.normal(0, 1, (H, W)).astype(np.float32)
        n = np.asarray(Image.fromarray(n, 'F').resize((W // 3, H), Image.BOX).resize((W, H), Image.BICUBIC)) + 0.4 * n
        img *= (1 + tooth * n / (n.std() + 1e-9) * 0.5)[..., None]
    if laid:
        a, pitch = (laid + (9,))[:2] if isinstance(laid, tuple) else (laid, 9)
        yy = np.arange(H)[:, None]
        wob = fbm(H, W, W / 3, rng, 2) * 1.5
        lines = 0.5 + 0.5 * np.cos(2 * math.pi * (yy + wob) / pitch)
        img *= (1 - a * lines ** 6)[..., None]
    if halftone:
        a, cell, ang = halftone[:3]
        ink = to_lin(rgb(halftone[3])) if len(halftone) > 3 and halftone[3] else b * 0.5
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        th = math.radians(ang)
        u = xx * math.cos(th) + yy * math.sin(th)
        v = -xx * math.sin(th) + yy * math.cos(th)
        fu, fv = (u % cell) - cell / 2, (v % cell) - cell / 2
        d = np.hypot(fu, fv)
        val = np.clip((field - field.min()) / (np.ptp(field) + 1e-9), 0, 1) ** 1.3   # dots grow where the light is
        rad = np.sqrt(val) * cell * 0.5
        cov = np.clip(rad - d + 0.5, 0, 1) * a
        img = img * (1 - cov[..., None]) + ink[None, None, :] * cov[..., None]
    if riso:
        a, ink = riso[0], to_lin(rgb(riso[1]))
        dx, dy = (riso[2], riso[3]) if len(riso) > 3 else (6, -4)
        m = np.clip(0.5 + 0.9 * fbm(H, W, W / 4, rng, 3), 0, 1) ** 2
        m = np.roll(np.roll(m, dx, 1), dy, 0)
        speck = rng.random((H, W)) > 0.06                         # ink skips
        cov = (m * a * speck)
        img = img * (1 - cov[..., None]) + np.maximum(img * ink * 1.6, ink * 0.25) * cov[..., None]   # overprint
    if fibers:
        lay = Image.new('L', (W, H), 0)
        dr = ImageDraw.Draw(lay)
        for _ in range(int(fibers * W * H / 1e6)):
            x, y = rng.random() * W, rng.random() * H
            ang, ln = rng.random() * math.pi, 8 + rng.random() * 40
            pts = [(x + math.cos(ang) * t * ln + rng.normal(0, 1.2), y + math.sin(ang) * t * ln + rng.normal(0, 1.2)) for t in np.linspace(0, 1, 6)]
            dr.line(pts, fill=int(40 + rng.random() * 60), width=1)
        f = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.5)), float) / 255
        img *= (1 - 0.35 * f * (1 if img.mean() > 0.2 else -1))[..., None]   # darker on light paper, lighter on dark
    out = to_srgb(img)
    if grain:
        a, size = (grain + (1,))[:2] if isinstance(grain, tuple) else (grain, 1)
        n = rng.normal(0, 1, (H, W)).astype(np.float32)
        if size > 1:
            n = soft(n, size) + 0.3 * n
            n /= n.std() + 1e-9
        l = out.mean(-1)
        w = 0.35 + 2.6 * l * (1 - l)                                # midtones carry the most grain
        out = out + (a * n * w)[..., None]
    out = out + (rng.random(out.shape) - rng.random(out.shape)) / 255   # triangular dither: no banding
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype('uint8'))


def photo(src, duotone=None, grade=None, grain=None, seed=1):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im, float) / 255
    if grade:
        lift, gamma, gain = grade
        a = np.clip(lift + (gain - lift) * a, 0, 1) ** (1 / gamma)
    if duotone:
        d, l = to_lin(rgb(duotone[0])), to_lin(rgb(duotone[1]))
        y = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
        a = to_srgb(d[None, None] * (1 - y[..., None]) + l[None, None] * y[..., None])
    if grain:
        rng = np.random.default_rng(seed)
        l = a.mean(-1)
        a = a + (grain * rng.normal(0, 1, l.shape) * (0.35 + 2.6 * l * (1 - l)))[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype('uint8'))


def _nums(s):
    out = []
    for p in s.split(','):
        p = p.strip()
        out.append(p if p.startswith('#') else float(p))
    return tuple(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('ground')
    g.add_argument('--base', required=True)
    g.add_argument('--out', required=True)
    g.add_argument('--w', type=int, default=2400)
    g.add_argument('--h', type=int, default=1350)
    g.add_argument('--seed', type=int, default=1)
    for k in ('mottle', 'tooth', 'fibers', 'laid', 'falloff', 'vignette', 'halftone', 'riso', 'grain'):
        g.add_argument('--' + k)
    g.add_argument('--light', action='append', default=[])
    p = sub.add_parser('photo')
    p.add_argument('src')
    p.add_argument('--out', required=True)
    p.add_argument('--duotone')
    p.add_argument('--grade')
    p.add_argument('--grain', type=float)
    a = ap.parse_args()
    if a.cmd == 'ground':
        kw = {}
        for k in ('mottle', 'laid', 'falloff', 'vignette', 'halftone', 'riso', 'grain'):
            v = getattr(a, k)
            if v:
                t = _nums(v)
                kw[k] = t if len(t) > 1 or k in ('halftone', 'riso') else t[0]
        if a.tooth:
            kw['tooth'] = float(a.tooth)
        if a.fibers:
            kw['fibers'] = float(a.fibers)
        kw['light'] = [_nums(s) for s in a.light]
        im = ground(a.w, a.h, a.base, a.seed, **kw)
    else:
        im = photo(a.src, duotone=a.duotone.split(',') if a.duotone else None,
                   grade=tuple(float(x) for x in a.grade.split(',')) if a.grade else None, grain=a.grain)
    if a.out.lower().endswith('.png'):
        im.save(a.out)
    else:
        im.save(a.out, quality=90, subsampling=0)
    print('wrote', a.out, im.size)


if __name__ == '__main__':
    main()
