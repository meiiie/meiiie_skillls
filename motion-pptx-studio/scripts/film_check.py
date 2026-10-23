#!/usr/bin/env python3
"""Check signature films the moment they are rendered, and that a deck really carries them.

  python3 film_check.py assets/film/NAME.mp4 [--poster-at S]   one film: >= 3 s, really moves, poster written
  python3 film_check.py --deck deck.json [--min 2]             the deck has >= MIN video shapes and every one passes

"Really moves": the largest mean frame difference at 10/40/70 % of the film is >= 1.0/255 (a lit colour on a still
drawing is not motion: move the camera or the parts). The poster (NAME.poster.png, the LAST frame unless --poster-at)
is what Google Slides, Keynote, print and a failed video show. Exit 1 on any failure: never ship a deck whose films
were silently skipped (principles/film-is-the-core.md)."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def seconds(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip() or 0)
    except ValueError:
        return 0.0


def _gray(p, t):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(p), '-frames:v', '1',
                        '-vf', 'scale=64:36,format=gray', '-f', 'rawvideo', '-'], capture_output=True)
    return r.stdout if len(r.stdout) == 64 * 36 else None


def motion(p, dur):
    fr = [f for f in (_gray(p, dur * k) for k in (0.1, 0.4, 0.7)) if f]
    if len(fr) < 2:
        return 0.0
    return max(sum(abs(a - b) for a, b in zip(fr[i], fr[j])) / len(fr[i]) for i in range(len(fr)) for j in range(i + 1, len(fr)))


def liveness(p, dur, thr=2.0):
    """Share of 1-second steps in which the picture really changes (a still hold between moves counts as dead)."""
    n = max(2, int(dur))
    fr = [_gray(p, min(dur - 0.05, k * dur / n)) for k in range(n + 1)]
    fr = [f for f in fr if f]
    if len(fr) < 2:
        return 0.0
    live = sum(sum(abs(a - b) for a, b in zip(x, y)) / len(x) > thr for x, y in zip(fr, fr[1:]))
    return live / (len(fr) - 1)


def depth_move(p, n=10):
    """Share of feature matches between frames that a 2-D pan/zoom cannot explain but a perspective
    (homography) can: ~0 for a flat frame move, >= 0.1 for a real tilt/orbit (ThreeDScene camera)."""
    try:
        import cv2, numpy as np
    except ImportError:
        return None
    cap = cv2.VideoCapture(str(p)); N = int(cap.get(7)); fr = []
    for k in range(n):
        cap.set(1, int(k * (N - 1) / (n - 1))); ok, f = cap.read()
        if ok: fr.append(cv2.cvtColor(cv2.resize(f, (640, int(640 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY))
    orb = cv2.ORB_create(1500); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True); best = 0.0
    for a, b in zip(fr, fr[1:]):
        k1, d1 = orb.detectAndCompute(a, None); k2, d2 = orb.detectAndCompute(b, None)
        if d1 is None or d2 is None or len(k1) < 12 or len(k2) < 12: continue
        m = bf.match(d1, d2)
        if len(m) < 12: continue
        P = np.float32([k1[x.queryIdx].pt for x in m]); Q = np.float32([k2[x.trainIdx].pt for x in m])
        if np.median(np.linalg.norm(P - Q, axis=1)) < 1: continue
        S, _ = cv2.estimateAffinePartial2D(P, Q, method=cv2.RANSAC, ransacReprojThreshold=2)
        Hh, _ = cv2.findHomography(P, Q, cv2.RANSAC, 2)
        if S is None or Hh is None: continue
        e = np.linalg.norm(cv2.transform(P[None], S)[0] - Q, axis=1); eh = np.linalg.norm(cv2.perspectiveTransform(P[None], Hh)[0] - Q, axis=1)
        best = max(best, float(np.mean(e > 3) - np.mean(eh > 3)))
    return best


def occupancy(png):
    """Share of the frame inside the bounding box of everything that is not background (corner colour)."""
    from PIL import Image, ImageChops
    im = Image.open(png).convert('RGB'); bg = Image.new('RGB', im.size, im.getpixel((2, 2)))
    bb = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 24 else 0).getbbox()
    return 0.0 if not bb else (bb[2] - bb[0]) * (bb[3] - bb[1]) / (im.width * im.height)


def liveness_window(p, dur, t0, t1, thr=2.0):
    """liveness() restricted to [t0, t1] of the runtime, sampled every half second."""
    n = max(2, int((t1 - t0) * dur * 2))
    fr = [f for f in (_gray(p, dur * (t0 + (t1 - t0) * k / n)) for k in range(n + 1)) if f]
    if len(fr) < 2:
        return 0.0
    return sum(sum(abs(a - b) for a, b in zip(x, y)) / len(x) > thr for x, y in zip(fr, fr[1:])) / (len(fr) - 1)


def grab_frame(mp4, out, at=None):
    """One still. at=None: the LAST frame. manimgx writes variable-frame-rate files whose held last frame starts
    seconds before the end, so `-sseof -0.25 -frames:v 1` can decode nothing: decode the last 3 s and keep
    overwriting the image (-update 1)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tries = ([['-ss', str(at), '-i', str(mp4), '-frames:v', '1']] if at is not None else
             [['-sseof', '-3', '-i', str(mp4)], ['-i', str(mp4)]])
    for args in tries:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', *args, '-update', '1', str(out)], capture_output=True)
        if out.is_file() and out.stat().st_size:
            return True
    return False


