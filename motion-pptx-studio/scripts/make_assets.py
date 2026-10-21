"""Asset kit: grounds, foil finishes, layered parts, photo treatment, glows and patterns.

Every deck needs the same raw materials: a ground that is not a flat fill, a hero object
in one consistent finish, parts that Morph can assemble, photos graded into the palette,
and a few textures. Make them here instead of improvising them per deck.

  python3 make_assets.py ground  --kind lacquer|noir|paper|clean|halftone|flat --base "#140B08" [--tone "#2B1710"]
                                [--crackle 0.5] [--grain 0.05] [--vignette 0.4] [--style noir-product --name main] --out ground.jpg
  python3 make_assets.py foil    SRC.svg|SRC.png --finish gold|silver|copper|bronze|ink|chalk|neon|metal --out hero.png
                                [--color "#D9B26A"] [--size 1600] [--seed 3]
  python3 make_assets.py layers  object.svg --out-dir assets/parts [--finish gold]     # one PNG per top-level <g id>
  python3 make_assets.py photo   SRC.jpg --out assets/hero.jpg --mode duotone|mono|sepia|grade|color
                                [--colors "#140B08,#E2BE7C"] [--aspect 16:9] [--focus 0.5,0.4] [--vignette 0.3]
                                [--grain 0.02] [--pair] [--min-size 2400]
  python3 make_assets.py glow    --color "#FFB020" --size 1600 --out glow.png [--softness 0.35]
  python3 make_assets.py pattern --kind woven|dots|stripes|hatch|chevron|grid --color "#D9B26A" --size 2400x300
                                [--finish gold] --out band.png

Drawings: write the object as an SVG in black on a transparent canvas, one <g id="part">
per moving part, all parts on the SAME canvas size so they line up when placed at the
same box. `layers` renders each part separately with the finish; place every part with
the same x/y/w/h in deck.json and Morph assembles them.
SVG rendering needs cairosvg (pip) or rsvg-convert (librsvg).
"""
import argparse
import io
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
STYLES = HERE.parent / 'assets' / 'styles'

FINISHES = {
    'gold': ((248, 218, 146), (150, 104, 40)),
    'silver': ((238, 241, 245), (118, 124, 134)),
    'copper': ((242, 172, 122), (118, 58, 30)),
    'bronze': ((222, 182, 112), (98, 68, 34)),
}


def hexrgb(h):
    h = h.strip().lstrip('#')
    if len(h) != 6:
        raise SystemExit(f'bad colour {h!r}: use #RRGGBB')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- noise helpers

def fractal(w, h, rng, octaves=5, base=4, persistence=0.55):
    """Smooth value noise in 0..1 from upscaled random grids (no scipy needed)."""
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gw, gh = max(2, int(base * 2 ** o * w / max(w, h))), max(2, int(base * 2 ** o * h / max(w, h)))
        grid = (rng.random((gh, gw)) * 255).astype(np.uint8)
        up = np.asarray(Image.fromarray(grid).resize((w, h), Image.BICUBIC), np.float32) / 255
        acc += up * amp
        tot += amp
        amp *= persistence
    acc /= tot
    return (acc - acc.min()) / max(1e-6, np.ptp(acc))


