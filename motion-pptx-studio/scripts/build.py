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


def gate(out, args):
    """v6.10: a failed gate leaves no deliverable. The deck is renamed NAME.UNFINISHED.pptx; fix and rebuild,
    or tell the user plainly which gate failed and why. Never hand over an UNFINISHED file as done."""
    try:
        run(args)
    except SystemExit:
        bad = out.with_name(out.stem + '.UNFINISHED.pptx')
        if out.exists():
            out.replace(bad)
        raise SystemExit(f'GATE FAILED: {Path(str(args[0])).name}. Deck moved to {bad.name}: not deliverable until it passes.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck')
    ap.add_argument('--out', required=True)
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--min-films', type=int, default=2)
    a = ap.parse_args()
    deck, out = Path(a.deck).resolve(), Path(a.out).resolve()
    import json
    n_sl = len([x for x in json.load(open(deck)).get('slides', []) if not x.get('hidden')])
    picks = [p for p in deck.parent.parent.glob('**/pick.md') if '.agents' not in str(p)] + list(deck.parent.glob('**/pick.md'))
    if n_sl > 8 and not any('<!-- signed: critic.sh' in p.read_text(errors='ignore') for p in picks):
        raise SystemExit('REFUSED: no critic-signed pick.md. Build the 3 sample chapters (<= 8 slides each), run '
                         '`scripts/critic.sh --pick samples`; if it cannot start, STOP here and tell the user the samples '
                         'are ready for an independent pick (principles/sample-chapters.md). Never write pick.md yourself.')
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
        # v6.7: photo reading is a gate (text over busy areas, empty fields, chapter without bleed / cut-out)
        gate(out, [HERE / 'art_check.py', root / f'r{n}', '--pptx', out, '--deck', deck])
        if n_sl > 8:   # v6.16: image-led from the chapter photo library
            libs = [p for p in deck.parent.glob('**/library.json') if '.agents' not in str(p)] + \
                   [p for p in deck.parent.parent.glob('library/library.json')]
            if not libs:
                bad = out.with_name(out.stem + '.UNFINISHED.pptx'); out.replace(bad)
                raise SystemExit('GATE FAILED: no library/library.json - build the chapter photo library first (principles/photo-library-first.md)')
            gate(out, [HERE / 'photo_library.py', 'check', libs[0], '--deck', deck, '--pptx', out])
    gate(out, [HERE / 'film_check.py', '--deck', deck, '--min', a.min_films])
    gate(out, [HERE / 'anim_check.py', out, '--deck', deck])   # v6.18 every component keyframed, purpose per slide
    if not any(deck.parent.glob('**/directions.md')):
        print('WARN     no directions.md: write three radically different directions and pick one BEFORE building '
              '(principles/three-directions.md)')


if __name__ == '__main__':
    main()