def check(mp4, poster_at=None, quiet=False):
    mp4 = Path(mp4)
    if not mp4.is_file():
        return [f'film not found: {mp4}'], {}
    dur = seconds(mp4)
    mv = motion(mp4, dur) if dur else 0.0
    lv = liveness(mp4, dur) if dur else 0.0
    dm = depth_move(mp4) if dur else None
    anatomy = mp4.with_suffix('.shapes.json').is_file()
    poster = mp4.with_suffix('.poster.png')
    made = not poster.is_file() and grab_frame(mp4, poster, poster_at)
    errs = []
    if dur < 3:
        errs.append(f'{mp4.name}: plays {dur:.1f} s (need 3+)')
    fill = occupancy(poster) if poster.is_file() else None
    # Floors catch dead films; fill + depth catch sparse flat ones (calibrated on flagship/space-v2 vs Codex, v6.6).
    if mv < 5.0:
        errs.append(f'{mp4.name}: barely changes ({mv:.1f}/255, need 5): move the camera or the parts')
    if lv < 0.35:
        errs.append(f'{mp4.name}: alive only {lv:.0%} of its seconds (need 35%): the process must keep running between camera moves')
    if fill is not None and fill < (0.5 if anatomy else 0.3):
        errs.append(f'{mp4.name}: the subject fills {fill:.0%} of the frame (need {50 if anatomy else 30}%): hero shot, push in or fit tighter')
    if dm is not None and not anatomy and dm < 0.1:   # v6.7: hard; fill no longer excuses a flat film
        errs.append(f'{mp4.name}: no 3-D camera move (depth {dm:.2f}, need 0.10): tilt or orbit >= 25 deg '
                    '(ThreeDScene.move_camera phi/theta, frame.set_euler_angles / reorient) - film-language')
    if anatomy:   # v6.7 hero rules, from the anatomy_film.py audit + the middle of the film
        au = {}
        fj = mp4.parent / mp4.stem / 'film.json'
        if fj.is_file():
            au = json.loads(fj.read_text()).get('audit', {})
        if au.get('solids') is not None and au['solids'] < 80:
            errs.append(f"{mp4.name}: {au['solids']} parts (need 80+): a hero machine has fasteners, pipes, racks")
        if au.get('line_contrast') is not None and au['line_contrast'] < 4.5:
            errs.append(f"{mp4.name}: edges {au['line_contrast']}:1 against the ground (need 4.5:1)")
        mid = liveness_window(mp4, dur, 0.2, 0.8) if dur else 0.0
        if mid < 0.6:
            errs.append(f'{mp4.name}: the medium flows in only {mid:.0%} of the middle seconds (need 60%): '
                        'water, grains or signal must travel through the machine while it works')
    if not quiet:
        print(f'film     {mp4.name}: {dur:.1f} s, motion {mv:.1f}/255, alive {lv:.0%}, depth ' + ('n/a' if dm is None else f'{dm:.2f}') + (f', fill {fill:.0%}' if fill is not None else '') + (' (anatomy)' if anatomy else '') + ('; poster written (last frame)' if made else ''))
        for e in errs:
            print('FAIL    ', e)
    return errs, {'seconds': round(dur, 2), 'motion': round(mv, 2), 'alive': round(lv, 2), 'depth': dm}


def videos(node, out):
    if isinstance(node, dict):
        if node.get('type') == 'video' and node.get('path'):
            out.append(node['path'])
        for v in node.values():
            videos(v, out)
    elif isinstance(node, list):
        for v in node:
            videos(v, out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('film', nargs='?')
    ap.add_argument('--poster-at', type=float)
    ap.add_argument('--deck')
    ap.add_argument('--min', type=int, default=2)
    a = ap.parse_args(argv)
    if a.deck:
        deck = Path(a.deck)
        vids = sorted(set(videos(json.loads(deck.read_text()), [])))
        errs = [] if len(vids) >= a.min else [f'deck has {len(vids)} film(s), need {a.min}: render them with ManimGX '
                                                f'(principles/manimgx-first.md); if ManimGX cannot run, stop and tell the user']
        for v in vids:
            p = Path(v) if Path(v).is_absolute() else deck.parent / v
            errs += check(p)[0]
        print(f'deck     {deck.name}: {len(vids)} film(s)', 'OK' if not errs else 'FAIL')
        for e in errs:
            print('FAIL    ', e)
        return 1 if errs else 0
    if not a.film:
        ap.error('give a film or --deck')
    return 1 if check(a.film, a.poster_at)[0] else 0


if __name__ == '__main__':
    sys.exit(main())
