"""Speaking-time budget: plan words per slide BEFORE writing, and measure the script AFTER.

Why: the storyboard of our ca trù deck said "48 slides x 7 s = 5.6 min"; the finished script
ran 11:53-13:36. The neko-core storyboard said ~6 min; it ran 8:28. Seconds-per-slide plans
lie. Budget WORDS per slide up front and measure them.

Plan mode (before writing any notes):
  python words_budget.py plan --minutes 6 --slides 34 [--wpm 130] [--pauses 8] [--morph-ms 1300]
  -> total spoken-word budget and the average per slide. Keyframe slides inside a motion run
     usually get 0-12 words; content slides take the rest.

Measure mode (after notes exist):
  python words_budget.py measure NOTES.md|DECK.pptx|UNPACKED_DIR [--target 6:00] [--wpm 130]
         [--wpm-fast 150] [--scenes scenes.json] [--count-morph]
  NOTES.md uses '##### N' blocks (ooxml.py notes-get writes them). A deck is read directly.
  Spoken words = whitespace tokens of lines that are NOT directions or sources. Skipped lines start
  with: Nguồn, Source, Ảnh, Photo, Motion, Ghi chú, Note, Cue, Credit, or are only [bracketed].
  Pause marks like [ngừng 2 giây] / [pause 2s] add their seconds. Exit 1 when the slow estimate is
  more than 10 % over --target.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

SKIP = re.compile(r'^\s*(Nguồn|Source|Sources|Ảnh|Photo|Motion|Ghi chú|Note|Notes|Cue|Credit|Credits|Hình|Fact)\b', re.I)
PAUSE = re.compile(r'\[(?:ngừng|ngưng|dừng|pause)\s*(\d+(?:[.,]\d+)?)\s*(?:giây|s|sec|seconds)?\s*\]', re.I)
BRACKET = re.compile(r'\[[^\]]*\]')
# Vietnamese is counted by syllable-tokens. Typical presenter pace: 130 (calm, TV) - 150 (brisk).


def spoken(line):
    if SKIP.match(line):
        return 0, 0.0
    pauses = sum(float(x.replace(',', '.')) for x in PAUSE.findall(line))
    words = len(BRACKET.sub(' ', line).split())
    return words, pauses


def fmt(sec):
    return f'{int(sec // 60)}:{int(round(sec % 60)):02d}'


def parse_minutes(s):
    if ':' in s:
        m, sec = s.split(':')
        return int(m) * 60 + int(sec)
    return float(s) * 60


def load_blocks(path):
    p = Path(path)
    if p.suffix == '.md' or p.suffix == '.txt':
        blocks = []
        for blk in p.read_text(encoding='utf-8').split('##### ')[1:]:
            head, _, body = blk.partition('\n')
            blocks.append((int(head.split()[0]), body.splitlines()))
        return blocks
    sys.path.insert(0, str(Path(__file__).parent))
    from check_deck import Src, slide_order, notes_part, notes_text
    src = Src(p)
    return [(i, notes_text(src, notes_part(src, part)).splitlines()) for i, part in enumerate(slide_order(src), 1)]


def plan(a):
    total = a.minutes * 60 - a.pauses * 2 - (a.slides * a.morph_ms / 1000 if a.count_morph else 0)
    words = int(total / 60 * a.wpm)
    print(f'target {a.minutes:g} min, {a.slides} slides, {a.wpm} words/min, {a.pauses} two-second pauses')
    print(f'TOTAL spoken-word budget: {words} words  (average {words / a.slides:.0f} per slide)')
    print('rule of thumb: keyframe-only slides 0-12 words, content slides 25-45, hook/close 15-30.')
    print('write the per-slide budget into the storyboard "words" column; the column must sum to <= the total.')


def measure(a):
    blocks = load_blocks(a.source)
    rows, tw, tp = [], 0, 0.0
    for n, lines in blocks:
        w = p = 0
        for line in lines:
            ww, pp = spoken(line)
            w += ww
            p += pp
        rows.append((n, w, p))
        tw += w
        tp += p
    morph = (len(blocks) * a.morph_ms / 1000) if a.count_morph else 0
    slow = tw / a.wpm * 60 + tp + morph
    fast = tw / a.wpm_fast * 60 + tp + morph
    print(f'{len(blocks)} slides, {tw} spoken words, {tp:g} s of marked pauses' + (f', {morph:g} s Morph' if morph else ''))
    print(f'estimate: {fmt(fast)} (at {a.wpm_fast} wpm) - {fmt(slow)} (at {a.wpm} wpm)')
    if a.scenes:
        for sc in json.loads(Path(a.scenes).read_text(encoding='utf-8')):
            w = sum(r[1] for r in rows if sc['start'] <= r[0] <= sc['end'])
            p = sum(r[2] for r in rows if sc['start'] <= r[0] <= sc['end'])
            print(f'  {sc["name"][:40]:40} slides {sc["start"]}-{sc["end"]}: {w} words, ~{fmt(w / a.wpm * 60 + p)}')
    heavy = sorted(rows, key=lambda r: -r[1])[:5]
    print('heaviest slides:', ', '.join(f'#{n}={w}w' for n, w, _ in heavy))
    if a.target:
        t = parse_minutes(a.target)
        over = slow - t
        print(f'target {fmt(t)}: ' + ('OK' if over <= 0.1 * t else f'OVER by {fmt(over)} -> trim ~{int(over / 60 * a.wpm)} words'))
        if over > 0.1 * t:
            sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Speaking-time budget.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('plan')
    s.add_argument('--minutes', type=float, required=True)
    s.add_argument('--slides', type=int, required=True)
    s.add_argument('--wpm', type=int, default=130)
    s.add_argument('--pauses', type=int, default=6)
    s.add_argument('--morph-ms', type=int, default=1300)
    s.add_argument('--count-morph', action='store_true', help='subtract Morph time (silent transitions)')
    s = sub.add_parser('measure')
    s.add_argument('source')
    s.add_argument('--target')
    s.add_argument('--wpm', type=int, default=130)
    s.add_argument('--wpm-fast', type=int, default=150)
    s.add_argument('--scenes')
    s.add_argument('--morph-ms', type=int, default=1300)
    s.add_argument('--count-morph', action='store_true')
    a = ap.parse_args(argv)
    plan(a) if a.cmd == 'plan' else measure(a)


if __name__ == '__main__':
    main()
