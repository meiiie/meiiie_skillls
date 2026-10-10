"""Measure text with the real font, the way PowerPoint will lay it out.

Used by build_deck.py (warnings while you build) and craft_audit.py (a finished deck).
Why: the most common defect in generated decks is text that overflows its box or wraps
one word onto a line of its own. A render shows it only if you look at the right slide;
this catches it on every slide, before the render.

  python typeset.py "Cormorant SemiBold" 54 6.0 "Một tiếng hát, hai nhạc cụ đệm" [--bold] [--line 0.9]

Fonts are resolved with fontconfig (fc-match). When the family is not installed the
measurement is skipped and `font_missing` is reported, because a fallback font would
give the wrong answer.
"""
import argparse
import functools
import re
import shutil
import subprocess
import sys

PT_PER_IN = 72.0


@functools.lru_cache(maxsize=256)
def font_file(family, bold=False, italic=False):
    """Return the path of an installed font file for family, or None if not installed."""
    if not family or not shutil.which('fc-match'):
        return None
    pattern = family + (':weight=bold' if bold else '') + (':slant=italic' if italic else '')
    try:
        out = subprocess.run(['fc-match', '-f', '%{file}\n%{family}\n%{fullname}', pattern],
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    lines = out.split('\n')
    if len(lines) < 2 or not lines[0]:
        return None
    path, fams = lines[0], (lines[1] + ',' + (lines[2] if len(lines) > 2 else '')).lower()
    want = family.lower()
    # fc-match always returns something; accept it only when the family really matches.
    names = {f.strip() for f in fams.split(',') if f.strip()}
    if want not in names:
        return None
    return path


@functools.lru_cache(maxsize=512)
def _font(path, size_px):
    from PIL import ImageFont
    return ImageFont.truetype(path, size_px)


SCALE = 4  # measure at 4 px per point for sub-point accuracy


def measure(text, family, size, width_in, bold=False, italic=False, line=1.0, spacing=0.0, caps=False):
    """Lay text out in a box width_in wide. Returns a dict:
    lines (list of str), height_in, widest_in, longest_word_in, font_missing (bool)."""
    path = font_file(family, bool(bold), bool(italic))
    if not path:
        return {'lines': [], 'height_in': 0.0, 'widest_in': 0.0, 'longest_word_in': 0.0, 'font_missing': True}
    f = _font(path, int(round(size * SCALE)))
    asc, desc = f.getmetrics()
    line_pt = (asc + desc) / SCALE * (line or 1.0)
    maxw = width_in * PT_PER_IN

    def wpt(s):
        s2 = s.upper() if caps else s
        return f.getlength(s2) / SCALE + max(0, len(s2) - 1) * (spacing or 0)

    out_lines, longest = [], 0.0
    for para in str(text).split('\n'):
        words = para.split(' ')
        cur = ''
        for w in words:
            longest = max(longest, wpt(w))
            trial = (cur + ' ' + w) if cur else w
            if cur and wpt(trial) > maxw:
                out_lines.append(cur)
                cur = w
            else:
                cur = trial
        out_lines.append(cur)
    widest = max((wpt(l) for l in out_lines), default=0.0)
    return {
        'lines': out_lines,
        'height_in': len(out_lines) * line_pt / PT_PER_IN,
        'widest_in': widest / PT_PER_IN,
        'longest_word_in': longest / PT_PER_IN,
        'font_missing': False,
    }


def fit_problems(text, family, size, w_in, h_in, bold=False, italic=False, line=1.0, spacing=0.0, caps=False,
                 tolerance=0.06):
    """Return a list of human-readable problems ('' list when the text fits)."""
    m = measure(text, family, size, w_in, bold, italic, line, spacing, caps)
    if m['font_missing']:
        return ['font not installed: ' + family]
    probs = []
    if m['longest_word_in'] > w_in * (1 + tolerance / 2):
        probs.append(f'a word is wider than the box ({m["longest_word_in"]:.2f} in > {w_in:.2f} in): it will break mid-word')
    if h_in and m['height_in'] > h_in * (1 + tolerance) + 0.02:
        probs.append(f'{len(m["lines"])} lines need {m["height_in"]:.2f} in but the box is {h_in:.2f} in tall')
    if len(m['lines']) >= 2 and len(m['lines'][-1].split()) == 1 and len(text.split()) >= 4 and size >= 24:
        probs.append(f'last line is a single word ("{m["lines"][-1]}"): rebalance the line breaks or widen the box')
    return probs


def main(argv=None):
    ap = argparse.ArgumentParser(description='Measure text with the installed font.')
    ap.add_argument('family')
    ap.add_argument('size', type=float)
    ap.add_argument('width_in', type=float)
    ap.add_argument('text')
    ap.add_argument('--height', type=float, default=0)
    ap.add_argument('--bold', action='store_true')
    ap.add_argument('--italic', action='store_true')
    ap.add_argument('--line', type=float, default=1.0)
    ap.add_argument('--spacing', type=float, default=0.0)
    a = ap.parse_args(argv)
    m = measure(a.text, a.family, a.size, a.width_in, a.bold, a.italic, a.line, a.spacing)
    if m['font_missing']:
        print('font not installed:', a.family)
        return 1
    print(f'{len(m["lines"])} line(s), {m["height_in"]:.2f} in tall, widest {m["widest_in"]:.2f} in')
    for l in m['lines']:
        print('  |', l)
    for p in fit_problems(a.text, a.family, a.size, a.width_in, a.height, a.bold, a.italic, a.line, a.spacing):
        print('PROBLEM', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
