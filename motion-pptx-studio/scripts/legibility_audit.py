#!/usr/bin/env python3
"""Legibility rules for text that sits on photographs, and for capitals (v5.4).

  scrim      a text that lies over a picture (photo, video poster, picture-filled shape) needs something
             between them: a colour band or chip (a filled shape under the text), a gradient scrim, its own
             fill, or a darkened / duotoned picture. Text straight on a busy photo is the most common
             legibility failure in magazine-style decks (references/styles/heritage-collage.md).
  caps body  ALL CAPS is for headlines, kickers and labels. A paragraph of 12+ words set in capitals
             below 28 pt reads slowly and shouts: set it in sentence case.

python3 legibility_audit.py DECK.pptx      prints every finding; exit 1 on a caps-body paragraph
Used by check_deck.py (caps body = ERROR; scrim = WARN, ERROR with --scrim strict) and gates.py.
"""
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))

P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
EMU_W, EMU_H = 12192000, 6858000
CAPS_WORDS = 12        # a paragraph this long in capitals is body text, not a headline
CAPS_LETTERS = 50      # ... and at least this many letters (Vietnamese words are one syllable)
CAPS_MAX_PT = 28       # capitals at or above this size are display type
COVER_MIN = 0.25       # share of the text box over a picture before the rule applies
BAND_MIN = 0.7         # share of that overlap a band must cover
BAND_ALPHA_MIN = 0.35  # a band fainter than this is not a scrim


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _alpha(fill):
    a = fill.find('.//' + A + 'alpha')
    return _int(a.get('val')) / 100000 if a is not None else 1.0


def _darkened(el):
    """A picture toned down enough to carry text: negative brightness, duotone or a strong lum/grey."""
    for lum in el.iter(A + 'lum'):
        if _int(lum.get('bright')) <= -15000:
            return True
    return el.find('.//' + A + 'duotone') is not None


def elements(root, cutout=None):
    """Top-level shapes in z-order (groups flattened): dicts kind, box, text, band, fill, dark, name."""
    tree = root.find('.//' + P + 'spTree')
    out = []
    if tree is None:
        return out

    def walk(parent):
        for el in parent:
            tag = el.tag.split('}')[-1]
            if tag == 'grpSp':
                walk(el)
                continue
            if tag not in ('sp', 'pic', 'graphicFrame', 'cxnSp'):
                continue
            xf = el.find('.//' + A + 'xfrm')
            off = xf.find(A + 'off') if xf is not None else None
            ext = xf.find(A + 'ext') if xf is not None else None
            if off is None or ext is None:
                continue
            box = (_int(off.get('x')) / EMU_W, _int(off.get('y')) / EMU_H, _int(ext.get('cx')) / EMU_W, _int(ext.get('cy')) / EMU_H)
            nv = el.find('.//' + P + 'cNvPr')
            text = ' '.join((t.text or '') for t in el.iter(A + 't')).strip()
            sppr = el.find(P + 'spPr')
            fill = None
            if sppr is not None:
                for k in ('solidFill', 'gradFill', 'blipFill'):
                    if sppr.find(A + k) is not None:
                        fill = k
                        break
            picture = tag == 'pic' or el.find('.//' + A + 'videoFile') is not None or fill == 'blipFill'
            if picture and cutout is not None and el.find('.//' + A + 'videoFile') is None:
                blip = el.find('.//' + A + 'blip')
                rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') if blip is not None else None
                if rid and cutout(rid):   # a cut-out PNG floats on the page: its empty corners are page, not photo
                    picture = False
            band = (not picture and fill in ('solidFill', 'gradFill')
                    and (fill == 'gradFill' or _alpha(sppr.find(A + 'solidFill')) >= BAND_ALPHA_MIN))
            out.append({'name': nv.get('name') if nv is not None else '', 'box': box, 'text': text, 'picture': picture,
                        'band': band, 'dark': picture and _darkened(el), 'el': el})
    walk(tree)
    return out


