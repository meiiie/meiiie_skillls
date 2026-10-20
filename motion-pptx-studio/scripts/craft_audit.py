"""Craft audit: does the deck read as ONE designed piece, and does every text fit?

visual_audit.py catches decks that cheat (a still photo, one template, slogans). This
module looks for the things the accepted reference deck does on every slide and generated
decks usually skip:

  ERROR  no persistent system: no !! shape appears on at least 60% of the slides (decks of 6+).
         The reference keeps its frame and its three strings on 48/48 slides; that is what
         makes 48 slides read as one film instead of 48 templates.
  WARN   text that overflows its box, or a word wider than its box (measured with the real
         font when it is installed: typeset.py)
  WARN   text outside the safe area (0.3 in from the edge), unless parked off-slide
  WARN   more than 12 distinct text sizes (a type scale has 8-10 roles)
  WARN   a flat solid fill as the ground on most slides (use a material ground: make_assets.py ground)
  WARN   low contrast between a text colour and what is behind it (only when renders are given)
  INFO   the persistent layers, the type scale, ground kinds

  python craft_audit.py DECK.pptx [--renders DIR]
"""
import sys
from collections import Counter

from visual_audit import A, P, Audit, _abs_box, _slide_order, _Zip

EMU = 914400
SYSTEM_SHARE = 0.60
SAFE_IN = 0.30
MAX_SIZES = 12


def _runs(sp):
    """Paragraphs of a text shape: list of dicts with text, size, font, bold, italic, spacing, caps, line, color."""
    paras = []
    for p in sp.iter(A + 'p'):
        rs = list(p.iter(A + 'r'))
        text = ''.join(t.text or '' for t in p.iter(A + 't'))
        if not text.strip():
            continue
        szs, font, bold, italic, spc, caps, color = [], None, False, False, 0.0, False, None
        for r in rs:
            rpr = r.find(A + 'rPr')
            if rpr is None:
                continue
            if rpr.get('sz'):
                szs.append(int(rpr.get('sz')) / 100)
            lat = rpr.find(A + 'latin')
            if lat is not None and lat.get('typeface') and not lat.get('typeface').startswith('+'):
                font = lat.get('typeface')
            bold = bold or rpr.get('b') in ('1', 'true')
            italic = italic or rpr.get('i') in ('1', 'true')
            spc = int(rpr.get('spc') or 0) / 100 or spc
            caps = caps or rpr.get('cap') == 'all'
            c = rpr.find(A + 'solidFill/' + A + 'srgbClr')
            if c is not None and color is None:
                color = c.get('val')
        size = max(szs) if szs else 18.0
        line = 1.0
        ppr = p.find(A + 'pPr')
        if ppr is not None:
            pct = ppr.find(A + 'lnSpc/' + A + 'spcPct')
            if pct is not None:
                line = int(pct.get('val')) / 100000
        before = 0.0
        if ppr is not None:
            sb = ppr.find(A + 'spcBef/' + A + 'spcPts')
            if sb is not None:
                before = int(sb.get('val')) / 100
        paras.append({'text': text, 'size': size, 'font': font, 'bold': bold, 'italic': italic, 'spacing': spc,
                      'caps': caps, 'line': line, 'color': color, 'before': before})
    return paras


def _insets(sp):
    bp = sp.find('.//' + A + 'bodyPr')
    if bp is None:
        return 0.1, 0.1, 0.05, 0.05, None, True
    g = lambda k, d: int(bp.get(k)) / EMU if bp.get(k) is not None else d  # noqa: E731
    auto = None
    if bp.find(A + 'normAutofit') is not None or bp.find(A + 'spAutoFit') is not None:
        auto = 'auto'
    wrap = bp.get('wrap') != 'none'
    return g('lIns', 0.1), g('rIns', 0.1), g('tIns', 0.05), g('bIns', 0.05), auto, wrap


