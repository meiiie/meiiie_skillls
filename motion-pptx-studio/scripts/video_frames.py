"""Extract frames from a video (the user's product video or a reference talk) for auditing.

  python video_frames.py VIDEO --out frames/ [--every 5] [--scene 0.35] [--width 854] [--sheet]
     --every N   one frame every N seconds (default 5)
     --scene T   instead: a frame at every scene change above threshold T (0.2-0.5)
     --sheet     also write frames/contact.jpg with time-coded labels
Frames are named f_<seconds>.jpg (f_037.jpg = 0:37) so the accuracy audit can cite them.

Getting the video first:
  YouTube / most sites :  yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" -o ref.mp4 URL
                          yt-dlp --write-auto-subs --sub-langs "en.*,vi.*" --skip-download -o ref URL  (transcript)
  Google Drive (public):  curl -L -o video.mp4 "https://drive.usercontent.google.com/download?id=FILE_ID&export=download&confirm=t"
  Shrink for analysis  :  ffmpeg -i in.mp4 -vf scale=854:-2 -c:v libx264 -crf 28 -an small.mp4
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description='Time-coded frames + contact sheet.')
    ap.add_argument('video')
    ap.add_argument('--out', required=True)
    ap.add_argument('--every', type=float, default=5.0)
    ap.add_argument('--scene', type=float)
    ap.add_argument('--width', type=int, default=854)
    ap.add_argument('--sheet', action='store_true')
    a = ap.parse_args(argv)
    if not shutil.which('ffmpeg'):
        raise SystemExit('ffmpeg not found: run setup.sh')
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / '_tmp'
    tmp.mkdir(exist_ok=True)
    if a.scene:
        vf = f"select='gt(scene,{a.scene})',scale={a.width}:-2,showinfo"
        cmd = ['ffmpeg', '-hide_banner', '-i', a.video, '-vf', vf, '-vsync', 'vfr', str(tmp / 'x_%05d.jpg')]
    else:
        vf = f'fps=1/{a.every},scale={a.width}:-2,showinfo'
        cmd = ['ffmpeg', '-hide_banner', '-i', a.video, '-vf', vf, str(tmp / 'x_%05d.jpg')]
    r = subprocess.run(cmd, capture_output=True, text=True)
    times = [float(t) for t in re.findall(r'pts_time:([\d.]+)', r.stderr)]
    files = sorted(tmp.glob('x_*.jpg'))
    if not files:
        raise SystemExit('no frames extracted:\n' + r.stderr[-800:])
    for i, f in enumerate(files):
        t = times[i] if i < len(times) else i * a.every
        dest = out / f'f_{int(t):03d}.jpg'
        k = 1
        while dest.exists():
            dest = out / f'f_{int(t):03d}_{k}.jpg'
            k += 1
        f.rename(dest)
    shutil.rmtree(tmp, ignore_errors=True)
    n = len(list(out.glob('f_*.jpg')))
    print(f'{n} frames -> {out}')
    if a.sheet:
        sys.path.insert(0, str(Path(__file__).parent))
        import contact_sheet
        contact_sheet.main([str(out), '--out', str(out / 'contact.jpg'), '--cols', '6', '--width', '300', '--per-sheet', '36'])
    print('NEXT: audit every frame against research/accuracy.md (wrong instrument details, AI hands, wrong technique, burned-in text).')


if __name__ == '__main__':
    main()
