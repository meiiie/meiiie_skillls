"""A deck's own design genome (v5.5): decisions on open axes, compiled into a style for build_deck, and a
distance that proves two decks are genuinely different (not one template recoloured).

  python3 genome.py compile WORK/design/genome.json [--out WORK/design/style.json] [--root WORK]
  python3 genome.py distance A B [--renders-a DIR --renders-b DIR]   A/B: .pptx decks (or style/genome .json)
  python3 genome.py axes                                             print the design space (references/design-space.md)

genome.json — every axis is a decision with a reason that comes from THIS subject (no defaults to copy):
  {"name": "falcon-night", "route": "noir-product",          the routed family it starts from (route.py), optional
   "why": {"material": "...", "palette": "...", ...},          one line per axis: why, from the subject or its pictures
   "light": "dark" | "light" | "mid",
   "palette": {"ground": "#0B0D10", "ink": "#E9EEF2", "accent": "#FF6A1A", "accent2": "#7FB3D5", "ground2": "#141A20"}
              or {"from_image": "assets/10_demo2_launch.jpg", "accent_pick": "vivid"},   sampled from a real picture
   "type": {"display": "Big Shoulders Display", "text": "Be Vietnam Pro", "label": "JetBrains Mono",
            "ratio": 1.414, "body": 16, "display_case": "upper|as-is", "tracking": -1},
   "grid": {"cols": 12, "margin": 0.7, "gutter": 0.2, "top": 0.7, "bottom": 0.7},
   "material": {"kind": "noir|paper|clean|flat|lacquer|halftone|gradient", "grain": 0.04, "tone": "#..."},
   "chrome": {"page": "br|bl|tr|tl|none", "rule": "bottom|top|left|none", "running": true},
   "motion": {"tempo_ms": 1100, "stagger_ms": 90, "transitions": ["push", "morph"], "verbs": ["create", "grow", "camera"]},
   "signature": "..."}
The compiled style keeps every role build_deck needs, enforces 4.5:1 for read text and 3:1 for the accent on its
ground, and stays within 8 type sizes.
"""
import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
AXES = {
    'material': 'what the ground is made of — taken from the subject (night sky, aged print, steel, lacquer, sea fog, paper)',
    'light': 'where the deck lives in luminance: dark stage, daylight paper, mid-tone',
    'palette': 'ground, ink, ONE lit accent (+ an optional second): sampled from the real pictures or the object\'s materials',
    'type': 'a display voice, a reading face and a label face; a scale ratio (1.25 calm … 1.618 dramatic); case habit',
    'grid': 'columns, margins and asymmetry: where the weight sits and how much is left empty',
    'image': 'how pictures enter: full-bleed plates, cut-out objects, framed prints, duotone, none (drawn only)',
    'composition': 'an invented set of 3-5 composition moves for THIS deck (focal point, weight, planes), not a layout menu',
    'chrome': 'what never moves: page number corner, rule, running head, source line',
    'motion': 'the motion grammar: tempo, easing, cut grammar (which transition marks which boundary) and the construction verbs',
    'signature': 'one object of the subject that persists and pays off at the hook, the turn and the close',
}


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hx(c):
    return '#' + ''.join(f'{max(0, min(255, round(v))):02X}' for v in c)


def mix(a, b, k):
    ca, cb = rgb(a), rgb(b)
    return hx([x + (y - x) * k for x, y in zip(ca, cb)])


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ensure(fg, bg, need):
    """Move fg toward white or black (whichever is further from bg) until it reaches `need`:1."""
    if contrast(fg, bg) >= need:
        return fg
    target = '#FFFFFF' if lum(bg) < 0.18 else '#000000'
    for k in range(1, 41):
        c = mix(fg, target, k / 40)
        if contrast(c, bg) >= need:
            return c
    return target


