"""Anti-template phase (v5.3): sketch THREE different art directions as thumbnails before the storyboard.

  python3 directions.py WORK [--spec WORK/design/directions.json] [--out WORK/design/directions.jpg]

design/directions.json:
  {"directions": [
     {"id": "A", "name": "Xưởng trắng", "composition": "swiss-grid",
      "palette": ["#FFFFFF", "#1464F4", "#0B1B33"],      ground, accent, ink (more allowed)
      "fonts": ["fonts/Display.ttf", "fonts/Body.ttf"],  display, body (paths under WORK)
      "image": "assets/gen/tex-alu.jpg",                 optional plate/hero image
      "title": "...", "kicker": "...", "number": "300k",
      "ground": "...", "type": "...", "motion": "...", "signature": "..."},  words for directions.md
     ... 3 entries ...],
   "chosen": "A", "why": "...", "chapters": "S1-S2 B, S3-S7 A"}

composition: FREE TEXT (v5.5): describe the layout you invent ("tall drawn object left, words right"). The
thumbnail is sketched from "sketch" (swiss-grid | hero-object | full-bleed | kinetic-number | editorial | split)
or, when absent, from keywords in the composition. "family" names the routed family a direction starts from.
Writes design/directions.jpg (3 thumbnails side by side, palette swatches and type under each) and, when
design/directions.md is still the template, fills it from the spec. Then LOOK: if two thumbnails could be
the same deck in another colour, they are not different directions; change one.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 960, 540


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def font(path, size, work):
    for p in ([work / path] if path else []) + [Path(path)] if path else []:
        try:
            return ImageFont.truetype(str(p), size)
        except OSError:
            continue
    for name in ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def cover(img, w, h):
    return ImageOps.fit(img.convert('RGB'), (w, h), Image.LANCZOS)


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    return lines + ([cur] if cur else [])


SKETCHES = ('full-bleed', 'kinetic-number', 'editorial', 'hero-object', 'split', 'swiss-grid')
SKETCH_WORDS = (('full-bleed', r'bleed|plate|full.?frame|photo fills'), ('kinetic-number', r'number|numeral|figure|stat'),
                ('hero-object', r'object|diagram|construct|drawn|isometric|cut.?out'), ('split', r'split|column|half|right|left'),
                ('swiss-grid', r'grid|swiss|modular'), ('editorial', r'.'))


def sketch_of(dr):
    s = dr.get('sketch') or dr.get('composition', '')
    if s in SKETCHES:
        return s
    for k, pat in SKETCH_WORDS:
        if re.search(pat, str(s), re.I):
            return k
    return 'editorial'


def thumb(dr, work):
    pal = [rgb(h) for h in dr.get('palette', ['#FFFFFF', '#1464F4', '#111111'])]
    ground, accent = pal[0], pal[1] if len(pal) > 1 else (20, 100, 244)
    ink = pal[2] if len(pal) > 2 else ((17, 17, 17) if lum(ground) > 128 else (240, 240, 240))
    fonts = dr.get('fonts', [None, None]) + [None, None]
    fd, fb = (lambda s: font(fonts[0], s, work)), (lambda s: font(fonts[1] or fonts[0], s, work))
    img = Image.new('RGB', (W, H), ground)
    pic = None
    if dr.get('image') and (work / dr['image']).is_file():
        pic = Image.open(work / dr['image'])
        pic = ImageOps.exif_transpose(pic)
    d = ImageDraw.Draw(img)
    comp = sketch_of(dr)
    title, kicker, number = dr.get('title', dr.get('name', '')), dr.get('kicker', ''), dr.get('number', '')
    if comp == 'full-bleed':
        if pic:
            img.paste(cover(pic, W, H))
        shade = Image.new('L', (W, H))
        sd = ImageDraw.Draw(shade)
        for y in range(H):
            sd.line([(0, y), (W, y)], fill=int(220 * max(0, (y - H * 0.35) / (H * 0.65))))
        img = Image.composite(Image.new('RGB', (W, H), ground), img, shade)
        d = ImageDraw.Draw(img)
        d.text((56, H - 200), kicker.upper(), font=fb(20), fill=accent)
        for i, l in enumerate(wrap(d, title, fd(54), W - 120)[:2]):
            d.text((56, H - 168 + i * 62), l, font=fd(54), fill=ink)
    elif comp == 'kinetic-number':
        if pic:
            img.paste(Image.blend(Image.new('RGB', (W, H), ground), cover(pic, W, H), 0.35))
            d = ImageDraw.Draw(img)
        f = fd(230)
        d.text((48, 40), number or '01', font=f, fill=accent)
        d.text((56, H - 120), kicker.upper(), font=fb(20), fill=ink)
        for i, l in enumerate(wrap(d, title, fd(34), W - 120)[:2]):
            d.text((56, H - 88 + i * 40), l, font=fd(34), fill=ink)
    elif comp == 'editorial':
        d.rectangle([0, 0, W, H], fill=ground)
        for i, l in enumerate(wrap(d, title, fd(50), 520)[:3]):
            d.text((60, 70 + i * 58), l, font=fd(50), fill=ink)
        d.line([(60, 260), (420, 256)], fill=accent, width=5)
        for c in range(2):
            for r_ in range(9):
                x0 = 60 + c * 260
                d.rectangle([x0, 300 + r_ * 22, x0 + 220 - (r_ * 37 % 60), 308 + r_ * 22], fill=tuple(int(v * .55 + g * .45) for v, g in zip(ink, ground)))
        if pic:
            p = cover(pic, 300, 400)
            img.paste(p, (W - 360, 70))
            d.rectangle([W - 362, 68, W - 58, 472], outline=ink, width=2)
    elif comp == 'hero-object':
        if pic:
            p = pic.convert('RGB')
            p.thumbnail((640, 400))
            img.paste(p, ((W - p.width) // 2, 70))
        d.text((56, 30), kicker.upper(), font=fb(18), fill=accent)
        d.text((56, H - 80), title, font=fd(34), fill=ink)
    elif comp == 'split':
        if pic:
            img.paste(cover(pic, W // 2, H), (W // 2, 0))
        for i, l in enumerate(wrap(d, title, fd(44), W // 2 - 110)[:3]):
            d.text((56, 160 + i * 52), l, font=fd(44), fill=ink)
        d.text((56, 120), kicker.upper(), font=fb(18), fill=accent)
    else:  # swiss-grid
        grid = tuple(int(v * .9 + a * .1) for v, a in zip(ground, accent))
        for c in range(13):
            x = 48 + c * (W - 96) / 12
            d.line([(x, 0), (x, H)], fill=grid, width=1)
        for r_ in range(0, H, 36):
            d.line([(0, r_), (W, r_)], fill=grid, width=1)
        d.rectangle([48, 48, 48 + 10, 160], fill=accent)
        d.text((76, 44), kicker.upper(), font=fb(18), fill=accent)
        for i, l in enumerate(wrap(d, title, fd(46), 480)[:3]):
            d.text((76, 76 + i * 54), l, font=fd(46), fill=ink)
        if number:
            d.text((76, H - 170), number, font=fd(110), fill=accent)
        if pic:
            p = pic.convert('RGB')
            p.thumbnail((440, 300))
            img.paste(p, (W - p.width - 48, H - p.height - 48))
    return img


def sheet(spec, work, out):
    drs = spec['directions']
    tiles = []
    for dr in drs:
        t = thumb(dr, work)
        cap = Image.new('RGB', (W, 120), (250, 250, 248))
        d = ImageDraw.Draw(cap)
        chosen = str(spec.get('chosen', '')).strip().upper().startswith(str(dr.get('id', '')).upper())
        d.text((16, 10), f'{dr.get("id", "?")} — {dr.get("name", "")}' + ('   ✓ chosen' if chosen else ''),
               font=font(None, 26, work), fill=(20, 20, 20))
        for i, h in enumerate(dr.get('palette', [])[:6]):
            d.rectangle([16 + i * 46, 52, 56 + i * 46, 92], fill=rgb(h), outline=(160, 160, 160))
        d.text((310, 50), f'{dr.get("composition", "")} · ' + ', '.join(Path(f).stem for f in dr.get('fonts', []) if f),
               font=font(None, 18, work), fill=(60, 60, 60))
        tile = Image.new('RGB', (W, H + 120), (255, 255, 255))
        tile.paste(t, (0, 0))
        tile.paste(cap, (0, H))
        if chosen:
            ImageDraw.Draw(tile).rectangle([0, 0, W - 1, H + 119], outline=(20, 100, 244), width=8)
        tiles.append(tile)
    gap = 24
    out_img = Image.new('RGB', (len(tiles) * W + (len(tiles) + 1) * gap, H + 120 + 2 * gap), (228, 228, 224))
    for i, t in enumerate(tiles):
        out_img.paste(t, (gap + i * (W + gap), gap))
    out.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out, quality=88)
    return out


def write_md(spec, md):
    lines = ['# Art directions (v5.3 anti-template phase)', '',
             'Three different directions were sketched as thumbnails (design/directions.jpg) before the storyboard.', '']
    for dr in spec['directions']:
        lines += [f'## Direction {dr.get("id", "?")} — {dr.get("name", "")}',
                  f'- ground: {dr.get("ground", "")}',
                  f'- palette: {" ".join(dr.get("palette", []))}',
                  f'- type: {dr.get("type", ", ".join(Path(f).stem for f in dr.get("fonts", []) if f))}',
                  f'- family: {dr.get("family", "free")}',
                  f'- composition: {dr.get("composition", "")} — {dr.get("composition_note", "")}',
                  f'- motion: {dr.get("motion", "")}',
                  f'- signature visual: {dr.get("signature", "")}', '']
    lines += ['## Decision', f'- chosen: {spec.get("chosen", "TODO")}', f'- why: {spec.get("why", "TODO")}',
              f'- chapters: {spec.get("chapters", "")}', '']
    md.write_text('\n'.join(lines), encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work')
    ap.add_argument('--spec')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    work = Path(a.work).resolve()
    spec_p = Path(a.spec) if a.spec else work / 'design/directions.json'
    spec = json.loads(spec_p.read_text(encoding='utf-8'))
    if len(spec.get('directions', [])) != 3:
        sys.exit('directions.json needs exactly 3 directions')
    comps = [sketch_of(d) for d in spec['directions']]
    if len(set(comps)) < 3:
        print(f'WARN two directions share a composition {comps}: are they really different?')
    out = Path(a.out) if a.out else work / 'design/directions.jpg'
    sheet(spec, work, out)
    md = work / 'design/directions.md'
    if not md.is_file() or 'TODO' in md.read_text(encoding='utf-8'):
        write_md(spec, md)
        print('wrote', md)
    print('wrote', out, '— LOOK at it: could two of these be the same deck in another colour?')


if __name__ == '__main__':
    main()
