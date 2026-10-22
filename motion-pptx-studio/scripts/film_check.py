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
    poster = mp4.with_suffix('.poster.png')
    made = not poster.is_file() and grab_frame(mp4, poster, poster_at)
    errs = []
    if dur < 3:
        errs.append(f'{mp4.name}: plays {dur:.1f} s (need 3+)')
    if mv < 1.0:
        errs.append(f'{mp4.name}: barely changes ({mv:.1f}/255, need 1.0): move the camera or the parts')
    if not quiet:
        print(f'film     {mp4.name}: {dur:.1f} s, motion {mv:.1f}/255' + ('; poster written (last frame)' if made else ''))
        for e in errs:
            print('FAIL    ', e)
    return errs, {'seconds': round(dur, 2), 'motion': round(mv, 2)}


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
