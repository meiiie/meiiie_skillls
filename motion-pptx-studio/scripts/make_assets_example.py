"""Example motif generator: gold-leaf textures, layered object parts, medallions and woven bands.

The drawings are an original sample (a long-necked lute split into head, neck and
body, a tally, a ring medallion, a basin, a clapper, a drum and a mat band).
Replace the geometry for another subject. Optional photos are written as gold
duotones next to a colour copy. Nothing is read from a fixed machine path.

Usage:
  python make_assets_example.py [--out assets_example]
      [--photo PATH|NAME[|SIZE[|x0,y0,x1,y1]]]

SIZE upscales when the long edge is smaller than SIZE. The box is four fractions
of the source width and height, left, top, right, bottom.
"""
import argparse
import io
import math
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter


def goldleaf(w, h, cell=44, seed=5):
    r = np.random.default_rng(seed)
    img = np.zeros((h, w, 3))
    hi = np.array([248, 218, 146])
    lo = np.array([150, 104, 40])
    wr = gaussian_filter(r.random((h, w)), [1.0, 4])
    wr = (wr - wr.min()) / np.ptp(wr)
    for y0 in range(-cell, h, cell):
        for x0 in range(-cell, w, cell):
            ox, oy = r.integers(-4, 4, 2)
            t = r.uniform(0.35, 0.85)
            ys = slice(max(0, y0 + oy), min(h, y0 + oy + cell + 3))
            xs = slice(max(0, x0 + ox), min(w, x0 + ox + cell + 3))
            img[ys, xs] = lo + (hi - lo) * t
    yy, xx = np.mgrid[0:h, 0:w]
    sheen = 0.85 + 0.3 * np.exp(-((xx - w * 0.35) ** 2 + (yy - h * 0.3) ** 2) / (2 * (0.45 * max(w, h)) ** 2))
    return np.clip(img * (0.85 + 0.25 * wr[..., None]) * sheen[..., None], 0, 255).astype('uint8')