def streaks(w, h, rng, vertical=True, strength=1.0):
    """Anisotropic brush streaks."""
    small = rng.random((h // 8 if not vertical else 8, 8 if not vertical else w // 8)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255
    return (a - 0.5) * strength


def vignette(w, h, amount):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return 1 - amount * np.clip(d, 0, 1) ** 2


def voronoi_cracks(w, h, rng, cell=90, width=1.6):
    """Distance to the nearest Voronoi edge, as a crack mask (1 on the crack)."""
    sw, sh = w // 2, h // 2
    n = max(8, int(sw * sh / (cell / 2) ** 2))
    pts = rng.random((n, 2)) * [sw, sh]
    yy, xx = np.mgrid[0:sh, 0:sw]
    q = np.stack([xx.ravel(), yy.ravel()], 1).astype(np.float32)
    try:
        from scipy.spatial import cKDTree
        d, _ = cKDTree(pts).query(q, k=2)
    except ImportError:  # brute force in chunks
        d = np.empty((len(q), 2), np.float32)
        for i in range(0, len(q), 20000):
            dd = np.sqrt(((q[i:i + 20000, None, :] - pts[None, :, :]) ** 2).sum(-1))
            d[i:i + 20000] = np.sort(dd, 1)[:, :2]
    edge = (d[:, 1] - d[:, 0]).reshape(sh, sw)
    m = np.clip(1 - edge / width, 0, 1).astype(np.float32)
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255


# ---------------------------------------------------------------- grounds

def ground(kind='lacquer', base='#140B08', tone=None, size=(2400, 1350), grain=0.04, vignette_amt=0.4,
           seed=1, crackle=0.0, lift=(0.75, 0.2), dots=0.0, grid=0.0, grid_alpha=0.05, dot=0.16, **_):
    """Return an RGB PIL image: a ground that reads as a material, never a flat fill.
    kinds: lacquer noir paper clean halftone flat blueprint mesh scanline."""
    w, h = size
    rng = np.random.default_rng(seed)
    b = np.array(hexrgb(base), np.float32)
    t = np.array(hexrgb(tone), np.float32) if tone else b * 1.25
    img = np.zeros((h, w, 3), np.float32) + b
    if kind == 'lacquer':
        cloud = fractal(w, h, rng, octaves=5, base=3)
        img = b + (t - b) * cloud[..., None] * 0.9
        img *= (1 + streaks(w, h, rng, vertical=True, strength=0.08))[..., None]
        if crackle:
            cr = voronoi_cracks(w, h, rng, cell=110)
            img *= (1 - 0.45 * crackle * cr)[..., None]
        img *= vignette(w, h, vignette_amt)[..., None]
    elif kind == 'noir':
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        lx, ly = lift
        d = np.sqrt(((xx / w - lx) * (w / h)) ** 2 + (yy / h - ly) ** 2)
        g = np.exp(-(d / 0.75) ** 2)
        img = b + (t - b) * g[..., None]
        img *= (1 + 0.04 * (fractal(w, h, rng, 4, 3) - 0.5))[..., None]
        if dots:
            step = int(w / 13.333 * 0.25)  # a dot every quarter inch
            m = np.zeros((h, w), np.float32)
            m[step // 2::step, step // 2::step] = 1
            m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
            img += (255 - img) * (m * dots)[..., None] * 0.6
        img *= vignette(w, h, vignette_amt * 0.6)[..., None]
    elif kind == 'paper':
        cloud = fractal(w, h, rng, octaves=6, base=5)
        img = b + (t - b) * (cloud[..., None] * 0.55)
        fib = Image.new('L', (w, h), 0)
        from PIL import ImageDraw
        dr = ImageDraw.Draw(fib)
        for _ in range(int(w * h / 900)):
            x, y = rng.random() * w, rng.random() * h
            ang, ln = rng.random() * math.pi, 6 + rng.random() * 26
            dr.line([(x, y), (x + math.cos(ang) * ln, y + math.sin(ang) * ln)], fill=int(40 + rng.random() * 70), width=1)
        f = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
        sign = 1 if b.mean() < 128 else -1
        img += sign * f[..., None] * 18
        img *= vignette(w, h, vignette_amt * 0.35)[..., None]
    elif kind == 'clean':
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        img = b + (t - b) * yy * 0.6 + np.zeros((h, w, 3), np.float32)
        if grid:
            step = int(w / 13.333 * grid)
            m = np.zeros((h, w), np.float32)
            m[:, ::step] = 1
            m[::step, :] = 1
            ink = 255 if b.mean() < 128 else 0
            img += (ink - img) * (m * grid_alpha)[..., None]
    elif kind == 'halftone':
        img = b + np.zeros((h, w, 3), np.float32)
        step = int(w / 13.333 * 0.22)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx = (xx % step) - step / 2
        cy = (yy % step) - step / 2
        r = (dot * step) * (0.25 + 0.75 * (xx / w * 0.6 + (1 - yy / h) * 0.4))
        m = np.clip(r - np.sqrt(cx ** 2 + cy ** 2) + 0.5, 0, 1)
        img += (t - img) * m[..., None]
    elif kind == 'flat':
        cloud = fractal(w, h, rng, octaves=3, base=2)
        img = b + (t - b) * cloud[..., None] * 0.5
    elif kind == 'blueprint':
        # drafting sheet: minor grid every `grid` inches, a major line every 4th, a soft centre lift
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx / w - 0.5) * (w / h)) ** 2 + (yy / h - 0.45) ** 2)
        img = b + (t - b) * np.exp(-(d / 0.9) ** 2)[..., None]
        step = max(4, int(w / 13.333 * (grid or 0.25)))
        m = np.zeros((h, w), np.float32)
        m[:, ::step] = grid_alpha or 0.07
        m[::step, :] = grid_alpha or 0.07
        m[:, ::step * 4] = 2.2 * (grid_alpha or 0.07)
        m[::step * 4, :] = 2.2 * (grid_alpha or 0.07)
        ink = 255 if b.mean() < 128 else 0
        img += (ink - img) * m[..., None]
    elif kind == 'mesh':
        # glass/tech: two or three soft colour fields on a dark base (tone, plus `blobs` hex list)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) / h
        img = b + np.zeros((h, w, 3), np.float32)
        cols = [t] + [np.array(hexrgb(c), np.float32) for c in (_.get('blobs') or [])]
        for c in cols:
            cx, cy, r = rng.random() * w / h, rng.random(), 0.35 + rng.random() * 0.35
            g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2))
            img += (c - img) * (g * 0.75)[..., None]
        img *= vignette(w, h, vignette_amt * 0.5)[..., None]
    elif kind == 'scanline':
        # CRT terminal: phosphor glow in the middle, horizontal scanlines
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx / w - 0.5) * (w / h)) ** 2 + (yy / h - 0.5) ** 2)
        img = b + (t - b) * np.exp(-(d / 0.8) ** 2)[..., None]
        period = max(3, int(h / 270))
        img *= (1 - 0.18 * ((yy.astype(int) % period) == 0))[..., None]
        img *= vignette(w, h, vignette_amt)[..., None]
    else:
        raise SystemExit(f'unknown ground kind {kind!r}')
    if grain:
        img += rng.normal(0, 255 * grain, (h, w, 1)).astype(np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')


def style_ground(style, name, size=(2400, 1350)):
    data = json.loads(Path(style if str(style).endswith('.json') else STYLES / f'{style}.json').read_text(encoding='utf-8'))
    rec = dict(data['grounds'][name])
    rec['vignette_amt'] = rec.pop('vignette', 0.4)
    return ground(size=size, **rec)


# ---------------------------------------------------------------- SVG + masks

def svg_to_png(svg_bytes, w=None, h=None):
    try:
        import cairosvg
        kw = {}
        if w:
            kw['output_width'] = w
        if h:
            kw['output_height'] = h
        return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_bytes, **kw))).convert('RGBA')
    except ImportError:
        exe = shutil.which('rsvg-convert')
        if not exe:
            raise SystemExit('SVG needs cairosvg (pip install cairosvg) or rsvg-convert (librsvg)')
        args = [exe, '-f', 'png'] + (['-w', str(w)] if w else []) + (['-h', str(h)] if h else [])
        out = subprocess.run(args, input=svg_bytes, capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(out)).convert('RGBA')


