"""Cut an object out of a plain (museum / studio / space) background -> transparent PNG cropped to the object.

  python3 cutout.py IN.jpg OUT.png [--tol 28] [--feather 1.5] [--pad 20] [--close 9] [--edge 18] [--rembg]
  --tol      colour distance from the border background that still counts as background
  --close    v5.4: closing radius in px that re-joins parts the background flood bit off (0 = off)
  --edge     v5.4: local-contrast floor; a dark pixel with this much detail around it is object, not
             background (solar panels against black space, a lacquer box on a dark cloth). 0 = off
  --rembg    use the rembg model instead (pip install rembg; for busy backgrounds)
How: the background is what a flood from the whole image border reaches within --tol of the border colour.
Dark parts of the object that touch the border colour are kept when they carry detail (--edge), the mask is
closed (--close) and every hole inside the object is filled, so nothing inside the outline turns transparent.
EXIF rotation is applied first (a phone photo stays upright). LOOK at the result on a light AND a dark slide:
halos mean --tol is too low, bitten edges mean it is too high.
The licence of the source still applies (BY-SA stays BY-SA, credit "(edited / đã chỉnh sửa)").
"""
import argparse
import sys

from PIL import Image, ImageFilter, ImageOps


def open_upright(path):
    im = Image.open(path)
    try:
        im.seek(0)          # MPO / multi-frame: the first frame is the photo
    except EOFError:
        pass
    return ImageOps.exif_transpose(im)


def object_mask(im, tol=28, close=9, edge=18, bridge=0):
    """L-mode mask (255 = object) for an RGB image on a plain background."""
    import numpy as np
    a = np.asarray(im.convert('RGB'), dtype=np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    ref = np.median(border, axis=0)
    colour_bg = np.abs(a - ref).max(axis=2) <= tol                  # background-coloured pixels
    near = colour_bg.copy()
    if edge:
        g = np.asarray(im.convert('L').filter(ImageFilter.FIND_EDGES), dtype=np.int16)
        local = np.asarray(Image.fromarray(g.astype('uint8')).filter(ImageFilter.MaxFilter(5)), dtype=np.int16)
        near &= local < edge                                       # detailed dark parts are object
    try:
        from scipy import ndimage
        lab, _ = ndimage.label(near)
        edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(edge_labels))
        obj = ~bg
        if close:
            st = ndimage.generate_binary_structure(2, 1)
            obj = ndimage.binary_closing(obj, structure=st, iterations=int(close), border_value=0)
        obj = ndimage.binary_fill_holes(obj)
        if bridge:   # v5.4: close a wide dark bay (a black solar panel against black space) that opens to the edge
            k = int(bridge)
            yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
            disk = (xx * xx + yy * yy) <= k * k
            pad = np.pad(obj, k + 1)
            big = ndimage.binary_closing(pad, structure=disk)[k + 1:-k - 1, k + 1:-k - 1]
            obj = ndimage.binary_fill_holes(big) & (obj | colour_bg)
        if edge:   # the detail test also catches a 2 px ring of background next to the outline: peel it off again
            obj = (ndimage.binary_erosion(obj, iterations=2) | (obj & ~colour_bg))
            obj = ndimage.binary_fill_holes(obj)
        return Image.fromarray((obj * 255).astype('uint8'), 'L')
    except ImportError:                                            # PIL-only fallback: flood from the four corners
        from PIL import ImageDraw
        m = Image.fromarray(((~near) * 255).astype('uint8'), 'L').convert('RGB')
        for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            ImageDraw.floodfill(m, xy, (255, 0, 255), thresh=0)
        r, g2, b = m.split()
        obj = Image.eval(g2, lambda v: 255 if v > 0 else 0)
        if close:
            k = 2 * int(close) + 1
            obj = obj.filter(ImageFilter.MaxFilter(min(k, 15))).filter(ImageFilter.MinFilter(min(k, 15)))
        return obj


def defringe(rgba, px=3):
    """Remove the background-coloured ring along the outline: inside a band of `px` pixels the alpha follows
    how far each pixel is from the background colour, and its colour is un-mixed from that background.
    (Anti-aliased edges carry the old background: a black halo on paper, a white one on a dark slide.)"""
    import numpy as np
    try:
        from scipy import ndimage
    except ImportError:
        return rgba
    arr = np.asarray(rgba, dtype=np.float32)
    rgb, al = arr[..., :3], arr[..., 3] / 255
    solid = al > 0.5
    if not solid.any() or solid.all():
        return rgba
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bgc = np.median(border, axis=0)
    dist_in = ndimage.distance_transform_edt(solid)
    band = solid & (dist_in <= px)
    inner = solid & (dist_in > px + 2)
    if not inner.any():
        return rgba
    # alpha = how much of the NEAREST solid object colour a band pixel carries (a projection onto bg -> object):
    # a dark solar panel keeps its dark edge, a white hull loses its black ring
    _, (iy, ix) = ndimage.distance_transform_edt(~inner, return_indices=True)
    obj_c = rgb[iy, ix]
    v = obj_c - bgc
    est = np.clip(((rgb - bgc) * v).sum(axis=2) / np.maximum((v * v).sum(axis=2), 1.0), 0, 1)
    est = np.where((v * v).sum(axis=2) < 100, 1.0, est)   # object colour ~ background colour: keep it as is
    a2 = al.copy()
    a2[band] = np.minimum(al[band], est[band])
    a2[band & (a2 < 0.3)] = 0   # near-background specks: drop, un-mixing them would only blow up noise
    safe = np.maximum(a2, 0.05)[..., None]
    unmixed = np.clip(bgc + (rgb - bgc) / safe, 0, 255)
    rgb2 = np.where(band[..., None], unmixed, rgb)
    out = np.dstack([rgb2, a2 * 255]).astype('uint8')
    return Image.fromarray(out, 'RGBA')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Background knock-out to transparent PNG.')
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tol', type=int, default=28)
    ap.add_argument('--feather', type=float, default=1.5)
    ap.add_argument('--pad', type=int, default=20)
    ap.add_argument('--close', type=int, default=9)
    ap.add_argument('--edge', type=int, default=18)
    ap.add_argument('--rembg', action='store_true')
    ap.add_argument('--bridge', type=int, default=0, help='px: also keep dark bays narrower than 2x this that open to the edge (black panels on black)')
    ap.add_argument('--defringe', type=int, default=6, help='px of outline to un-mix from the background colour (0 = off)')
    a = ap.parse_args(argv)
    im = open_upright(a.src).convert('RGB')
    if a.rembg:
        try:
            from rembg import remove
        except ImportError:
            sys.exit('rembg not installed: bash setup.sh --with-rembg')
        out = remove(im)
    else:
        m = object_mask(im, a.tol, a.close, a.edge, a.bridge)
        if a.feather:
            m = m.filter(ImageFilter.GaussianBlur(a.feather))
        out = im.convert('RGBA')
        out.putalpha(m)
        if a.defringe:
            out = defringe(out, a.defringe)
    bbox = out.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
    if not bbox:
        sys.exit('nothing left after knock-out: lower --tol')
    x0, y0, x1, y1 = bbox
    p = a.pad
    out = out.crop((max(0, x0 - p), max(0, y0 - p), min(out.width, x1 + p), min(out.height, y1 + p)))
    out.save(a.dst)
    kept = out.getchannel('A').point(lambda v: 255 if v > 128 else 0).histogram()[255] / max(1, out.width * out.height)
    print(f'wrote {a.dst} {out.width}x{out.height}, {kept:.0%} of the crop is object — LOOK at it on a light and a dark background')


if __name__ == '__main__':
    main()