def render(svg, w, h, fn, out):
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert('RGBA')
    a = np.array(im).astype(float)
    lum = a[..., :3].mean(-1) / 255
    m = (a[..., 3] * (1 - lum)).clip(0, 255).astype('uint8')
    t = Image.fromarray(goldleaf(w, h, cell=max(14, max(w, h) // 80), seed=len(fn))).convert('RGBA')
    t.putalpha(Image.fromarray(m))
    t.save(Path(out) / (fn + '.png'))
    return fn


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def tally(x, y, w, h, ang=0, cx=0, cy=0):
    return (
        f'<g transform="rotate({ang} {cx} {cy})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w * 0.35}" fill="#000"/>'
        f'<circle cx="{x + w / 2}" cy="{y + w * 0.7}" r="{w * 0.18}" fill="#fff"/>'
        f'<line x1="{x + w / 2}" y1="{y + h * 0.3}" x2="{x + w / 2}" y2="{y + h * 0.8}" stroke="#fff" stroke-width="{w * 0.08}"/></g>'
    )


def generate_vectors(out):
    # Layered lute on one shared canvas so each part can morph on its own.
    head = (
        '<g fill="#000"><rect x="258" y="40" width="84" height="230" rx="10"/><rect x="250" y="262" width="100" height="22"/>'
        '<rect x="140" y="105" width="120" height="22" rx="8"/><circle cx="135" cy="116" r="22"/>'
        '<rect x="140" y="195" width="120" height="22" rx="8"/><circle cx="135" cy="206" r="22"/>'
        '<rect x="340" y="150" width="120" height="22" rx="8"/><circle cx="465" cy="161" r="22"/></g>'
        '<g fill="none" stroke="#fff" stroke-width="5"><rect x="272" y="60" width="56" height="190" rx="6"/></g>'
    )
    neck = '<g fill="#000"><rect x="272" y="284" width="56" height="1426"/>' + ''.join(
        f'<rect x="250" y="{1010 + i * 66}" width="100" height="24" rx="4"/>' for i in range(10)
    ) + '</g>'
    body = (
        '<g fill="#000"><path d="M110,1705 L490,1705 L415,2330 L185,2330 Z"/></g>'
        '<g fill="none" stroke="#fff" stroke-width="7"><path d="M150,1745 L450,1745 L385,2290 L215,2290 Z"/></g>'
        '<g fill="#fff"><rect x="255" y="2050" width="90" height="22"/><rect x="270" y="2235" width="60" height="26"/></g>'
    )
    for name, part in (('dd_head', head), ('dd_neck', neck), ('dd_body', body)):
        render(svg(600, 2400, part), 600, 2400, name, out)
    strings = ''.join(f'<line x1="{x}" y1="284" x2="{x}" y2="2240" stroke="#000" stroke-width="5"/>' for x in (285, 300, 315))
    render(svg(600, 2400, head + neck + body + strings), 600, 2400, 'dd_full', out)
    render(svg(300, 1200, tally(60, 20, 180, 1160)), 300, 1200, 'the_tru', out)
    # Medallion: tally ring, weave ring, core.
    c = 1000
    render(svg(2000, 2000, ''.join(tally(c - 24, 70, 48, 250, k * 360 / 44, c, c) for k in range(44))), 2000, 2000, 'med_tally', out)
    weave = []
    for yy in range(380, 1620, 28):
        for xx in range(380, 1620, 56):
            off = 28 if (yy // 28) % 2 else 0
            weave.append(f'<rect x="{xx + off}" y="{yy}" width="44" height="18" rx="3"/>')
    render(svg(
        2000, 2000,
        '<defs><clipPath id="r"><path fill-rule="evenodd" d="M1000,330 a670,670 0 1,0 0.1,0 Z M1000,470 a530,530 0 1,0 0.1,0 Z"/></clipPath></defs>'
        f'<g clip-path="url(#r)" fill="#000">{"".join(weave)}</g><g fill="none" stroke="#000" stroke-width="10"><circle cx="1000" cy="1000" r="680"/><circle cx="1000" cy="1000" r="520"/></g>',
    ), 2000, 2000, 'med_weave', out)
    render(svg(
        2000, 2000,
        '<g fill="none" stroke="#000"><circle cx="1000" cy="1000" r="430" stroke-width="16"/><circle cx="1000" cy="1000" r="395" stroke-width="5"/></g>'
        '<g stroke="#000" stroke-width="9">' + ''.join(f'<line x1="{x}" y1="700" x2="{x}" y2="1300"/>' for x in (960, 1000, 1040)) + '</g><circle cx="1000" cy="660" r="22" fill="#000"/>',
    ), 2000, 2000, 'med_core', out)
    render(svg(
        1400, 600,
        '<g fill="#000"><path d="M80,150 C120,520 1280,520 1320,150 Z"/></g><ellipse cx="700" cy="150" rx="660" ry="90" fill="#000"/>'
        '<ellipse cx="700" cy="150" rx="600" ry="62" fill="#fff"/><path d="M180,280 C320,420 1080,420 1220,280" fill="none" stroke="#fff" stroke-width="10"/>'
        + ''.join(tally(500 + i * 90, -300 + i * 10, 40, 330, -25 + i * 14, 700, 150) for i in range(5)),
    ), 1400, 600, 'basin', out)
    render(svg(
        1600, 900,
        '<g fill="#000"><path d="M120,640 C500,600 1100,600 1480,640 L1470,740 C1100,700 500,700 130,740 Z"/></g>'
        '<g fill="none" stroke="#fff" stroke-width="6"><path d="M180,690 C520,655 1080,655 1420,690"/></g>'
        '<g stroke="#000" stroke-linecap="round"><line x1="430" y1="80" x2="640" y2="610" stroke-width="30"/>'
        '<line x1="1150" y1="80" x2="980" y2="440" stroke-width="30"/><line x1="985" y1="430" x2="895" y2="610" stroke-width="16"/><line x1="1000" y1="440" x2="945" y2="615" stroke-width="16"/></g>',
    ), 1600, 900, 'phach', out)
    render(svg(
        1200, 1000,
        '<g fill="#000"><path d="M300,380 C260,520 260,700 300,840 C420,900 780,900 900,840 C940,700 940,520 900,380 Z"/><ellipse cx="600" cy="380" rx="300" ry="85"/></g>'
        '<ellipse cx="600" cy="380" rx="265" ry="64" fill="#fff"/><ellipse cx="600" cy="380" rx="235" ry="48" fill="#000"/>'
        '<g fill="#fff">' + ''.join(f'<circle cx="{600 + 285 * math.cos(a)}" cy="{380 + 75 * math.sin(a) + (0)}" r="9"/>' for a in [k * math.pi / 9 for k in range(10)]) + '</g>'
        '<path d="M290,800 C420,860 780,860 910,800" fill="none" stroke="#fff" stroke-width="8"/>'
        '<line x1="250" y1="120" x2="980" y2="300" stroke="#000" stroke-width="22" stroke-linecap="round"/>',
    ), 1200, 1000, 'trong_chau', out)
    band = ''.join(
        f'<rect x="{x + (22 if (y // 22) % 2 else 0)}" y="{y}" width="36" height="14" rx="2"/>'
        for y in range(0, 300, 22) for x in range(-44, 2444, 44)
    )
    render(svg(2400, 300, f'<g fill="#000">{band}</g>'), 2400, 300, 'mat_band', out)


def duo(src, fn, out, box=None, size=None):
    im = Image.open(src).convert('RGB')
    if box:
        width, height = im.size
        im = im.crop((int(box[0] * width), int(box[1] * height), int(box[2] * width), int(box[3] * height)))
    if size and max(im.size) < size:
        im = im.resize((int(im.width * size / max(im.size)), int(im.height * size / max(im.size))), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 50, 2))
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600), Image.LANCZOS)
    gray = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    ImageOps.colorize(gray, (14, 8, 6), (226, 190, 124)).save(Path(out) / f'duo_{fn}.jpg', quality=90)
    im.save(Path(out) / f'col_{fn}.jpg', quality=90)


def parse_photo(spec):
    bits = spec.split('|')
    if not 2 <= len(bits) <= 4 or not bits[0] or not bits[1]:
        raise ValueError('photo must be PATH|NAME[|SIZE[|x0,y0,x1,y1]]')
    size = int(bits[2]) if len(bits) >= 3 and bits[2] else None
    box = None
    if len(bits) == 4 and bits[3]:
        box = tuple(float(v) for v in bits[3].split(','))
        if len(box) != 4:
            raise ValueError('photo box needs four comma-separated fractions')
    return bits[0], bits[1], box, size


def main(argv=None):
    parser = argparse.ArgumentParser(description='Generate example gold-leaf motifs and optional duotone photos.')
    parser.add_argument('--out', default='assets_example', help='directory for PNG motifs and optional photo layers')
    parser.add_argument('--photo', action='append', default=[], metavar='PATH|NAME[|SIZE[|BOX]]', help='source photo to write as duo_NAME.jpg and col_NAME.jpg')
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        photos = [parse_photo(spec) for spec in args.photo]
    except ValueError as error:
        raise SystemExit(str(error))
    generate_vectors(out)
    for path, name, box, size in photos:
        duo(path, name, out, box=box, size=size)
    print('ok')


if __name__ == '__main__':
    main()