def load_mask(src, size=None):
    """Alpha mask (L) of a drawing: SVG/PNG alpha, or dark-on-light luminance."""
    p = Path(src)
    if p.suffix.lower() == '.svg':
        im = svg_to_png(p.read_bytes(), w=size)
    else:
        im = Image.open(p).convert('RGBA')
        if size and im.width != size:
            im = im.resize((size, round(im.height * size / im.width)), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    alpha = a[..., 3] / 255
    lum = a[..., :3].mean(-1) / 255
    if alpha.min() > 0.99:  # opaque image: dark strokes on light paper
        m = 1 - lum
    else:  # black = solid, white details inside = cut out
        m = alpha * (1 - lum)
    return Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), 'L')


def leaf(w, h, hi, lo, seed=5, cell=None):
    """Gold-leaf style metal: square leaves of slightly different tone, wrinkles and a sheen."""
    rng = np.random.default_rng(seed)
    cell = cell or max(10, max(w, h) // 80)
    gw, gh = w // cell + 2, h // cell + 2
    tones = rng.uniform(0.35, 0.9, (gh, gw)).astype(np.float32)
    t = np.asarray(Image.fromarray((tones * 255).astype(np.uint8)).resize((gw * cell, gh * cell), Image.NEAREST), np.float32)[:h, :w] / 255
    ox, oy = rng.integers(0, cell, 2)
    t = np.roll(np.roll(t, ox, 1), oy, 0)
    wr = fractal(w, h, rng, octaves=4, base=max(w, h) // 60)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sheen = 0.85 + 0.3 * np.exp(-((xx - w * 0.35) ** 2 + (yy - h * 0.3) ** 2) / (2 * (0.45 * max(w, h)) ** 2))
    hi, lo = np.array(hi, np.float32), np.array(lo, np.float32)
    img = lo + (hi - lo) * t[..., None]
    img *= (0.85 + 0.25 * wr)[..., None] * sheen[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def foil(src, finish='gold', size=None, color=None, seed=5):
    """Return RGBA: the drawing's shape filled with a finish."""
    m = load_mask(src, size)
    w, h = m.size
    ma = np.asarray(m, np.float32) / 255
    if finish in FINISHES or finish == 'metal':
        if finish == 'metal':
            c = np.array(hexrgb(color or '#B0B4BA'), np.float32)
            hi, lo = tuple(np.clip(c * 1.25 + 30, 0, 255)), tuple(c * 0.5)
        else:
            hi, lo = FINISHES[finish]
        rgb = leaf(w, h, hi, lo, seed)
        a = ma
    elif finish == 'ink':
        c = np.array(hexrgb(color or '#1B1815'), np.float32)
        rng = np.random.default_rng(seed)
        tex = 1 + 0.06 * (fractal(w, h, rng, 4, max(w, h) // 120) - 0.5)
        rgb = np.clip(c * tex[..., None], 0, 255).astype(np.uint8)
        a = ma
    elif finish == 'chalk':
        rng = np.random.default_rng(seed)
        c = np.array(hexrgb(color or '#F4F1EA'), np.float32)
        rgb = np.zeros((h, w, 3), np.uint8) + c.astype(np.uint8)
        rough = rng.random((h, w)).astype(np.float32)
        a = ma * np.clip(0.55 + 0.6 * rough, 0, 1)
    elif finish == 'neon':
        c = np.array(hexrgb(color or '#6EE7F9'), np.float32)
        glow = np.asarray(m.filter(ImageFilter.GaussianBlur(max(4, w // 90))), np.float32) / 255
        core = ma
        a = np.clip(core + glow * 0.85, 0, 1)
        white = np.array([255, 255, 255], np.float32)
        rgb = np.clip(c + (white - c) * (core * 0.75)[..., None], 0, 255).astype(np.uint8)
    else:
        raise SystemExit(f'unknown finish {finish!r}')
    out = np.dstack([rgb, (np.clip(a, 0, 1) * 255).astype(np.uint8)])
    return Image.fromarray(out, 'RGBA')


def svg_layers(svg_path):
    """Yield (id, svg_bytes) with only that top-level <g id> visible, on the full canvas."""
    from lxml import etree
    tree = etree.parse(str(svg_path))
    root = tree.getroot()
    groups = [g for g in root if isinstance(g.tag, str) and g.tag.endswith('}g') and g.get('id')]
    if not groups:
        raise SystemExit(f'{svg_path}: no top-level <g id="..."> groups to split')
    for g in groups:
        r2 = etree.fromstring(etree.tostring(root))
        for other in [x for x in r2 if isinstance(x.tag, str) and x.tag.endswith('}g') and x.get('id') and x.get('id') != g.get('id')]:
            r2.remove(other)
        yield g.get('id'), etree.tostring(r2)


def layers(svg_path, out_dir, finish=None, size=None, color=None, seed=5):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for i, (gid, data) in enumerate(svg_layers(svg_path)):
        tmp = out_dir / f'.{gid}.svg'
        tmp.write_bytes(data)
        if finish:
            im = foil(tmp, finish, size=size, color=color, seed=seed + i)
        else:
            im = svg_to_png(data, w=size)
        tmp.unlink()
        dest = out_dir / f'{gid}.png'
        im.save(dest)
        made.append({'id': gid, 'file': dest.name, 'size': im.size})
    (out_dir / 'layers.json').write_text(json.dumps(made, indent=1), encoding='utf-8')
    return made


# ---------------------------------------------------------------- photos

def crop_aspect(im, aspect, focus=(0.5, 0.5)):
    if not aspect:
        return im
    a, b = (float(v) for v in aspect.split(':'))
    want = a / b
    w, h = im.size
    if w / h > want:
        nw = int(h * want)
        x0 = int((w - nw) * focus[0])
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / want)
    y0 = int((h - nh) * focus[1])
    return im.crop((0, y0, w, y0 + nh))


def treat_photo(src, mode='duotone', colors=None, aspect=None, focus=(0.5, 0.5), vignette_amt=0.0, grain=0.0,
                min_size=None, seed=1):
    im = Image.open(src).convert('RGB')
    im = crop_aspect(im, aspect, focus)
    if min_size and max(im.size) < min_size:
        k = min_size / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 50, 2))
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600), Image.LANCZOS)
    gray = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    if mode == 'duotone':
        c1, c2 = (colors or ['#140B08', '#E2BE7C'])[:2]
        out = ImageOps.colorize(gray, hexrgb(c1), hexrgb(c2))
    elif mode == 'mono':
        out = gray.convert('RGB')
    elif mode == 'sepia':
        out = ImageOps.colorize(gray, (24, 14, 8), (236, 214, 170))
    elif mode == 'grade':
        tint = np.array(hexrgb((colors or ['#D9B26A'])[0]), np.float32) / 255
        a = np.asarray(im, np.float32)
        a = a * (0.65 + 0.35 * tint)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    elif mode == 'color':
        out = im
    else:
        raise SystemExit(f'unknown photo mode {mode!r}')
    a = np.asarray(out, np.float32)
    if vignette_amt:
        a *= vignette(out.width, out.height, vignette_amt)[..., None]
    if grain:
        a += np.random.default_rng(seed).normal(0, 255 * grain, (out.height, out.width, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), im


# ---------------------------------------------------------------- glow + pattern

def glow(color, size=1600, softness=0.35):
    c = hexrgb(color)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2) / (size / 2)
    a = np.exp(-(d / max(0.05, softness)) ** 2) * np.clip(1 - d, 0, 1)
    rgba = np.zeros((size, size, 4), np.uint8)
    rgba[..., :3] = c
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def pattern(kind, w, h, color='#D9B26A', finish=None, unit=None, seed=3):
    from PIL import ImageDraw
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    u = unit or max(8, h // 14)
    if kind == 'woven':
        for y in range(0, h, u):
            off = u if (y // u) % 2 else 0
            for x in range(-2 * u, w + 2 * u, 2 * u):
                d.rounded_rectangle([x + off, y + 2, x + off + int(1.6 * u), y + u - 2], radius=2, fill=255)
    elif kind == 'dots':
        for y in range(u // 2, h, u):
            for x in range(u // 2 + (u // 2 if (y // u) % 2 else 0), w, u):
                r = u * 0.18
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    elif kind == 'stripes':
        for x in range(-h, w + h, u):
            d.polygon([(x, h), (x + u // 2, h), (x + u // 2 + h, 0), (x + h, 0)], fill=255)
    elif kind == 'hatch':
        for x in range(-h, w + h, u // 2):
            d.line([(x, h), (x + h, 0)], fill=255, width=max(1, u // 10))
    elif kind == 'chevron':
        for y in range(0, h + u, u):
            pts = []
            for x in range(0, w + u, u):
                pts.append((x, y + (u // 2 if (x // u) % 2 else 0)))
            d.line(pts, fill=255, width=max(2, u // 6))
    elif kind == 'grid':
        for x in range(0, w, u):
            d.line([(x, 0), (x, h)], fill=255, width=1)
        for y in range(0, h, u):
            d.line([(0, y), (w, y)], fill=255, width=1)
    else:
        raise SystemExit(f'unknown pattern {kind!r}')
    if finish in FINISHES:
        rgb = leaf(w, h, *FINISHES[finish], seed=seed)
    else:
        rgb = np.zeros((h, w, 3), np.uint8) + np.array(hexrgb(color), np.uint8)
    return Image.fromarray(np.dstack([rgb, np.asarray(m)]), 'RGBA')


# ---------------------------------------------------------------- CLI

def parse_size(s, default):
    if not s:
        return default
    if 'x' in s:
        a, b = s.lower().split('x')
        return int(a), int(b)
    return int(s), int(s)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    g = sub.add_parser('ground', help='a material ground (2400x1350 by default)')
    g.add_argument('--kind', default='lacquer')
    g.add_argument('--base', default='#140B08')
    g.add_argument('--tone')
    g.add_argument('--grain', type=float, default=0.04)
    g.add_argument('--vignette', type=float, default=0.4)
    g.add_argument('--crackle', type=float, default=0.0)
    g.add_argument('--dots', type=float, default=0.0)
    g.add_argument('--grid', type=float, default=0.0, help='grid step in inches (clean)')
    g.add_argument('--seed', type=int, default=1)
    g.add_argument('--size', help='WxH in px (default 2400x1350)')
    g.add_argument('--style', help='take the recipe from a style pack')
    g.add_argument('--name', default='main', help='ground name in the style pack (main, alt)')
    g.add_argument('--out', required=True)

    f = sub.add_parser('foil', help='fill a drawing with a finish')
    f.add_argument('src')
    f.add_argument('--finish', default='gold')
    f.add_argument('--color')
    f.add_argument('--size', type=int, help='output width in px')
    f.add_argument('--seed', type=int, default=5)
    f.add_argument('--out', required=True)

    la = sub.add_parser('layers', help='one PNG per top-level <g id> of an SVG')
    la.add_argument('svg')
    la.add_argument('--out-dir', required=True)
    la.add_argument('--finish')
    la.add_argument('--color')
    la.add_argument('--size', type=int)

    p = sub.add_parser('photo', help='grade a photo into the palette')
    p.add_argument('src')
    p.add_argument('--out', required=True)
    p.add_argument('--mode', default='duotone')
    p.add_argument('--colors', help='"#dark,#light" for duotone, "#tint" for grade')
    p.add_argument('--aspect', help='e.g. 16:9, 1:1, 4:5')
    p.add_argument('--focus', default='0.5,0.5')
    p.add_argument('--vignette', type=float, default=0.0)
    p.add_argument('--grain', type=float, default=0.0)
    p.add_argument('--min-size', type=int)
    p.add_argument('--pair', action='store_true', help='also write NAME_mono and NAME_color with the same crop (colour bloom)')

    gl = sub.add_parser('glow', help='a soft radial light (RGBA PNG)')
    gl.add_argument('--color', required=True)
    gl.add_argument('--size', type=int, default=1600)
    gl.add_argument('--softness', type=float, default=0.35)
    gl.add_argument('--out', required=True)

    pa = sub.add_parser('pattern', help='a band or tile (RGBA PNG)')
    pa.add_argument('--kind', default='woven')
    pa.add_argument('--color', default='#D9B26A')
    pa.add_argument('--finish')
    pa.add_argument('--size', default='2400x300')
    pa.add_argument('--unit', type=int)
    pa.add_argument('--out', required=True)

    a = ap.parse_args(argv)
    if a.cmd == 'ground':
        size = parse_size(a.size, (2400, 1350))
        im = style_ground(a.style, a.name, size) if a.style else ground(
            a.kind, a.base, a.tone, size, a.grain, a.vignette, a.seed, a.crackle, dots=a.dots, grid=a.grid)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        im.save(a.out, quality=92)
    elif a.cmd == 'foil':
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        foil(a.src, a.finish, a.size, a.color, a.seed).save(a.out)
    elif a.cmd == 'layers':
        for row in layers(a.svg, a.out_dir, a.finish, a.size, a.color):
            print(row['id'], '->', row['file'], row['size'])
    elif a.cmd == 'photo':
        cols = a.colors.split(',') if a.colors else None
        fx, fy = (float(v) for v in a.focus.split(','))
        out, cropped = treat_photo(a.src, a.mode, cols, a.aspect, (fx, fy), a.vignette, a.grain, a.min_size)
        dest = Path(a.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, quality=90)
        if a.pair:
            mono, _ = treat_photo(a.src, 'duotone' if cols else 'mono', cols, a.aspect, (fx, fy), a.vignette, a.grain, a.min_size)
            mono.save(dest.with_name(dest.stem + '_mono' + dest.suffix), quality=90)
            cropped.save(dest.with_name(dest.stem + '_color' + dest.suffix), quality=90)
    elif a.cmd == 'glow':
        glow(a.color, a.size, a.softness).save(a.out)
    elif a.cmd == 'pattern':
        w, h = parse_size(a.size, (2400, 300))
        pattern(a.kind, w, h, a.color, a.finish, a.unit).save(a.out)
    print('ok', getattr(a, 'out', None) or getattr(a, 'out_dir', ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
