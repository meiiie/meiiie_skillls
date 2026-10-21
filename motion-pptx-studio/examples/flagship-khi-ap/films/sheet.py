"""contact sheet / stills of a (possibly variable-frame-rate) film.
  python3 sheet.py film.mp4 out.png t1 t2 ... [--w 960] [--cols 2]
  python3 sheet.py film.mp4 --still t out.png        one full-resolution frame
manimgx writes held frames once with a long duration, so a frame is picked by index: the last
frame whose timestamp is <= t."""
import sys, subprocess, tempfile, os, bisect
from PIL import Image, ImageDraw

def pts(film):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'frame=pts_time',
                          '-of', 'csv=p=0', film], capture_output=True, text=True).stdout.split()
    return [float(x.strip(',')) for x in out if x.strip(',').strip()]

def grab(film, t, path, P=None):
    P = P or pts(film)
    i = max(0, bisect.bisect_right(P, t + 1e-6) - 1)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', film, '-vf', f"select='eq(n\\,{i})'", '-vsync', '0',
                    '-frames:v', '1', '-update', '1', path], check=True)
    return path

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--still' in a:
        film, t, out = a[0], float(a[a.index('--still') + 1]), a[a.index('--still') + 2]
        print(grab(film, t, out)); sys.exit()
    w, cols = 960, 2
    if '--w' in a:
        i = a.index('--w'); w = int(a[i + 1]); del a[i:i + 2]
    if '--cols' in a:
        i = a.index('--cols'); cols = int(a[i + 1]); del a[i:i + 2]
    film, out, ts = a[0], a[1], [float(x) for x in a[2:]]
    P = pts(film)
    tmp = tempfile.mkdtemp()
    ims = []
    for k, t in enumerate(ts):
        p = grab(film, t, os.path.join(tmp, f'{k}.png'), P)
        im = Image.open(p).convert('RGB'); im = im.resize((w, int(im.height * w / im.width)))
        d = ImageDraw.Draw(im); d.rectangle([0, 0, 64, 22], fill='black'); d.text((6, 5), f'{t:.1f}s', fill='white')
        ims.append(im)
    rows = (len(ims) + cols - 1) // cols
    h = ims[0].height
    sheet = Image.new('RGB', (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * (w + 8), (i // cols) * (h + 8)))
    sheet.save(out)
    print(out, sheet.size)
