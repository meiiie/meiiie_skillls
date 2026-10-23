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


def project_root(deck):
    """v6.22: the project = the nearest ancestor of deck.json holding design/ or samples/ (max 3 up); every
    gate looks for style.json, pick.md and samples only inside it, never in sibling projects."""
    for p in [deck.parent, *list(deck.parents)[1:4]]:
        if (p / 'design').is_dir() or (p / 'samples').is_dir():
            return p
    return deck.parent


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
    proj = project_root(deck); is_sample = "samples" in deck.relative_to(proj).parts
    picks = [p for p in proj.glob('**/pick.md') if '.agents' not in str(p)]
    signed = [p for p in picks if '<!-- signed: critic.sh' in p.read_text(errors='ignore')]
    # v6.22: the sample/pick step cannot be skipped: a full deck (any size) needs a signed pick.md in THIS project,
    # next to >= 3 built sample chapters, and newer than them.
    samp = [d for d in (proj / "samples").glob('*') if d.is_dir() and any(d.glob('**/*.pptx'))] if (proj / "samples").is_dir() else []
    newest = max([f.stat().st_mtime for d in samp for f in d.glob('**/*.pptx')] or [0])
    if not is_sample and not (len(samp) >= 3 and any(p.stat().st_mtime >= newest for p in signed)):
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
        gate(out, [HERE / 'style_check.py', root / f'r{n}', '--pptx', out, '--deck', deck])   # v6.21 locked style + layout rhythm
        if n_sl > 8 and not is_sample:   # v6.16 (v6.22: never on samples): image-led from the chapter photo library
            libs = [p for p in proj.glob('**/library.json') if '.agents' not in str(p) and 'samples' not in p.parts]
            if not libs:
                bad = out.with_name(out.stem + '.UNFINISHED.pptx'); out.replace(bad)
                raise SystemExit('GATE FAILED: no library/library.json - build the chapter photo library first (principles/photo-library-first.md)')
            gate(out, [HERE / 'photo_library.py', 'check', libs[0], '--deck', deck, '--pptx', out])
            hp = [p for p in proj.glob('**/hero-plan.md') if '.agents' not in str(p) and 'samples' not in p.parts]
            if not hp:
                bad = out.with_name(out.stem + '.UNFINISHED.pptx'); out.replace(bad)
                raise SystemExit('GATE FAILED: no design/hero-plan.md - plan every slide\'s visual from the library first (principles/hero-plan.md)')
            gate(out, [HERE / 'photo_library.py', 'plan', hp[0]])
    if is_sample: a.min_films = 0   # v6.21: sample chapters need no films
    gate(out, [HERE / 'film_check.py', '--deck', deck, '--min', a.min_films])
    import re as _re   # v6.21 toy-render gate on every embedded film
    fl = sorted({m for m in _re.findall(r'"([^"]+\.mp4)"', open(deck, encoding='utf-8').read())})
    fl = [str((deck.parent / f) if not Path(f).is_absolute() else f) for f in fl]
    fl = [f for f in fl if Path(f).exists() and 'SIMULATION' not in f]
    if fl: gate(out, [HERE / 'film_art.py', *fl])
    gate(out, [HERE / 'anim_check.py', out, '--deck', deck])   # v6.18 every component keyframed, purpose per slide
    if not any(deck.parent.glob('**/directions.md')):
        print('WARN     no directions.md: write three radically different directions and pick one BEFORE building '
              '(principles/three-directions.md)')


if __name__ == '__main__':
    main()
