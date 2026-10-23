"""No-Morph safe mode (v5.1): make a motion deck read correctly where Morph does not play.

Morph (p159) plays only in PowerPoint 365 / 2019+ (Windows, Mac, web). PowerPoint 2016 and older,
Google Slides, Keynote and LibreOffice take the mc:Fallback branch, which v5 wrote as a plain fade:
shared !! shapes then jump from their old place to the new one instead of travelling.

deck.json "compat" (written to motion.json, read by motion.py and check_deck.py --compat):
  "morph"  Morph as authored, fade fallback (opt-in; Morph needs PowerPoint 365/2019+).
  "safe"   DEFAULT since v6.18: no Morph anywhere. Every Morph slide gets a classic transition (fade unless
           "safe_transition" names another core one) and the Morph is rebuilt as classic effects:
             shared !! shape that moved   -> appear (zoom when also resized) + motion path from its old place
             shared !! shape resized only -> zoom entrance
             shared text that changed     -> type (byChar) / word (byWord) / fade entrance
             new !! shape                 -> fade entrance
           These are PowerPoint 2010+ effects; Keynote and LibreOffice play them, Google Slides keeps
           fade/fly/zoom and drops motion paths (the shape then just appears at its end place).
  "dual"   keep Morph for PowerPoint 365, but the mc:Fallback carries a directional classic transition
           (push/wipe picked from the main move) and new !! shapes get a fade entrance, which Morph
           tolerates (they fade in after the Morph instead of during it). Moved shapes stay
           un-animated so Morph still pairs them.
Shapes that already carry an authored effect are left alone.
"""
import copy

from lxml import etree

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
P, A, MC = ('{%s}' % NS[k] for k in ('p', 'a', 'mc'))
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'
EMU = 914400
SLIDE_W, SLIDE_H = 13.333, 7.5
MODES = ('morph', 'safe', 'dual')
MOVE_MIN = 0.03      # fraction of slide width a shared shape must move to count as Morph motion
SIZE_MIN = 0.10      # relative size change that counts as a resize


def check_mode(mode):
    mode = mode or 'safe'
    if mode not in MODES:
        raise ValueError(f'compat must be one of {MODES}, got {mode!r}')
    return mode


def _xfrm(el):
    tag = etree.QName(el).localname
    if tag == 'graphicFrame':
        x = el.find('p:xfrm', NS)
    elif tag == 'grpSp':
        x = el.find('p:grpSpPr/a:xfrm', NS)
    else:
        x = el.find('p:spPr/a:xfrm', NS)
    if x is None:
        return None
    off, ext = x.find('a:off', NS), x.find('a:ext', NS)
    if off is None or ext is None:
        return None
    return tuple(int(v) / EMU for v in (off.get('x'), off.get('y'), ext.get('cx'), ext.get('cy')))


def shapes(root):
    """Top-level shapes of a slide: name -> dict(id, box (x, y, w, h) inches, text, kind)."""
    tree = root.find('p:cSld/p:spTree', NS)
    out = {}
    if tree is None:
        return out
    for el in tree:
        tag = etree.QName(el).localname if isinstance(el.tag, str) else ''
        if tag not in ('sp', 'pic', 'grpSp', 'cxnSp', 'graphicFrame'):
            continue
        c = el.find('.//p:cNvPr', NS)
        if c is None:
            continue
        txt = ''.join(t.text or '' for t in el.iter(A + 't')).strip()
        out.setdefault(c.get('name') or '', {'id': c.get('id'), 'box': _xfrm(el), 'text': txt, 'kind': tag})
    return out


def has_morph(root):
    return any(etree.QName(e).namespace == P159 for e in root.iter() if isinstance(e.tag, str))


def strip_morph(root):
    """Replace every Morph carrier by the transition a non-Morph player uses (its mc:Fallback). Returns count."""
    n = 0
    for ac in list(root.iter(MC + 'AlternateContent')):
        if not any(etree.QName(e).namespace == P159 for e in ac.iter() if isinstance(e.tag, str)):
            continue
        fb = ac.find('mc:Fallback/p:transition', NS)
        parent = ac.getparent()
        if fb is not None:
            parent.replace(ac, copy.deepcopy(fb))
        else:
            parent.remove(ac)
        n += 1
    return n


