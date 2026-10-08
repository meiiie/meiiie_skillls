"""Check that a font really covers the text you will put on slides (e.g. every Vietnamese diacritic).

Usage:
  python check_fonts.py FONT [FONT ...] [--lang vi] [--text "Hỏi trước, rồi mới làm."] [--text-file notes.md]
                        [--png sample.png]
FONT is a .ttf/.otf path or a family name resolved with fc-match (Linux/macOS with fontconfig).
--lang vi adds the full Vietnamese alphabet in both cases with all five tone marks.
--png renders the sample in every font so you can LOOK at diacritic stacking (ẫ, ợ, Ỹ):
a font can "have" the glyphs and still collide marks with the line above (we rejected
Great Vibes for that) or miss them entirely (Bodoni Moda had no ơ ư ỹ ẫ).
Also warns when the file is a variable font: PowerPoint handles variable fonts poorly, so
ship the static instances (Google Fonts zips have a static/ folder).
Exit code 1 if any font misses a character.
"""
import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

VI_BASE = 'aăâeêioôơuưy'
TONES = ['', '\u0301', '\u0300', '\u0309', '\u0303', '\u0323']


def vietnamese():
    chars = set('đĐ')
    for b in VI_BASE:
        for t in TONES:
            for c in (b, b.upper()):
                chars.add(unicodedata.normalize('NFC', c + t))
    return ''.join(sorted(chars)) + ' “”‘’–—…·'


def resolve(font):
    p = Path(font)
    if p.is_file():
        return p
    try:
        out = subprocess.run(['fc-match', '-f', '%{file}', font], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ''
    if out and Path(out).is_file():
        fam = subprocess.run(['fc-match', '-f', '%{family}', font], capture_output=True, text=True).stdout
        if font.lower().split(':')[0] not in fam.lower():
            print(f'WARNING: "{font}" is not installed; fc-match fell back to {fam} ({out})')
            return None
        return Path(out)
    print(f'WARNING: cannot resolve font "{font}" (give a .ttf path)')
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description='Glyph coverage check for slide text.')
    ap.add_argument('fonts', nargs='+')
    ap.add_argument('--lang', choices=('vi', 'none'), default='vi')
    ap.add_argument('--text', default='')
    ap.add_argument('--text-file')
    ap.add_argument('--png')
    a = ap.parse_args(argv)
    text = a.text
    if a.text_file:
        text += Path(a.text_file).read_text(encoding='utf-8')
    if a.lang == 'vi':
        text += vietnamese()
    text = unicodedata.normalize('NFC', text)
    needed = sorted({c for c in text if not c.isspace() and unicodedata.category(c)[0] != 'C'})
    bad = 0
    paths = []
    for f in a.fonts:
        p = resolve(f)
        if p is None:
            bad += 1
            continue
        tt = TTFont(str(p), fontNumber=0, lazy=True)
        cmap = tt.getBestCmap() or {}
        miss = [c for c in needed if ord(c) not in cmap]
        var = 'fvar' in tt
        name = tt['name'].getDebugName(4) or p.name
        status = 'PASS' if not miss else 'FAIL'
        print(f'{status} {name} ({p.name}): {len(needed) - len(miss)}/{len(needed)} characters'
              + (f'; missing: {"".join(miss[:60])}' if miss else ''))
        if var:
            print(f'  WARN variable font: ship static instances (e.g. {name}-Regular.ttf, -Bold.ttf) for PowerPoint')
        bad += bool(miss)
        paths.append((name, p))
    if a.png and paths:
        from PIL import Image, ImageDraw, ImageFont
        sample = (a.text.strip() or 'Hỏi trước, rồi mới làm.') + '\nẪ ẫ Ợ ợ Ỹ ỹ Ự ự Ặ ặ Ề ề Đ đ — Ca Trù · Đàn đáy'
        rows = []
        for name, p in paths:
            fnt = ImageFont.truetype(str(p), 54)
            im = Image.new('RGB', (1800, 190), 'white')
            d = ImageDraw.Draw(im)
            d.text((20, 8), name, fill=(150, 30, 30), font=ImageFont.truetype(str(p), 22))
            d.multiline_text((20, 40), sample, fill='black', font=fnt, spacing=6)
            rows.append(im)
        out = Image.new('RGB', (1800, 190 * len(rows)), 'white')
        for i, im in enumerate(rows):
            out.paste(im, (0, i * 190))
        out.save(a.png)
        print('sample rendered ->', a.png, '(LOOK at it: marks must not collide or fall back)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
