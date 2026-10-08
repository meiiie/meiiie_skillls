"""Tile images into labelled contact sheets (slide renders, asset candidates, video frames).

Usage:
  python contact_sheet.py INPUT [INPUT ...] --out contact.jpg [--cols 4] [--width 480]
         [--per-sheet 0] [--label name|index|none] [--captions captions.tsv]

INPUT is image files and/or folders (jpg/jpeg/png/webp, sorted naturally).
--per-sheet N splits into contact-1.jpg, contact-2.jpg ... (0 = one sheet).
--captions is a TSV of "filename<TAB>caption" (e.g. licence + author) printed under each tile.
Always LOOK at the sheet afterwards: the sheet exists so a human-like eye checks every image.
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EXT = {'.jpg', '.jpeg', '.png', '.webp'}


def natural(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', p.name)]


def collect(inputs):
    files = []
    for i in inputs:
        p = Path(i)
        if p.is_dir():
            files += sorted((q for q in p.iterdir() if q.suffix.lower() in EXT and not q.name.startswith('contact')), key=natural)
        elif p.suffix.lower() in EXT:
            files.append(p)
    return files


def font(size):
    for name in ('DejaVuSans.ttf', 'Arial.ttf', 'LiberationSans-Regular.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(files, out, cols, width, label, captions):
    thumbs = []
    for i, f in enumerate(files, 1):
        try:
            im = Image.open(f).convert('RGB')
        except Exception as e:  # unreadable candidate: show it as a grey tile
            im = Image.new('RGB', (16, 9), (90, 90, 90))
            print('unreadable', f, e)
        im.thumbnail((width, width * 3 // 4 if im.width >= im.height else width))
        thumbs.append((i, f, im))
    th = max(t[2].height for t in thumbs)
    cap_h = 0 if label == 'none' else 34 if captions else 20
    rows = (len(thumbs) + cols - 1) // cols
    W, H = cols * (width + 8) + 8, rows * (th + cap_h + 8) + 8
    canvas = Image.new('RGB', (W, H), (24, 24, 26))
    d = ImageDraw.Draw(canvas)
    fnt, small = font(13), font(11)
    for k, (i, f, im) in enumerate(thumbs):
        x = 8 + (k % cols) * (width + 8)
        y = 8 + (k // cols) * (th + cap_h + 8)
        canvas.paste(im, (x + (width - im.width) // 2, y))
        if label != 'none':
            text = str(i) if label == 'index' else f'{i} · {f.name}'
            d.text((x, y + th + 3), text[:60], fill=(235, 235, 235), font=fnt)
            if captions and f.name in captions:
                d.text((x, y + th + 19), captions[f.name][:70], fill=(170, 170, 170), font=small)
    canvas.save(out, quality=88)
    print('wrote', out, f'({len(thumbs)} images)')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Labelled contact sheets.')
    ap.add_argument('inputs', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--width', type=int, default=480)
    ap.add_argument('--per-sheet', type=int, default=0)
    ap.add_argument('--label', choices=('name', 'index', 'none'), default='name')
    ap.add_argument('--captions')
    a = ap.parse_args(argv)
    files = collect(a.inputs)
    if not files:
        raise SystemExit('no images found in ' + ' '.join(a.inputs))
    caps = {}
    if a.captions:
        for line in Path(a.captions).read_text(encoding='utf-8').splitlines():
            if '\t' in line:
                k, v = line.split('\t', 1)
                caps[k] = v
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.per_sheet and len(files) > a.per_sheet:
        for n in range(0, len(files), a.per_sheet):
            sheet(files[n:n + a.per_sheet], out.with_name(f'{out.stem}-{n // a.per_sheet + 1}{out.suffix}'), a.cols, a.width, a.label, caps)
    else:
        sheet(files, out, a.cols, a.width, a.label, caps)


if __name__ == '__main__':
    main()