def _lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(c1, c2):
    a, b = sorted((_lum(c1), _lum(c2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def audit_craft(path, renders_dir=None, audit=None):
    import typeset
    from lxml import etree
    audit = audit or Audit()
    z = _Zip(path)
    order, sw, sh = _slide_order(z)
    n = len(order)
    audit.n = n
    presence = Counter()
    sizes = Counter()
    grounds = Counter()
    overflow, unsafe, low = [], [], []
    renders = {}
    if renders_dir:
        from visual_audit import _load_renders
        renders = _load_renders(renders_dir)
    for idx, part in enumerate(order, 1):
        t = etree.fromstring(z.read(part))
        names = {c.get('name') for c in t.iter(P + 'cNvPr') if (c.get('name') or '').startswith('!!')}
        for nm in names:
            presence[nm] += 1
        bg = t.find('.//' + P + 'bg')
        kind = 'flat'
        if bg is not None and bg.find('.//' + A + 'blip') is not None:
            kind = 'image'
        else:
            for pic in t.iter(P + 'pic'):
                b = _abs_box(pic)
                if b and b[2] * b[3] >= 0.85 * sw * sh:
                    kind = 'full-bleed photo'
                    break
        grounds[kind] += 1
        texts = []  # (name, x, y, w, h, need or None, anchor, problem)
        W, H = sw / EMU, sh / EMU
        for sp in t.iter(P + 'sp'):
            if sp.find(P + 'txBody') is None:
                continue
            paras = _runs(sp)
            if not paras:
                continue
            box = _abs_box(sp)
            if not box:
                continue
            x, y, w, h = (v / EMU for v in box)
            tw, th = w, h   # text is laid out in the unrotated box
            xf = sp.find('.//' + A + 'xfrm')
            rot = int(xf.get('rot', 0)) / 60000 if xf is not None else 0
            if rot % 180:   # v5.2: rotated text covers its rotated box, not the unrotated one
                import math as _m
                r = _m.radians(rot)
                rw, rh = abs(w * _m.cos(r)) + abs(h * _m.sin(r)), abs(w * _m.sin(r)) + abs(h * _m.cos(r))
                x, y, w, h = x + w / 2 - rw / 2, y + h / 2 - rh / 2, rw, rh
            c = sp.find('.//' + P + 'cNvPr')
            name = c.get('name') if c is not None else '?'
            for pr in paras:
                if pr['size'] >= 8:
                    sizes[round(pr['size'])] += 1
            parked = x >= W or y >= H or x + w <= 0 or y + h <= 0
            if not parked and (x < SAFE_IN - 1e-3 or y < SAFE_IN - 1e-3 or x + w > W - SAFE_IN + 1e-3 or y + h > H - SAFE_IN + 1e-3):
                unsafe.append(f'slide {idx} {name}')
            li, ri, ti, bi, auto, wrap = _insets(sp)
            iw, ih = tw - li - ri, th - ti - bi
            if iw <= 0 or parked:
                continue
            need, problem = 0.0, None
            for pr in paras:
                if not pr['font']:
                    need = None
                    break
                m = typeset.measure(pr['text'], pr['font'], pr['size'], iw if wrap else 1e6, pr['bold'], pr['italic'],
                                    pr['line'], pr['spacing'], pr['caps'])
                if m['font_missing']:
                    need = None
                    break
                need += m['height_in'] + pr['before'] / 72
                if wrap and m['longest_word_in'] > iw * 1.04:
                    problem = f'a word is wider than the box ({m["longest_word_in"]:.2f} > {iw:.2f} in): it breaks mid-word'
            bp = sp.find('.//' + A + 'bodyPr')
            anchor = (bp.get('anchor') if bp is not None else None) or 't'
            texts.append((name, x, y, w, h, None if auto else need, anchor, problem))
        # A box that is too short is harmless on its own; it matters when the text runs into
        # another text or off the slide. That is what a viewer sees.
        for name, x, y, w, h, need, anchor, problem in texts:
            if need is not None and need > h * 1.08 + 0.04:
                top = y if anchor == 't' else (y + h - need if anchor == 'b' else y + (h - need) / 2)
                bot = top + need
                hits = [o[0] for o in texts if o[0] != name and o[1] < x + w and x < o[1] + o[3]
                        and o[2] < bot and top < o[2] + o[4] and not (o[2] < y + h and y < o[2] + o[4])]
                if top < 0.05 or bot > H - 0.05:
                    problem = problem or f'text needs {need:.2f} in and runs off the slide (box {h:.2f} in)'
                elif hits:
                    problem = problem or f'text needs {need:.2f} in (box {h:.2f} in) and runs into {hits[:3]}'
            if problem:
                overflow.append(f'slide {idx} {name}: {problem}')
        for sp in t.iter(P + 'sp'):
            if sp.find(P + 'txBody') is None:
                continue
            paras = _runs(sp)
            box = _abs_box(sp)
            if not paras or not box:
                continue
            x, y, w, h = (v / EMU for v in box)
            tw, th = w, h   # text is laid out in the unrotated box
            xf = sp.find('.//' + A + 'xfrm')
            rot = int(xf.get('rot', 0)) / 60000 if xf is not None else 0
            if rot % 180:   # v5.2: rotated text covers its rotated box, not the unrotated one
                import math as _m
                r = _m.radians(rot)
                rw, rh = abs(w * _m.cos(r)) + abs(h * _m.sin(r)), abs(w * _m.sin(r)) + abs(h * _m.cos(r))
                x, y, w, h = x + w / 2 - rw / 2, y + h / 2 - rh / 2, rw, rh
            c = sp.find('.//' + P + 'cNvPr')
            name = c.get('name') if c is not None else '?'
            if renders.get(idx) is not None and paras[0]['color']:
                im = renders[idx]
                rx, ry = im.width / W, im.height / H
                l, tp = max(0, int(x * rx)), max(0, int(y * ry))
                r, bt = min(im.width, int((x + w) * rx)), min(im.height, int((y + h) * ry))
                crop = im.crop((l, tp, r, bt)) if r - l > 2 and bt - tp > 2 else None
                if crop is not None:
                    import numpy as np
                    arr = np.asarray(crop.convert('RGB')).reshape(-1, 3)
                    lumv = arr @ np.array([0.2126, 0.7152, 0.0722])
                    px = [tuple(int(v) for v in arr[i]) for i in np.argsort(lumv)]
                    tc = tuple(int(paras[0]['color'][i:i + 2], 16) for i in (0, 2, 4))
                    # the background is whichever end of the luminance range is farther from the text colour
                    lo, hi = px[len(px) // 10], px[-len(px) // 10]
                    bgc = lo if abs(_lum(lo) - _lum(tc)) > abs(_lum(hi) - _lum(tc)) else hi
                    med = px[len(px) // 2]
                    bgc = med if abs(_lum(med) - _lum(tc)) > abs(_lum(bgc) - _lum(tc)) * 0.8 else bgc
                    ratio = contrast(tc, bgc)
                    need_ratio = 3.0 if paras[0]['size'] >= 24 or paras[0]['bold'] and paras[0]['size'] >= 18 else 4.5
                    if ratio < need_ratio and paras[0]['size'] >= 10:
                        low.append(f'slide {idx} {name}: {ratio:.1f}:1 (need {need_ratio:.1f}:1)')
    persistent = sorted(((nm, k) for nm, k in presence.items() if k >= SYSTEM_SHARE * n), key=lambda kv: -kv[1])
    if n >= 6 and not persistent:
        top = presence.most_common(3)
        audit.error(f'no persistent system: no !! shape is on {SYSTEM_SHARE:.0%} of the {n} slides (most persistent: {top}). '
                    'Give the deck a frame, a rail or a signature object that carries through (style chrome or a !! layer).')
    else:
        audit.info('system: ' + ', '.join(f'{nm} {k}/{n}' for nm, k in persistent[:6]))
    scale = sorted(sizes)
    audit.info(f'type scale: {scale}')
    if len(scale) > MAX_SIZES:
        audit.warn(f'{len(scale)} distinct text sizes {scale}: keep to the style pack type roles (8-10 steps)')
    audit.info('grounds: ' + ', '.join(f'{k} {v}' for k, v in grounds.items()))
    if n >= 6 and grounds['flat'] > 0.7 * n:
        audit.warn(f'flat colour ground on {grounds["flat"]}/{n} slides: use a material ground (make_assets.py ground, style grounds)')
    if unsafe:
        audit.warn(f'text outside the {SAFE_IN} in safe area on {len(unsafe)} shape(s): {unsafe[:8]}')
    for o in overflow[:20]:
        audit.warn('text overflow: ' + o)
    if len(overflow) > 20:
        audit.warn(f'... and {len(overflow) - 20} more text overflows')
    for lo_ in low[:12]:
        audit.warn('low contrast: ' + lo_)
    return audit


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck')
    ap.add_argument('--renders')
    a = ap.parse_args(argv)
    from visual_audit import print_audit
    au = audit_craft(a.deck, a.renders)
    print_audit(a.deck, au)
    return 1 if au.errors else 0


if __name__ == '__main__':
    sys.exit(main())