def _inter(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    return (x1, y1, x2 - x1, y2 - y1) if x2 > x1 and y2 > y1 else None


def _area(b):
    return b[2] * b[3] if b else 0.0


def scrim_missing(root, cutout=None):
    """Names of texts lying on a picture with no band, gradient, own fill or toned picture between.
    cutout(rId) -> True for a transparent cut-out picture (see cutout_reader); those do not count as photos."""
    els = elements(root, cutout)
    bad = []
    for i, t in enumerate(els):
        if not t['text'] or t['picture'] or len(t['text']) < 2:
            continue
        if t['band']:   # the text box has its own fill: it is its own chip
            continue
        tb = t['box']
        ta = _area(tb)
        if ta <= 0:
            continue
        for j in range(i):
            m = els[j]
            if not m['picture'] or m['dark']:
                continue
            ov = _inter(tb, m['box'])
            if _area(ov) < COVER_MIN * ta:
                continue
            covered = sum(_area(_inter(ov, els[k]['box'])) for k in range(j + 1, i) if els[k]['band'])
            if covered < BAND_MIN * _area(ov):
                bad.append(t['name'] or t['text'][:24])
                break
    return bad


def cutout_reader(src, slide_part):
    """cutout(rId) for one slide of a check_deck.Src: True when the picture has >= 15% transparent pixels."""
    import io
    from PIL import Image
    rels_name = slide_part.replace('slides/', 'slides/_rels/') + '.rels'
    try:
        rels = etree.fromstring(src.read(rels_name))
    except Exception:
        return None
    target = {r.get('Id'): r.get('Target') for r in rels}
    memo = {}

    def cutout(rid):
        t = target.get(rid)
        if not t or not t.lower().endswith('.png'):
            return False
        if t not in memo:
            name = 'ppt/' + t.replace('../', '') if t.startswith('../') else t
            try:
                im = Image.open(io.BytesIO(src.read(name)))
                if im.mode in ('RGBA', 'LA', 'P') and 'A' in im.convert('RGBA').getbands():
                    al = im.convert('RGBA').getchannel('A').resize((64, 64))
                    memo[t] = al.histogram()[0:16] and sum(al.histogram()[0:16]) / 4096 >= 0.15
                else:
                    memo[t] = False
            except Exception:
                memo[t] = False
        return memo[t]
    return cutout


def caps_body(root):
    """(name, words, pt) of paragraphs of CAPS_WORDS+ words set in capitals below CAPS_MAX_PT."""
    out = []
    for e in elements(root):
        if not e['text']:
            continue
        for p in e['el'].iter(A + 'p'):
            runs = [r for r in p.iter(A + 'r')]
            txt = ''.join((r.findtext(A + 't') or '') for r in runs)
            words = len([w for w in txt.split() if re.search(r'[^\W\d_]', w)])   # tokens with a letter: numbers do not count
            if words < CAPS_WORDS or len(re.sub(r'[\W\d_]', '', txt)) < CAPS_LETTERS:
                continue
            sizes = [_int(r.find(A + 'rPr').get('sz')) / 100 for r in runs if r.find(A + 'rPr') is not None and r.find(A + 'rPr').get('sz')]
            pt = max(sizes) if sizes else 18
            if pt >= CAPS_MAX_PT:
                continue
            capped = all((r.find(A + 'rPr') is not None and r.find(A + 'rPr').get('cap') == 'all') or not any(ch.islower() for ch in (r.findtext(A + 't') or ''))
                         for r in runs if (r.findtext(A + 't') or '').strip())
            letters = re.sub(r'[^\w]', '', txt)
            if capped and letters and not letters.isdigit():
                out.append((e['name'] or txt[:24], words, pt))
    return out


def audit_pptx(path):
    """[(position, scrim_names, caps_list)] in presentation order."""
    from check_deck import Src, slide_order
    src = Src(path)
    res = []
    for i, p in enumerate(slide_order(src), 1):
        root = etree.fromstring(src.read(p))
        res.append((i, scrim_missing(root, cutout_reader(src, p)), caps_body(root)))
    return res


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    bad = 0
    for i, sc, cb in audit_pptx(argv[0]):
        for n in sc:
            print(f'WARN  slide {i}: text {n!r} sits on a photo with no colour band, chip or gradient scrim')
        for n, w, pt in cb:
            bad += 1
            print(f'ERROR slide {i}: {n!r}: {w} words in ALL CAPS at {pt:g} pt (caps are for headlines; set body text in sentence case)')
    print('RESULT:', 'FAIL' if bad else 'PASS')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