def palette_from_image(path, light, pick='vivid'):
    from PIL import Image, ImageOps
    import numpy as np
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB').resize((96, 64))
    a = np.asarray(im, np.float32).reshape(-1, 3)
    l = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    mx, mn = a.max(1), a.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    order = np.argsort(l)
    dark, bright = a[order[: len(a) // 8]].mean(0), a[order[-len(a) // 8:]].mean(0)
    ground = hx(dark * 0.55) if light == 'dark' else hx(bright * 0.35 + 255 * 0.62)
    ink = '#F2F2EE' if light == 'dark' else hx(dark * 0.6)
    w = sat * (1 - abs(l / 255 - 0.55))
    accent = hx(a[int(w.argmax())])
    second = a[np.argsort(-w)[len(a) // 40]]
    return {'ground': ground, 'ink': ink, 'accent': accent, 'accent2': hx(second)}


def type_scale(t):
    b = float(t.get('body', 16))
    r = float(t.get('ratio', 1.333))
    small = max(11, round(b / r))
    sub = round(b * r * r)
    quote = round(b * r ** 3)
    title = max(36, min(60, round(b * r ** 4)))
    disp = max(72, min(130, round(b * r ** 6)))
    num = max(110, min(190, round(b * r ** 7.5)))
    return {'small': small, 'body': round(b), 'sub': sub, 'quote': quote if quote not in (sub, title) else quote + 2,
            'title': title, 'display': disp, 'numeral': num}


def compile_genome(g, root=None):
    root = Path(root) if root else None
    base = {}
    if g.get('route'):
        for d in (SKILL / 'assets' / 'styles', SKILL / 'assets' / 'styles-experimental'):
            p = d / f'{g["route"]}.json'
            if p.is_file():
                base = json.loads(p.read_text(encoding='utf-8'))
                break
        if not base:
            raise SystemExit(f'genome route {g["route"]!r}: no such family')
    light = g.get('light', 'dark')
    pal_in = dict(g.get('palette') or {})
    if pal_in.get('from_image'):
        p = Path(pal_in['from_image'])
        p = p if p.is_absolute() or not root else root / p
        sampled = palette_from_image(p, light, pal_in.get('accent_pick', 'vivid'))
        pal_in = {**sampled, **{k: v for k, v in pal_in.items() if k.startswith(('ground', 'ink', 'accent')) and isinstance(v, str) and v.startswith('#')}}
    if not all(k in pal_in for k in ('ground', 'ink', 'accent')):
        raise SystemExit('genome palette needs ground, ink and accent (or from_image)')
    G = pal_in['ground']
    away = '#FFFFFF' if lum(G) < 0.18 else '#000000'
    # Contrast is measured against the ground as it RENDERS: a stained, vignetted paper is darker at the edges
    # (where kickers, sources and page numbers sit) than its base colour, and a noir ground is lighter where it glows.
    mat0 = g.get('material') or {}
    st, vg = float(mat0.get('stains', 0) or 0), float(mat0.get('vignette', 0.15 if lum(G) >= 0.18 else 0.4))
    worst = mix(mat0.get('tone', G) if lum(G) >= 0.18 else G, away, 0.06 + 0.12 * st + 0.3 * vg * (0.35 + 0.5 * st)) if lum(G) >= 0.18 else mix(G, '#FFFFFF', 0.04)
    I = ensure(ensure(pal_in['ink'], G, 7.0), worst, 6.0)
    A = ensure(ensure(pal_in['accent'], G, 3.0), worst, 3.0)
    pal = {'ground': G, 'ground2': pal_in.get('ground2', mix(G, away, 0.06)), 'surface': pal_in.get('surface', mix(G, away, 0.1)),
           'ink': I, 'head': pal_in.get('head', I), 'muted': ensure(ensure(mix(I, G, 0.38), G, 4.6), worst, 5.0), 'faint': mix(I, G, 0.82),
           'accent': A, 'accent2': ensure(ensure(pal_in.get('accent2', mix(A, I, 0.5)), G, 3.0), worst, 3.0), 'lit': pal_in.get('lit', A),
           'veil': pal_in.get('veil', mix(G, '#000000', 0.35) if lum(G) < 0.18 else mix(I, '#000000', 0.2))}
    for k, v in pal_in.items():
        if k not in pal and isinstance(v, str) and v.startswith('#'):
            pal[k] = v
    t = g.get('type') or {}
    fonts = {'display': t.get('display', base.get('fonts', {}).get('display', 'Be Vietnam Pro')),
             'text': t.get('text', base.get('fonts', {}).get('text', 'Be Vietnam Pro')),
             'label': t.get('label', t.get('text', base.get('fonts', {}).get('label', 'Be Vietnam Pro')))}
    if t.get('script'):
        fonts['script'] = t['script']
    sc = type_scale(t)
    caps = t.get('display_case', 'as-is') == 'upper'
    trk = float(t.get('tracking', -1))
    acc_text = ensure(ensure(A, G, 4.6), worst, 4.6)
    roles = {
        'kicker': {'font': 'label', 'size': sc['small'], 'bold': True, 'spacing': 1.6, 'caps': True, 'color': 'kick'},
        'display': {'font': 'display', 'size': sc['display'], 'bold': True, 'line': 0.9, 'spacing': trk * 2, 'caps': caps, 'color': 'head'},
        'title': {'font': 'display', 'size': sc['title'], 'bold': True, 'line': 0.98, 'spacing': trk, 'caps': caps, 'color': 'head'},
        'subtitle': {'font': 'text', 'size': sc['sub'], 'line': 1.2, 'color': 'muted'},
        'body': {'font': 'text', 'size': sc['body'], 'line': 1.35, 'color': 'ink'},
        'caption': {'font': 'text', 'size': sc['small'], 'color': 'muted'},
        'label': {'font': 'label', 'size': sc['small'], 'bold': True, 'spacing': 1.2, 'caps': True, 'color': 'muted'},
        'numeral': {'font': 'display', 'size': sc['numeral'], 'bold': True, 'line': 0.82, 'spacing': trk * 3, 'color': 'accent'},
        'quote': {'font': 'display', 'size': sc['quote'], 'bold': False, 'line': 1.1, 'color': 'head'},
        'cardtitle': {'font': 'display', 'size': sc['sub'], 'bold': True, 'line': 1.0, 'color': 'head'},
        'pageno': {'font': 'label', 'size': sc['small'], 'bold': True, 'color': 'muted'},
    }
    if t.get('script'):
        roles['script'] = {'font': 'script', 'size': sc['sub'], 'color': 'accent', 'line': 1.0}
    pal['kick'] = acc_text
    gr = g.get('grid') or {}
    m = float(gr.get('margin', 0.8))
    grid = {'cols': int(gr.get('cols', 12)), 'left': float(gr.get('left', m)), 'right': float(gr.get('right', m)),
            'top': float(gr.get('top', 0.75)), 'bottom': float(gr.get('bottom', 0.75)), 'gutter': float(gr.get('gutter', 0.22)),
            'safe': float(gr.get('safe', 0.4))}
    mat = g.get('material') or {}
    kind = mat.get('kind', 'noir' if lum(G) < 0.18 else 'paper')
    grounds = {'main': {'kind': kind, 'base': G, 'tone': mat.get('tone', mix(G, A, 0.12)), 'grain': float(mat.get('grain', 0.03)), 'vignette': vg,
                        'seed': int(mat.get('seed', 7)), **{k: v for k, v in mat.items() if k not in ('kind', 'tone', 'grain', 'seed')}},
               'alt': {'kind': mat.get('alt_kind', 'flat'), 'base': pal['ground2'], 'tone': mix(pal['ground2'], A, 0.1), 'grain': 0.02, 'seed': 8}}
    ch = g.get('chrome') or {}
    W, H = 13.333, 7.5
    over = []
    rule = ch.get('rule', 'bottom')
    if rule == 'bottom':
        over.append({'type': 'line', 'name': '!!rule', 'x1': grid['left'], 'y1': H - grid['bottom'] + 0.05, 'x2': W - grid['right'],
                     'y2': H - grid['bottom'] + 0.05, 'color': 'faint', 'width': 0.75})
    elif rule == 'top':
        over.append({'type': 'line', 'name': '!!rule', 'x1': grid['left'], 'y1': grid['top'] - 0.1, 'x2': W - grid['right'],
                     'y2': grid['top'] - 0.1, 'color': 'faint', 'width': 0.75})
    elif rule == 'left':
        over.append({'type': 'line', 'name': '!!rule', 'x1': grid['left'] - 0.35, 'y1': grid['top'], 'x2': grid['left'] - 0.35,
                     'y2': H - grid['bottom'], 'color': 'faint', 'width': 0.75})
    corner = ch.get('page', 'br')
    if corner != 'none':
        x = W - grid['right'] - 1.5 if corner.endswith('r') else grid['left']
        y = H - grid['bottom'] + 0.14 if corner.startswith('b') else max(0.42, grid['top'] - 0.42)
        over.append({'type': 'text', 'name': '!!pageno', 'text': '{n}', 'x': round(x, 3), 'y': round(y, 3), 'w': 1.5, 'h': 0.25,
                     'role': 'pageno', 'align': 'r' if corner.endswith('r') else 'l'})
    if ch.get('running', True):   # the running head sits at the top, in the corner the page number does not use
        rx = grid['left'] if corner != 'tl' else W - grid['right'] - 6
        over.append({'type': 'text', 'name': '!!running', 'text': '{scene}', 'x': round(rx, 3), 'y': round(max(0.42, grid['top'] - 0.42), 3), 'w': 6,
                     'h': 0.25, 'role': 'label', 'align': 'l' if corner != 'tl' else 'r'})
    mo = g.get('motion') or {}
    style = dict(base)
    style.pop('fit', None)
    style.update({
        'name': g.get('name', 'genome'), 'label': g.get('label', g.get('signature', ''))[:120], 'route': g.get('route'),
        'palette': pal, 'fonts': fonts,
        'font_files': [{'family': f, 'weights': '400,700'} for f in dict.fromkeys(fonts.values())],
        'type': roles, 'grid': grid, 'default_bg': 'main', 'grounds': grounds, 'chrome': {'over': over},
        'card': {**base.get('card', {}), 'fill': 'surface', 'line': 'faint', 'line_width': 0.75, 'rule': 'accent',
                 'lit_fill': mix(pal['surface'], A, 0.18), 'lit_line': 'accent', 'radius': float((g.get('card') or {}).get('radius', 0.0)),
                 'dim_alpha': 0.7, 'fill_alpha': 1.0},
        'photo': {'duotone': [mix(G, '#000000', 0.2), mix(I, A, 0.15)], 'veil': 0.5},
        'motion': {'default_ms': int(mo.get('tempo_ms', 1100)), 'bloom_ms': int(mo.get('tempo_ms', 1100) * 1.5),
                   'stagger_ms': int(mo.get('stagger_ms', 90)), 'transitions': mo.get('transitions', ['morph']),
                   'effects': mo.get('effects', ['wipe', 'stretch', 'wheel']), 'verbs': mo.get('verbs', [])},
        'genome': {k: g.get(k) for k in ('why', 'signature', 'composition', 'image') if g.get(k)},
    })
    style.setdefault('screen', {'bezel': pal['surface'], 'line': pal['faint'], 'line_width': 0.75, 'radius': 0.02, 'bar': pal['ground2']})
    style.setdefault('shadow', None)
    return style


# ------------------------------------------------------------------ distance between decks
def deck_fingerprint(pptx, renders=None):
    """What a viewer would call the deck's look: colours, type, geometry, motion (all measured)."""
    import re
    import zipfile
    from collections import Counter
    sys.path.insert(0, str(HERE))
    import variety_audit
    from lxml import etree
    z = zipfile.ZipFile(pptx)
    slides = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=lambda n: int(re.findall(r'\d+', n)[-1]))
    fonts, sizes, techs, trans, boxes = Counter(), Counter(), Counter(), Counter(), []
    import motionlib
    for n in slides:
        raw = z.read(n)
        root = etree.fromstring(raw)
        for f in re.findall(rb'typeface="([^"]+)"', raw):
            fonts[f.decode()] += 1
        for s in re.findall(rb'<a:rPr[^>]*\ssz="(\d+)"', raw):
            sizes[int(s) // 100] += 1
        for t in variety_audit.effect_techniques(root):
            techs[t] += 1
        trans[motionlib.describe_transition(root)[0]] += 1
        for a_, b_, c_, d_ in re.findall(rb'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', raw):
            off, ext = (int(a_), int(b_)), (int(c_), int(d_))
            boxes.append((off[0] / 12192000, off[1] / 6858000, ext[0] / 12192000, ext[1] / 6858000))
    col = None
    if renders:
        from PIL import Image
        import numpy as np
        ims = sorted(Path(renders).glob('slide-*.jpg')) or sorted(Path(renders).glob('*.jpg'))
        acc = np.zeros((4, 4, 4))
        for p in ims[:40]:
            a = (np.asarray(Image.open(p).convert('RGB').resize((64, 36))) // 64).reshape(-1, 3)
            for r, g, b in a:
                acc[r, g, b] += 1
        col = (acc / max(1, acc.sum())).ravel().tolist()
    occ = [[0] * 6 for _ in range(4)]
    for x, y, w, h in boxes:
        if w * h > 0.01:
            for i in range(4):
                for j in range(6):
                    cx, cy = (j + 0.5) / 6, (i + 0.5) / 4
                    if x <= cx <= x + w and y <= cy <= y + h:
                        occ[i][j] += 1
    tot = sum(map(sum, occ)) or 1
    return {'fonts': dict(fonts), 'sizes': dict(sizes), 'techniques': dict(techs), 'transitions': dict(trans),
            'occupancy': [v / tot for row in occ for v in row], 'colour': col, 'slides': len(slides)}


def _hist_dist(a, b):
    keys = set(a) | set(b)
    sa, sb = sum(a.values()) or 1, sum(b.values()) or 1
    return 0.5 * sum(abs(a.get(k, 0) / sa - b.get(k, 0) / sb) for k in keys)


def _vec_dist(a, b):
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


def deck_distance(fa, fb):
    d = {'type (families)': _hist_dist(fa['fonts'], fb['fonts']), 'type (sizes)': _hist_dist(fa['sizes'], fb['sizes']),
         'motion (techniques)': _hist_dist(fa['techniques'], fb['techniques']),
         'cuts (transitions)': _hist_dist(fa['transitions'], fb['transitions']),
         'layout (occupancy)': _vec_dist(fa['occupancy'], fb['occupancy'])}
    if fa.get('colour') and fb.get('colour'):
        d['colour (rendered)'] = _vec_dist(fa['colour'], fb['colour'])
    d['overall'] = sum(d.values()) / len(d)
    return {k: round(v, 3) for k, v in d.items()}


VERB_TECH = {'create': 'wipe along the stroke (Manim Create)', 'grow': 'stretch from the contact edge (GrowFromEdge)',
             'write': 'letter-by-letter type (Write)', 'sweep': 'wheel sweep for arcs and circles',
             'camera': 'Morph camera move on the diagram (MovingCamera)', 'transform': 'Morph between part states (Transform)',
             'trace': 'motion path along the drawn line (MoveAlongPath)', 'indicate': 'indicate pulse on the lit part (Indicate)',
             'zoom': 'zoom-in for the one lit subject'}


def art_direction_md(g, st, work=None):
    """design/art-direction.md written FROM the genome, so the prose and the compiled style cannot drift.
    Every decision line carries its reason; the style choice quotes routing.md (chosen + rejected with reasons)."""
    why = g.get('why') or {}
    p = st['palette']
    src = (g.get('palette') or {}).get('from_image')
    psrc = why.get('palette', 'chosen for this deck')
    L = ['# Art direction (compiled from design/genome.json; edit the genome, not this file)', '<!-- genome -->', '',
         f'- style: design/style.json (genome "{g.get("name", "")}", family {g.get("route", "none")})',
         f'- label: {g.get("label", "")}', '']
    L += ['## Style choice']
    rj = {}
    if work is not None and (Path(work) / 'design/routing.json').is_file():
        r = json.loads((Path(work) / 'design/routing.json').read_text(encoding='utf-8'))
        ch = r.get('chosen') or {}
        if not isinstance(ch, dict):
            ch = next((x for x in r.get('ranked', []) if x.get('name') == ch), {'name': ch})
        L.append(f'- chosen: {ch.get("name")} (fit {ch.get("fit", "?")}) '
                 f'as the starting family, then re-decided axis by axis in the genome; why: {r.get("why", "")}')
        rj = r.get('rejected') or {}
        items_ = rj.items() if isinstance(rj, dict) else [(x.get('name'), x.get('reason') or '; '.join(x.get('rejected', []))) for x in rj]
        for n, why_ in list(items_)[:4]:
            L.append(f'- rejected: {n}, {why_ if isinstance(why_, str) else "; ".join(map(str, why_))}')
    else:
        L.append(f'- chosen: {g.get("route", "free genome")}; no routing.json yet (run route.py first)')
    L += ['', '## Palette (every hex with where it comes from)',
          f'- ground {p["ground"]}: {why.get("material", "the deck ground")}' + (f' (sampled from {src})' if src else ' (from the genome palette)'),
          f'- ink {p["ink"]}: from the genome ink {(g.get("palette") or {}).get("ink", "(sampled)")}, held at 7:1+ against the ground as it renders',
          f'- accent {p["accent"]}: {why.get("accent", psrc)}', f'- accent2 {p["accent2"]}: {why.get("accent2", "second voice; " + psrc)}',
          f'- muted {p["muted"]}: mixed from ink and ground for labels and sources, 5:1 against the darkest rendered ground', '']
    arc = g.get('arc') or [f'{s} {p.get("ground2") if i % 2 else p["ground"]}' for i, s in enumerate(['S1-S2', 'S3'])]
    L += ['## Colour arc', '- ' + ' → '.join(arc), '']
    mat = g.get('material') or {}
    motifs = g.get('motifs') or [f'{mat.get("kind", "flat")} ground (grain {mat.get("grain", 0.03)})', g.get('image', 'photographs as found')]
    L += ['## Motifs and textures'] + [f'- {m}' for m in motifs] + ['']
    L += ['## Layered objects (Morph)'] + [f'- {m}' for m in (g.get('layers') or [g.get('signature', 'the signature object')])] + ['']
    L += ['## Signature', f'- {g.get("signature", "")}', '']
    mo = g.get('motion') or {}
    L += ['## Motion vocabulary', f'- grammar: {why.get("motion", "")}', f'- tempo {mo.get("tempo_ms", 1200)} ms, stagger {mo.get("stagger_ms", 120)} ms; '
          f'transitions {", ".join(mo.get("transitions", []))}']
    L += [f'- {v}: {VERB_TECH.get(v, v)}' for v in mo.get('verbs', [])] + ['']
    L += ['## Type and grid', f'- type: {why.get("type", "")}', f'- grid: {why.get("grid", "")}',
          f'- composition: {why.get("composition", "")}', '']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('compile')
    s.add_argument('genome')
    s.add_argument('--out')
    s.add_argument('--root')
    s = sub.add_parser('distance')
    s.add_argument('a')
    s.add_argument('b')
    s.add_argument('--renders-a')
    s.add_argument('--renders-b')
    s.add_argument('--json')
    sub.add_parser('axes')
    a = ap.parse_args(argv)
    if a.cmd == 'axes':
        for k, v in AXES.items():
            print(f'{k:12} {v}')
        return 0
    if a.cmd == 'compile':
        gp = Path(a.genome)
        g = json.loads(gp.read_text(encoding='utf-8'))
        root = Path(a.root) if a.root else (gp.parent.parent if gp.parent.name == 'design' else gp.parent)
        st = compile_genome(g, root)
        out = Path(a.out) if a.out else gp.with_name('style.json')
        out.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')
        ad = root / 'design/art-direction.md'
        if not ad.is_file() or '<!-- genome -->' in ad.read_text(encoding='utf-8') or 'TODO' in ad.read_text(encoding='utf-8'):
            ad.parent.mkdir(parents=True, exist_ok=True)
            ad.write_text(art_direction_md(g, st, root), encoding='utf-8')
            print('wrote', ad)
        p = st['palette']
        print(f'{out}: ground {p["ground"]} ink {p["ink"]} ({contrast(p["ink"], p["ground"]):.1f}:1) accent {p["accent"]} '
              f'({contrast(p["accent"], p["ground"]):.1f}:1) muted {contrast(p["muted"], p["ground"]):.1f}:1; '
              f'sizes {sorted({r["size"] for r in st["type"].values()})}; fonts {list(dict.fromkeys(st["fonts"].values()))}')
        return 0
    fa = deck_fingerprint(a.a, a.renders_a)
    fb = deck_fingerprint(a.b, a.renders_b)
    d = deck_distance(fa, fb)
    for k, v in d.items():
        print(f'{k:22} {v:.3f}')
    if a.json:
        Path(a.json).write_text(json.dumps({'a': a.a, 'b': a.b, 'distance': d, 'fingerprints': {'a': fa, 'b': fb}}, indent=1), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
