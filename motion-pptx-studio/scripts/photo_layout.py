#!/usr/bin/env python3
"""Photo levers for composition: find the subject and the quiet space, crop with intent, cut out, mask.
Decisions stay yours (principles/photo-arrangement.md); this only measures and cuts.

  python3 photo_layout.py analyze IMG [--grid 4x3] [--json OUT]      subject box, quiet cells, text colour per cell
  python3 photo_layout.py crop IMG --aspect 16:9 --out OUT [--subject-at 0.66,0.5] [--zoom 1.0] [--detail] [--focus X,Y]
        place the subject's centre at a frame point (e.g. right third, leaving the left quiet for type);
        --zoom >1 tightens around the subject; --detail = the tightest crop that is still the subject (2.5x)
  python3 photo_layout.py cutout IMG --out OUT.png [--feather 2]     subject on transparency (rembg if present:
        `pip install "rembg[cpu]"`, first run downloads a ~170 MB model;
        else OpenCV GrabCut seeded by the saliency box: check the edge by eye)
  python3 photo_layout.py mask IMG --shape circle|arch|band|pill|poly:x,y;x,y;... --out OUT.png [--aspect 1:1]
        the photo inside a shape that comes from the subject (a cup rim, a window arch, a field strip)
Python: from photo_layout import analyze, crop
"""
import argparse, json, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def saliency(im):
    """Spectral-residual saliency (Hou & Zhang 2007) on a 128 px grey copy, blurred; 0..1 at image size."""
    g = np.asarray(im.convert('L').resize((128, int(128 * im.height / im.width) or 1)), float)
    F = np.fft.fft2(g); A = np.log(np.abs(F) + 1e-9); P = np.angle(F)
    k = np.ones((3, 3)) / 9; pad = np.pad(A, 1, mode='edge')
    avg = sum(pad[i:i + A.shape[0], j:j + A.shape[1]] * k[i, j] for i in range(3) for j in range(3))
    s = np.abs(np.fft.ifft2(np.exp(A - avg + 1j * P))) ** 2
    s = np.asarray(Image.fromarray((s / s.max() * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(4)), float)
    detail = np.asarray(im.convert('L').resize(s.shape[::-1]).filter(ImageFilter.FIND_EDGES), float)
    m = 0.6 * s / (s.max() + 1e-9) + 0.4 * detail / (detail.max() + 1e-9)
    return np.asarray(Image.fromarray((m * 255).astype('uint8')).resize(im.size, Image.BILINEAR), float) / 255

def subject_box(sal, keep=0.6):
    """Smallest box holding `keep` of the saliency mass (robust to scattered texture)."""
    def span(p):
        c = np.cumsum(p) / p.sum(); lo = np.searchsorted(c, (1 - keep) / 2); hi = np.searchsorted(c, 1 - (1 - keep) / 2)
        return lo / len(p), (hi + 1) / len(p)
    w = sal ** 2
    (x0, x1), (y0, y1) = span(w.sum(0)), span(w.sum(1))
    return [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)]

