"""Cut an object out of a plain (museum / studio) background -> transparent PNG cropped to the object.

  python cutout.py IN.jpg OUT.png [--tol 28] [--feather 1.5] [--pad 20] [--rembg]
  --tol      colour distance from the corner background that still counts as background
  --rembg    use the rembg model instead (pip install rembg; for busy backgrounds)
Flood-fills from the four corners, so the object's own light areas (inside) are kept.
LOOK at the result on a dark slide: halos mean --tol is too low, bitten edges mean too high.
The licence of the source still applies (BY-SA stays BY-SA, credit "(edited / đã chỉnh sửa)").
"""
import argparse
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def main(argv=None):
    ap = argparse.ArgumentParser(description='Background knock-out to transparent PNG.')
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tol', type=int, default=28)
    ap.add_argument('--feather', type=float, default=1.5)
    ap.add_argument('--pad', type=int, default=20)
    ap.add_argument('--rembg', action='store_true')
    a = ap.parse_args(argv)
    im = Image.open(a.src).convert('RGB')
    if a.rembg:
        try:
            from rembg import remove
        except ImportError:
            sys.exit('rembg not installed: bash setup.sh --with-rembg')
        out = remove(im)
    else:
        work = im.copy()
        w, h = work.size
        key = (255, 0, 255)
        for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            if work.getpixel(xy) != key:
                ImageDraw.floodfill(work, xy, key, thresh=a.tol)
        diff = ImageChops.difference(work, Image.new('RGB', work.size, key))
        m = diff.convert('L').point(lambda v: 0 if v == 0 else 255)
        if a.feather:
            m = m.filter(ImageFilter.GaussianBlur(a.feather))
        out = im.convert('RGBA')
        out.putalpha(m)
    bbox = out.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
    if not bbox:
        sys.exit('nothing left after knock-out: lower --tol')
    x0, y0, x1, y1 = bbox
    p = a.pad
    out = out.crop((max(0, x0 - p), max(0, y0 - p), min(out.width, x1 + p), min(out.height, y1 + p)))
    out.save(a.dst)
    print(f'wrote {a.dst} {out.width}x{out.height} — LOOK at it on a dark background')


if __name__ == '__main__':
    main()
