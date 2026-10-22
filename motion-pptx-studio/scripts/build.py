#!/usr/bin/env python3
"""deck.json -> deck/NAME.pptx with transitions and animations, slide renders and a contact sheet, film check.

  python3 build.py WORK/deck.json --out WORK/deck/NAME.pptx [--no-render] [--min-films 2]

Steps: build_deck.py (shapes, text, images, video+poster) -> ooxml unpack -> motion.py (transitions, effects from
deck/motion.json) -> pack -> render.sh (LibreOffice: end state of every slide, contact-N.jpg) -> film_check --deck.
Renders go to WORK/renders/rN (a new folder every run, so you never look at a stale image)."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(args):
    r = subprocess.run([sys.executable if str(args[0]).endswith('.py') else 'bash', *map(str, args)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out[-3000:])
    if r.returncode:
        raise SystemExit(f'FAILED: {Path(str(args[0])).name} (exit {r.returncode})')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck')
    ap.add_argument('--out', required=True)
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--min-films', type=int, default=2)
    a = ap.parse_args()
    deck, out = Path(a.deck).resolve(), Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    built = out.with_name(out.stem + '.build.pptx')
    up = out.with_name(out.stem + '.unpacked')
    run([HERE / 'build_deck.py', deck, '--out', built])
    shutil.rmtree(up, ignore_errors=True)
    run([HERE / 'ooxml.py', 'unpack', built, up])
    run([HERE / 'motion.py', up])
    run([HERE / 'ooxml.py', 'pack', up, out])
    shutil.rmtree(up, ignore_errors=True)
    built.unlink(missing_ok=True)
    print('deck    ', out)
    if not a.no_render:
        root = deck.parent / 'renders'
        n = 1
        while (root / f'r{n}').exists():
            n += 1
        run([HERE / 'render.sh', out, root / f'r{n}'])
    run([HERE / 'film_check.py', '--deck', deck, '--min', a.min_films])


if __name__ == '__main__':
    main()
