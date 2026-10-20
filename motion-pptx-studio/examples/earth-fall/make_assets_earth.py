"""Deck-specific assets for 'Trái Đất': graded photos, cut-out layers, and a hand-rendered rotating globe film.
All sources are NASA/USGS public domain (see assets/CREDITS.md)."""
import subprocess, sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

A = Path(__file__).resolve().parent / 'assets'
Image.MAX_IMAGE_PIXELS = None
BG = (5, 7, 11)


def pbd():
    im = Image.open(A / 'pale_blue_dot.png').convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    # locate the dot: brightest small feature near the expected place
    sub = a[2500:2850, 2950:3300].sum(2)
    yy, xx = np.unravel_index(np.argmax(sub), sub.shape)
    dx, dy = 2950 + xx, 2500 + yy
    ch = int(W * 9 / 16)
    y0 = int(np.clip(dy - ch * 0.5, 0, H - ch))
    crop = im.crop((0, y0, W, y0 + ch))
    crop.save(A / 'pbd_wide.jpg', quality=90)
    print('dot at', dx, dy, '-> wide crop frac', dx / W, (dy - y0) / ch)
    return dx / W, (dy - y0) / ch


def earthrise():
    im = Image.open(A / 'earthrise.jpg').convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2)
    # moon: per column, first row (from 60% height down) brighter than 40 and everything below
    alpha = np.zeros((H, W), np.uint8)
    top = int(H * 0.6)
    for x in range(W):
        col = lum[top:, x]
        idx = np.argmax(col > 38)
        alpha[top + idx:, x] = 255
    m = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.2))
    moon = im.copy(); moon.putalpha(m)
    bbox = (0, int(H * 0.68), W, H)
    moon.crop(bbox).save(A / 'er_moon.png')
    # earth: bright, bluish pixels in the upper area
    box = (int(W * 0.47), int(H * 0.43), int(W * 0.67), int(H * 0.6))
    e = im.crop(box)
    ea = np.asarray(e).astype(np.float32)
    al = np.clip((ea.max(2) - 18) * 6, 0, 255).astype(np.uint8)
    e.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(0.8)))
    e.save(A / 'er_earth.png')
    print('earthrise moon bbox', bbox, 'earth box', box, e.size)


def blue_marble():
    im = Image.open(A / 'blue_marble.jpg').convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2)
    ys, xs = np.where(lum > 30)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2
    S = int(r * 2) + 8
    box = (int(cx - S / 2), int(cy - S / 2), int(cx + S / 2), int(cy + S / 2))
    c = im.crop(box)
    yy, xx = np.mgrid[0:S, 0:S]
    d = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2)
    al = np.clip((r + 1.5 - d) * 255 / 3, 0, 255).astype(np.uint8)
    c.putalpha(Image.fromarray(al))
    c.thumbnail((2200, 2200))
    c.save(A / 'bm_disc.png')
    print('blue marble disc', c.size)


def photos():
    for src, dst, w in (('limb_sunset.jpg', 'limb.jpg', 2560), ('lava.jpg', 'lava_g.jpg', 2400)):
        im = Image.open(A / src).convert('RGB')
        im.thumbnail((w, w))
        im.save(A / dst, quality=88)


def globe(n=450, size=900, out='globe.mp4'):
    day = np.asarray(Image.open(A / 'tex_day.jpg').convert('RGB')).astype(np.float32) / 255
    night = np.asarray(Image.open(A / 'tex_night.jpg').convert('RGB').resize((day.shape[1], day.shape[0]))).astype(np.float32) / 255
    TH, TW = day.shape[:2]
    R = 0.86                                     # globe radius in frame units
    v, u = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (u + 0.5) / size * 2 - 1; v = 1 - (v + 0.5) / size * 2
    x, y = u / R, v / R
    rr = x * x + y * y
    inside = rr <= 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    tilt = np.radians(23.4)
    # undo axial tilt (axis leans right, as in the seasons film)
    xt = x * np.cos(tilt) - y * np.sin(tilt)
    yt = x * np.sin(tilt) + y * np.cos(tilt)
    lat = np.arcsin(np.clip(yt, -1, 1))
    L = np.array([-0.86, 0.18, 0.47]); L /= np.linalg.norm(L)
    dl = x * L[0] + y * L[1] + z * L[2]
    dayw = np.clip((dl + 0.08) / 0.26, 0, 1); dayw = dayw * dayw * (3 - 2 * dayw)
    shade = np.clip(dl, 0, 1) ** 0.5 * 0.85 + 0.15
    # atmosphere rim
    dist = np.sqrt(rr) * R
    rim = np.clip(1 - (dist - R) / 0.05, 0, 1) * (dist >= R) * 0.9
    rim_in = np.clip((dist - R * 0.9) / (R * 0.1), 0, 1) * inside * 0.35
    lit_side = np.clip(0.25 + (x * L[0] + y * L[1]) * 0.9, 0, 1)
    bg = np.array(BG, np.float32) / 255
    rowi = np.clip(((0.5 - lat / np.pi) * TH).astype(int), 0, TH - 1)
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{size}x{size}', '-r', '30', '-i', '-',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '27', '-preset', 'medium', '-movflags', '+faststart', str(A / out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    poster = None
    for f in range(n):
        ph = 2 * np.pi * f / n
        lon = np.arctan2(xt, z) - ph + np.pi * 0.6
        coli = (((lon / (2 * np.pi)) % 1) * TW).astype(int) % TW
        dc = day[rowi, coli]; nc = night[rowi, coli]
        nightc = nc * np.array([1.25, 1.0, 0.65]) * 1.3 + np.array([0.004, 0.008, 0.02])
        col = dc * shade[..., None] * dayw[..., None] + nightc * (1 - dayw[..., None])
        col = col + rim_in[..., None] * np.array([0.35, 0.6, 1.0]) * lit_side[..., None]
        img = np.where(inside[..., None], col, bg)
        img = img + (rim[..., None] * np.array([0.45, 0.72, 1.0]) * lit_side[..., None]) * (~inside)[..., None]
        fr = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        p.stdin.write(fr.tobytes())
        if f == 0:
            poster = fr
    p.stdin.close(); p.wait()
    Image.fromarray(poster).save(A / out.replace('.mp4', '.poster.png'))
    print('globe film', n, 'frames')


if __name__ == '__main__':
    what = sys.argv[1:] or ['pbd', 'earthrise', 'blue_marble', 'photos', 'globe']
    for w in what:
        globals()[w]()