def _move(prev, cur):
    """(dx, dy, scale): inches from this centre back to the previous one, and old/new size; None if a box is missing."""
    if not prev.get('box') or not cur.get('box'):
        return None
    px, py, pw, ph = prev['box']
    cx, cy, cw, ch = cur['box']
    dx = (px + pw / 2) - (cx + cw / 2)
    dy = (py + ph / 2) - (cy + ch / 2)
    s = ((pw * ph) / (cw * ch)) ** 0.5 if cw * ch > 0 and pw * ph > 0 else 1.0
    return dx, dy, s


def moved(m):
    return m is not None and (abs(m[0]) >= MOVE_MIN * SLIDE_W or abs(m[1]) >= MOVE_MIN * SLIDE_W)


def resized(m):
    return m is not None and abs(m[2] - 1) >= SIZE_MIN


def main_direction(prev, cur):
    """'l'|'r'|'t'|'b' when every moved shared shape travels the same way, else None."""
    dirs = set()
    for nm, c in cur.items():
        if nm.startswith('!!') and nm in prev:
            m = _move(prev[nm], c)
            if moved(m):
                dx, dy = -m[0], -m[1]           # travel = new - old
                dirs.add(('r' if dx > 0 else 'l') if abs(dx) >= abs(dy) else ('b' if dy > 0 else 't'))
    return dirs.pop() if len(dirs) == 1 else None


def plan(prev, cur, mode, ms=1300, option='byObject', taken=(), safe_transition=None):
    """Classic replacement for one Morph slide.

    prev, cur: shapes() of the previous and this slide. Returns (transition spec or None, effects list).
    safe: the spec replaces the Morph. dual: the spec is the Morph with a classic 'fallback'.
    """
    mode = check_mode(mode)
    if mode == 'morph':
        return None, []
    taken = set(taken)
    effects = []
    ms_move = max(500, min(int(ms), 1600))
    for nm, c in cur.items():
        if not nm.startswith('!!') or nm in taken:
            continue
        if nm not in prev:
            effects.append({'shape': nm, 'fx': 'fade', 'ms': 600, 'delay': 150, '_why': 'new'})
            continue
        if mode == 'dual':
            continue
        m = _move(prev[nm], c)
        changed_text = c['text'] and c['text'] != prev[nm]['text']
        if moved(m):
            first = 'zoom' if resized(m) else 'appear'
            effects.append({'shape': nm, 'fx': first, 'ms': ms_move, 'delay': 0, '_why': 'moved'})
            effects.append({'shape': nm, 'fx': 'path', 'path': [[round(m[0], 3), round(m[1], 3)], [0, 0]], 'from_offset': True,
                            'ms': ms_move, 'delay': 0, 'ease': [30, 60], '_why': 'moved'})
        elif resized(m):
            effects.append({'shape': nm, 'fx': 'zoom', 'ms': ms_move, 'delay': 0, '_why': 'resized'})
        elif changed_text:
            fx = {'byChar': 'type', 'byWord': 'word'}.get(option, 'fade')
            effects.append({'shape': nm, 'fx': fx, 'ms': 600, 'delay': 100, '_why': 'text'})
    if mode == 'safe':
        t = safe_transition or {'type': 'fade'}
        t = dict({'type': t} if isinstance(t, str) else t)
        t.setdefault('ms', min(int(ms), 800))
        import motionlib
        if motionlib.TRANSITIONS.get(t.get('type'), ('?',))[0] != 'p':
            core = sorted(k for k, v in motionlib.TRANSITIONS.items() if v[0] == 'p')
            raise ValueError(f'safe_transition must be a core (PowerPoint 2007+) transition: {core}')
        return t, effects
    d = main_direction(prev, cur)
    if d in ('l', 'r'):
        fb = {'type': 'push', 'dir': d}
    elif d:
        fb = {'type': 'wipe', 'dir': d}
    else:
        fb = {'type': 'fade'}
    return {'type': 'morph', 'ms': int(ms), 'option': option, 'fallback': fb}, effects