def analyze(path, grid=(4, 3)):
    im = Image.open(path).convert('RGB'); sal = saliency(im); L = np.asarray(im.convert('L'), float)
    gx, gy = grid; H, W = sal.shape; cells = []
    for j in range(gy):
        for i in range(gx):
            sl = (slice(j * H // gy, (j + 1) * H // gy), slice(i * W // gx, (i + 1) * W // gx))
            busy = float(sal[sl].mean()); lum = float(L[sl].mean())
            cells.append({'cell': [i, j], 'busy': round(busy, 3), 'luma': round(lum),
                          'text': '#FFFFFF-ish (dark area)' if lum < 120 else '#111111-ish (light area)'})
    q = sorted(cells, key=lambda c: c['busy'])
    box = subject_box(sal)
    return {'image': path, 'size': im.size, 'subject_box': box,
            'subject_centre': [round((box[0] + box[2]) / 2, 3), round((box[1] + box[3]) / 2, 3)],
            'quiet_cells': [c['cell'] for c in q[:max(2, len(q) // 3)]], 'cells': cells}

def crop(path, aspect, out=None, subject_at=(0.5, 0.5), zoom=1.0, detail=False, focus=None):
    """focus=(x, y) overrides the measured subject: saliency mistakes busy texture (paving, foliage) for a
    subject, so look at analyze's box first and pass the real subject when it is wrong."""
    im = Image.open(path).convert('RGB'); W, H = im.size; a = analyze(path)
    sx, sy = focus or a['subject_centre']; bx = a['subject_box']
    if focus: bx = [sx - .15, sy - .15, sx + .15, sy + .15]
    ar = aspect[0] / aspect[1]
    cw = min(W, H * ar); ch = cw / ar
    if detail:
        zoom = max(zoom, 2.5)
    cw /= zoom; ch /= zoom
    sw, sh = (bx[2] - bx[0]) * W, (bx[3] - bx[1]) * H
    if detail and sw > cw * 0.9:                      # keep the whole subject at least 90 % in frame
        cw = min(W, sw / 0.9); ch = cw / ar
    x = sx * W - subject_at[0] * cw; y = sy * H - subject_at[1] * ch
    x = min(max(0, x), W - cw); y = min(max(0, y), H - ch)
    c = im.crop((int(x), int(y), int(x + cw), int(y + ch)))
    if out: c.save(out, quality=92)
    return c

def cutout(path, out, feather=2):
    im = Image.open(path).convert('RGB')
    try:
        from rembg import remove
        res = remove(im)
    except ImportError:
        venv = '/workspace/venv-rembg/bin/python'
        if os.path.exists(venv) and subprocess.run([venv, '-c', 'import rembg'], capture_output=True).returncode == 0:
            subprocess.run([venv, '-c', f'from rembg import remove;from PIL import Image;remove(Image.open({path!r})).save({out!r})'], check=True)
            res = Image.open(out)
        else:
            import cv2
            a = np.asarray(im)[:, :, ::-1].copy(); h, w = a.shape[:2]; b = analyze(path)['subject_box']
            r = (int(b[0] * w), int(b[1] * h), int((b[2] - b[0]) * w), int((b[3] - b[1]) * h))
            mask = np.zeros((h, w), np.uint8); bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
            cv2.grabCut(a, mask, r, bg, fg, 5, cv2.GC_INIT_WITH_RECT)
            alpha = np.where((mask == 1) | (mask == 3), 255, 0).astype('uint8')
            res = im.convert('RGBA'); res.putalpha(Image.fromarray(alpha))
            print('cutout: rembg not found, used GrabCut (check the edge)', file=sys.stderr)
    if feather:
        al = res.getchannel('A').filter(ImageFilter.GaussianBlur(feather)); res.putalpha(al)
    bb = res.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox()
    res = res.crop(bb) if bb else res
    res.save(out); return res

def mask(path, shape, out, aspect=(1, 1)):
    c = crop(path, aspect); W, H = c.size; m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if shape == 'circle': d.ellipse((0, 0, W - 1, H - 1), fill=255)
    elif shape == 'arch': d.rectangle((0, W // 2, W, H), fill=255); d.ellipse((0, 0, W - 1, W - 1), fill=255)
    elif shape == 'pill': d.rounded_rectangle((0, 0, W - 1, H - 1), radius=min(W, H) // 2, fill=255)
    elif shape == 'band': d.rectangle((0, int(H * .3), W, int(H * .7)), fill=255)
    elif shape.startswith('poly:'):
        pts = [tuple(float(v) for v in p.split(',')) for p in shape[5:].split(';')]
        d.polygon([(x * W, y * H) for x, y in pts], fill=255)
    r = c.convert('RGBA'); r.putalpha(m.filter(ImageFilter.GaussianBlur(1))); r.save(out); return r

def _pair(s, sep):
    a, b = s.split(sep); return float(a), float(b)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['analyze', 'crop', 'cutout', 'mask']); ap.add_argument('img')
    ap.add_argument('--out'); ap.add_argument('--json'); ap.add_argument('--grid', default='4x3'); ap.add_argument('--aspect', default='16:9')
    ap.add_argument('--subject-at', default='0.5,0.5'); ap.add_argument('--zoom', type=float, default=1.0)
    ap.add_argument('--detail', action='store_true'); ap.add_argument('--feather', type=int, default=2); ap.add_argument('--shape', default='circle'); ap.add_argument('--focus')
    a = ap.parse_args()
    if a.cmd == 'analyze':
        r = analyze(a.img, tuple(int(v) for v in a.grid.split('x'))); s = json.dumps(r, ensure_ascii=False, indent=1)
        open(a.json, 'w').write(s) if a.json else print(s)
    elif a.cmd == 'crop': crop(a.img, _pair(a.aspect, ':'), a.out, _pair(a.subject_at, ','), a.zoom, a.detail, _pair(a.focus, ',') if a.focus else None); print('wrote', a.out)
    elif a.cmd == 'cutout': cutout(a.img, a.out, a.feather); print('wrote', a.out)
    else: mask(a.img, a.shape, a.out, _pair(a.aspect, ':')); print('wrote', a.out)
