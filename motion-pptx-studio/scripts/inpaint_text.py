"""Remove unwanted script (e.g. Han characters on couplets / plaques, brand text on a mat) from a photo region.

  python inpaint_text.py IN.jpg OUT.jpg --box x0,y0,x1,y1 [--box ...] [--thr 20] [--dilate 5]
                         [--radius 9] [--vblur 0] [--flatten] [--preview crop.png]
  --box      pixel rectangle(s) holding the text (find them on a render or with an image viewer)
  --thr      how much brighter/darker than the local background a stroke must be (lower = more aggressive)
  --vblur N  vertical smoothing for tall pillar couplets (e.g. 61)
  --flatten  replace each box with its smoothed median colour (plain lacquer panels / hoành phi)
Keep the original in media_orig/. If the photo is CC BY-SA, the edited file stays CC BY-SA and the
credit line must say "(đã chỉnh sửa / edited)". Always LOOK at the result (--preview) before using it.
"""
import argparse
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    sys.exit('needs opencv-python-headless and numpy: bash setup.sh --install')


def clean(img, box, thr, dil, rad, vblur, flatten):
    x0, y0, x1, y1 = box
    roi = img[y0:y1, x0:x1]
    g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.int16)
    k = max(3, (min(roi.shape[:2]) // 4) | 1)
    bg = cv2.medianBlur(g.astype(np.uint8), min(31, k)).astype(np.int16)
    mask = (np.abs(g - bg) > thr).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((dil, dil), np.uint8), iterations=2)
    out = cv2.inpaint(roi, mask, rad, cv2.INPAINT_TELEA)
    if vblur:
        b = cv2.blur(out, (3, vblur))
        out = cv2.addWeighted(b, 0.8, out, 0.2, 0)
    if flatten:
        flat = np.full_like(out, np.median(out.reshape(-1, 3), axis=0).astype(np.uint8))
        out = cv2.GaussianBlur(cv2.addWeighted(cv2.GaussianBlur(out, (0, 0), 15), 0.5, flat, 0.5, 0), (0, 0), 3)
    noise = np.random.default_rng(1).normal(0, 3, out.shape)  # film grain so the patch does not look plastic
    img[y0:y1, x0:x1] = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return mask.mean() / 255


def main(argv=None):
    ap = argparse.ArgumentParser(description='Inpaint text out of photo regions.')
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--box', action='append', required=True)
    ap.add_argument('--thr', type=int, default=20)
    ap.add_argument('--dilate', type=int, default=5)
    ap.add_argument('--radius', type=int, default=9)
    ap.add_argument('--vblur', type=int, default=0)
    ap.add_argument('--flatten', action='store_true')
    ap.add_argument('--preview')
    a = ap.parse_args(argv)
    img = cv2.imread(a.src)
    if img is None:
        sys.exit('cannot read ' + a.src)
    boxes = [tuple(int(v) for v in b.split(',')) for b in a.box]
    for b in boxes:
        cov = clean(img, b, a.thr, a.dilate, a.radius, a.vblur, a.flatten)
        print(f'box {b}: {cov:.0%} of the box inpainted')
    cv2.imwrite(a.dst, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if a.preview:
        x0 = max(0, min(b[0] for b in boxes) - 80); y0 = max(0, min(b[1] for b in boxes) - 80)
        x1 = max(b[2] for b in boxes) + 80; y1 = max(b[3] for b in boxes) + 80
        cv2.imwrite(a.preview, img[y0:y1, x0:x1])
        print('preview ->', a.preview, '(LOOK at it)')
    print('wrote', a.dst, '- credit it as "(đã chỉnh sửa / edited)"; BY-SA stays BY-SA')


if __name__ == '__main__':
    main()