def _overlap(a, b):
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    return ix * iy / max(1e-6, min(a[2] * a[3], b[2] * b[3]))


def _animated_ids(root):
    """spid -> set of preset classes on the slide (entr/emph/exit/path)."""
    out = {}
    for ctn in root.iter(P + 'cTn'):
        cls = ctn.get('presetClass')
        if not cls:
            continue
        for t in ctn.iter(P + 'spTgt'):
            out.setdefault(t.get('spid'), set()).add(cls)
    return out


def audit(roots, mode, morph_slides=None):
    """No-Morph audit over the slides in show order. roots: list of (tag, slide root).
    morph_slides: indexes (0-based, show order) authored as Morph (from motion.json); None = every slide whose
    transition is Morph or fade (a deliberate push/curtains/... cut is allowed to jump). Returns (errors, warns, infos) for the deck as it plays where Morph is not available."""
    mode = check_mode(mode)
    errors, warns, infos = [], [], []
    prev = {}
    lost = 0
    for idx, (tag, root) in enumerate(roots):
        cur = shapes(root)
        if mode == 'safe' and has_morph(root):
            errors.append(f'{tag}: compat=safe but the slide still carries a Morph transition')
        if morph_slides is None:
            import motionlib
            authored_morph = motionlib.describe_transition(root)[0] in ('morph', 'fade')
        else:
            authored_morph = idx in morph_slides
        anim = _animated_ids(root)
        exits = {s for s, c in anim.items() if c == {'exit'}}
        for nm, c in cur.items():
            if authored_morph and nm.startswith('!!') and nm in prev:
                m = _move(prev[nm], c)
                if moved(m) and not ({'entr', 'path'} & anim.get(c['id'], set())):
                    lost += 1
                    msg = f'{tag}: {nm} moves ({m[0]:+.1f}, {m[1]:+.1f}) in with no classic motion: it jumps without Morph'
                    if mode == 'safe':
                        errors.append(msg)
                    elif mode == 'dual':
                        infos.append(msg)
        texts = [(nm, c) for nm, c in cur.items() if c['text'] and c['box'] and c['id'] not in exits
                 and c['box'][0] < SLIDE_W and c['box'][1] < SLIDE_H and c['box'][0] + c['box'][2] > 0 and c['box'][1] + c['box'][3] > 0]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if _overlap(texts[i][1]['box'], texts[j][1]['box']) > 0.5:
                    warns.append(f'{tag}: end state, text {texts[i][0]!r} and {texts[j][0]!r} overlap (look at the no-Morph render)')
        prev = cur
    infos.append(f'no-Morph: compat={mode}, {lost} shared-shape move(s) without a classic replacement')
    return errors, warns, infos


def compare_renders(intended_dir, nomorph_dir, tol=6.0):
    """Mean absolute pixel difference per slide between two render.sh folders. Returns (errors, infos)."""
    from pathlib import Path
    from PIL import Image, ImageChops, ImageStat
    a = sorted(Path(intended_dir).glob('slide-*.jpg'))
    b = sorted(Path(nomorph_dir).glob('slide-*.jpg'))
    errors, infos = [], []
    if len(a) != len(b):
        errors.append(f'no-Morph render has {len(b)} slides, intended render {len(a)}')
    worst = 0.0
    for x, y in zip(a, b):
        ia, ib = Image.open(x).convert('L'), Image.open(y).convert('L')
        if ia.size != ib.size:
            ib = ib.resize(ia.size)
        d = ImageStat.Stat(ImageChops.difference(ia, ib)).mean[0]
        worst = max(worst, d)
        if d > tol:
            errors.append(f'{y.name}: no-Morph end state differs from the intended render (mean diff {d:.1f} > {tol})')
        if ImageStat.Stat(ib).stddev[0] < 2:
            errors.append(f'{y.name}: no-Morph render is blank')
    infos.append(f'no-Morph render: {len(b)} slides compared, worst mean diff {worst:.2f}')
    return errors, infos
