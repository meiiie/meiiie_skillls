"""Native PowerPoint motion beyond Morph: slide transitions and animation timing XML (v5).

Used by motion.py; importable on its own. Everything here writes plain OOXML that python-pptx
does not author (p:transition children, p:timing trees), so the result stays fully editable in
PowerPoint: every effect shows up in the Animation Pane with its preset name.

TRANSITIONS  name -> how it is written. 'morph' is p159 (Office 2015+, fade fallback); p14/p15 names
             need PowerPoint 2010/2013+ (fade fallback for older readers); the rest are ECMA-376 core.
EFFECTS      entrance / emphasis / exit / path / media, each a function that returns one <p:par>.

An effect is a dict:
  {"shape": "!!dot" | "@fade1-x" (name on the slide), "fx": "fly", "dir": "l|r|t|b|in|out|h|v",
   "delay": 0 (ms from the start of its click group), "ms": 600, "click": 0 (0 = plays automatically
   after the slide arrives; 1, 2 ... = the Nth click), "by": "letter|word" (text, per-unit stagger
   "step": 8 = % of ms), "loop": true (repeat forever), "reverse": true (auto-reverse),
   "path": [[dx, dy], ...] in inches relative to the shape or "C" curves (see path_d),
   "scale": 1.12, "deg": 360, "trigger": "<name of the shape that is clicked>",
   "ease": [accel %, decel %]}
"""
import math
import re
from collections import Counter

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
P15 = 'http://schemas.microsoft.com/office/powerpoint/2012/main'
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
SLIDE_W_IN, SLIDE_H_IN = 13.333, 7.5

# ------------------------------------------------------------------ transitions
# kind: 'p' core, 'p14' Office 2010, 'p15' Office 2013 preset, 'morph'
DIRS4 = {'l': 'l', 'r': 'r', 'u': 'u', 'd': 'd', 't': 'u', 'b': 'd', None: None}
TRANSITIONS = {
    'none': ('p', None, {}),
    'fade': ('p', 'fade', {}),
    'cut': ('p', 'cut', {}),
    'push': ('p', 'push', {'dir': 'u'}),
    'wipe': ('p', 'wipe', {'dir': 'r'}),
    'split': ('p', 'split', {'orient': 'vert', 'dir': 'out'}),
    'cover': ('p', 'cover', {'dir': 'l'}),
    'uncover': ('p', 'pull', {'dir': 'l'}),
    'shape': ('p', 'circle', {}),
    'diamond': ('p', 'diamond', {}),
    'zoombox': ('p', 'zoom', {}),
    'dissolve': ('p', 'dissolve', {}),
    'blinds': ('p', 'blinds', {'dir': 'vert'}),
    'checker': ('p', 'checker', {}),
    'randombars': ('p', 'randomBar', {'dir': 'vert'}),
    'clock': ('p', 'wheel', {'spokes': '1'}),
    'comb': ('p', 'comb', {}),
    'reveal': ('p14', 'reveal', {'dir': 'r'}),
    'flash': ('p14', 'flash', {}),
    'ripple': ('p14', 'ripple', {}),
    'honeycomb': ('p14', 'honeycomb', {}),
    'glitter': ('p14', 'glitter', {'pattern': 'hexagon', 'dir': 'l'}),
    'vortex': ('p14', 'vortex', {'dir': 'r'}),
    'shred': ('p14', 'shred', {'pattern': 'strip', 'dir': 'in'}),
    'switch': ('p14', 'switch', {'dir': 'r'}),
    'flip': ('p14', 'flip', {'dir': 'r'}),
    'gallery': ('p14', 'gallery', {'dir': 'l'}),
    'cube': ('p14', 'prism', {'dir': 'r'}),
    'doors': ('p14', 'doors', {'dir': 'vert'}),
    'window': ('p14', 'window', {'dir': 'vert'}),
    'zoom': ('p14', 'warp', {'dir': 'in'}),
    'pan': ('p14', 'pan', {'dir': 'u'}),
    'ferris': ('p14', 'ferris', {'dir': 'l'}),
    'conveyor': ('p14', 'conveyor', {'dir': 'l'}),
    'rotate': ('p14', 'prism', {'dir': 'r', 'isContent': '1'}),
    'orbit': ('p14', 'prism', {'dir': 'r', 'isContent': '1', 'isInverted': '1'}),
    'flythrough': ('p14', 'flythrough', {'dir': 'in'}),
    'fallover': ('p15', 'fallOver', {}),
    'drape': ('p15', 'drape', {}),
    'curtains': ('p15', 'curtains', {}),
    'wind': ('p15', 'wind', {}),
    'prestige': ('p15', 'prestige', {}),
    'fracture': ('p15', 'fracture', {}),
    'crush': ('p15', 'crush', {}),
    'peeloff': ('p15', 'peelOff', {}),
    'pagecurl': ('p15', 'pageCurlDouble', {}),
    'airplane': ('p15', 'airplane', {}),
    'origami': ('p15', 'origami', {}),
    'morph': ('morph', 'morph', {}),
}
# attributes PowerPoint accepts per element (others are dropped so the XML stays schema-valid)
_ALLOWED = {'push': {'dir'}, 'wipe': {'dir'}, 'cover': {'dir'}, 'pull': {'dir'}, 'split': {'orient', 'dir'},
            'blinds': {'dir'}, 'checker': {'dir'}, 'randomBar': {'dir'}, 'comb': {'dir'}, 'wheel': {'spokes'},
            'zoom': {'dir'}, 'reveal': {'dir', 'thruBlk'}, 'glitter': {'pattern', 'dir'}, 'vortex': {'dir'},
            'shred': {'pattern', 'dir'}, 'switch': {'dir'}, 'flip': {'dir'}, 'gallery': {'dir'}, 'prism': {'dir', 'isContent', 'isInverted'},
            'doors': {'dir'}, 'window': {'dir'}, 'warp': {'dir'}, 'pan': {'dir'}, 'ferris': {'dir'}, 'conveyor': {'dir'},
            'flythrough': {'dir', 'hasBounce'}, 'ripple': {'dir'}}
_DIR_VALUES = {  # what "dir" may be for each element
    'push': {'l', 'r', 'u', 'd'}, 'wipe': {'l', 'r', 'u', 'd'}, 'cover': {'l', 'r', 'u', 'd', 'lu', 'ru', 'ld', 'rd'},
    'pull': {'l', 'r', 'u', 'd', 'lu', 'ru', 'ld', 'rd'}, 'split': {'in', 'out'}, 'blinds': {'horz', 'vert'},
    'checker': {'horz', 'vert'}, 'randomBar': {'horz', 'vert'}, 'comb': {'horz', 'vert'}, 'zoom': {'in', 'out'},
    'reveal': {'l', 'r'}, 'glitter': {'l', 'r', 'u', 'd'}, 'vortex': {'l', 'r', 'u', 'd'}, 'shred': {'in', 'out'},
    'switch': {'l', 'r'}, 'flip': {'l', 'r'}, 'gallery': {'l', 'r'}, 'prism': {'l', 'r', 'u', 'd'},
    'doors': {'horz', 'vert'}, 'window': {'horz', 'vert'}, 'warp': {'in', 'out'}, 'pan': {'l', 'r', 'u', 'd'},
    'ferris': {'l', 'r'}, 'conveyor': {'l', 'r'}, 'flythrough': {'in', 'out'}, 'ripple': {'center', 'lu', 'ru', 'ld', 'rd'},
}


def transition_names():
    return sorted(TRANSITIONS)


def transition_xml(spec, default_ms=1300):
    """One transition carrier (an mc:AlternateContent or a plain p:transition) as a string.

    spec: "fade" | {"type": "push", "dir": "l", "ms": 700, "option": "byChar" (morph), "invX": true (p15),
                    "orient": "horz" (split), "advance_ms": 4000 (auto advance), "click": true}
    """
    if isinstance(spec, str):
        spec = {'type': spec}
    kind = spec.get('type', 'morph')
    if kind not in TRANSITIONS:
        raise ValueError(f'unknown transition {kind!r}; known: {", ".join(transition_names())}')
    ns, el, defaults = TRANSITIONS[kind]
    ms = int(spec.get('ms', default_ms))
    adv = ''
    if spec.get('advance_ms'):
        adv = f' advTm="{int(spec["advance_ms"])}"' + ('' if spec.get('click', True) else ' advClick="0"')
    spd = 'fast' if ms <= 600 else ('med' if ms <= 1000 else 'slow')
    attrs = dict(defaults)
    for k in ('dir', 'orient', 'pattern', 'isContent', 'isInverted', 'thruBlk', 'hasBounce'):
        if k in spec:
            v = spec[k]
            attrs[k] = DIRS4.get(v, v) if (k == 'dir' and el in ('push', 'wipe', 'pan', 'vortex', 'prism', 'glitter')) else v
    if el in _ALLOWED:
        attrs = {k: str(v) for k, v in attrs.items() if k in _ALLOWED[el]}
        if 'dir' in attrs and el in _DIR_VALUES and attrs['dir'] not in _DIR_VALUES[el]:
            raise ValueError(f'transition {kind}: dir={attrs["dir"]!r} not one of {sorted(_DIR_VALUES[el])}')
    else:
        attrs = {}
    a = ''.join(f' {k}="{v}"' for k, v in attrs.items())
    p = f'xmlns:p="{P_NS}"'
    if ns == 'p' and el is None:
        return f'<p:transition {p} spd="{spd}"{adv}/>'
    if ns == 'morph':
        opt = spec.get('option', 'byObject')
        if opt not in ('byObject', 'byWord', 'byChar'):
            raise ValueError('morph option must be byObject, byWord or byChar')
        fallback = f'<p:transition {p} spd="slow"{adv}><p:fade/></p:transition>'
        if spec.get('fallback'):   # compat 'dual': a classic transition for players without Morph
            fb = spec['fallback'] if isinstance(spec['fallback'], dict) else {'type': spec['fallback']}
            fb = dict(fb, ms=fb.get('ms', min(ms, 900)))
            if fb.get('advance_ms') is None and spec.get('advance_ms'):
                fb['advance_ms'], fb['click'] = spec['advance_ms'], spec.get('click', True)
            if TRANSITIONS.get(fb.get('type'), ('?',))[0] != 'p' or fb['type'] == 'morph':
                raise ValueError(f'morph fallback must be a core transition (fade, push, wipe ...), got {fb.get("type")!r}')
            fx = transition_xml(fb, default_ms)
            fallback = fx[fx.index('<mc:Fallback>') + 13:fx.index('</mc:Fallback>')] if '<mc:Fallback>' in fx else fx
        return (f'<mc:AlternateContent xmlns:mc="{MC}"><mc:Choice xmlns:p159="{P159}" Requires="p159">'
                f'<p:transition {p} xmlns:p14="{P14}" spd="slow" p14:dur="{ms}"{adv}><p159:morph option="{opt}"/></p:transition></mc:Choice>'
                f'<mc:Fallback>{fallback}</mc:Fallback></mc:AlternateContent>')
    if ns == 'p':
        inner = f'<p:{el}{a}/>'
        return (f'<mc:AlternateContent xmlns:mc="{MC}"><mc:Choice xmlns:p14="{P14}" Requires="p14">'
                f'<p:transition {p} spd="{spd}" p14:dur="{ms}"{adv}>{inner}</p:transition></mc:Choice>'
                f'<mc:Fallback><p:transition {p} spd="{spd}"{adv}>{inner}</p:transition></mc:Fallback></mc:AlternateContent>')
    if ns == 'p14':
        inner = f'<p14:{el}{a}/>'
        return (f'<mc:AlternateContent xmlns:mc="{MC}"><mc:Choice xmlns:p14="{P14}" Requires="p14">'
                f'<p:transition {p} spd="{spd}" p14:dur="{ms}"{adv}>{inner}</p:transition></mc:Choice>'
                f'<mc:Fallback><p:transition {p} spd="{spd}"{adv}><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    # p15 preset transition
    inv = ''
    if spec.get('invX'):
        inv += ' invX="1"'
    if spec.get('invY'):
        inv += ' invY="1"'
    prst = el
    if kind == 'pagecurl' and spec.get('pages') == 'single':
        prst = 'pageCurlSingle'
    return (f'<mc:AlternateContent xmlns:mc="{MC}"><mc:Choice xmlns:p15="{P15}" Requires="p15">'
            f'<p:transition {p} xmlns:p14="{P14}" spd="slow" p14:dur="{ms}"{adv}><p15:prstTrans prst="{prst}"{inv}/></p:transition></mc:Choice>'
            f'<mc:Fallback><p:transition {p} spd="slow"{adv}><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')


# ------------------------------------------------------------------ effects
class Ids:
    def __init__(self, start=3):
        self.n = start - 1

    def __call__(self):
        self.n += 1
        return str(self.n)


def _tgt(spid):
    return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'


def _set_vis(ids, spid, val='visible', delay=0):
    return (f'<p:set><p:cBhvr><p:cTn id="{ids()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst></p:cTn>'
            f'{_tgt(spid)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="{val}"/></p:to></p:set>')


def _anim(ids, spid, attr, a, b, ms, additive=True):
    def val(v):
        return f'<p:fltVal val="{v}"/>' if isinstance(v, (int, float)) else f'<p:strVal val="{v}"/>'
    add = ' additive="base"' if additive else ''
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr{add}><p:cTn id="{ids()}" dur="{ms}" fill="hold"/>{_tgt(spid)}'
            f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
            f'<p:tav tm="0"><p:val>{val(a)}</p:val></p:tav><p:tav tm="100000"><p:val>{val(b)}</p:val></p:tav></p:tavLst></p:anim>')


def _filter(ids, spid, filt, ms, transition='in'):
    return (f'<p:animEffect transition="{transition}" filter="{filt}"><p:cBhvr><p:cTn id="{ids()}" dur="{ms}"/>{_tgt(spid)}</p:cBhvr></p:animEffect>')


FLY_SUB = {'t': 1, 'r': 2, 'b': 4, 'l': 8}
FLY_FROM = {'t': ('#ppt_x', '0-#ppt_h/2'), 'b': ('#ppt_x', '1+#ppt_h/2'), 'l': ('0-#ppt_w/2', '#ppt_y'), 'r': ('1+#ppt_w/2', '#ppt_y')}
DIR_ALIAS = {'u': 'b', 'up': 'b', 'd': 't', 'down': 't', 'left': 'l', 'right': 'r'}
WIPE = {'l': (8, 'wipe(left)'), 'r': (2, 'wipe(right)'), 't': (1, 'wipe(up)'), 'b': (4, 'wipe(down)')}
SPLIT = {'v': (21, 'barn(outVertical)'), 'h': (26, 'barn(outHorizontal)'), 'vin': (37, 'barn(inVertical)'), 'hin': (42, 'barn(inHorizontal)')}

# fx -> (presetClass, presetID); used for the Animation Pane name and by check_deck.py
PRESETS = {
    'appear': ('entr', 1), 'fade': ('entr', 10), 'fly': ('entr', 2), 'float': ('entr', 42), 'rise': ('entr', 42),
    'wipe': ('entr', 22), 'split': ('entr', 16), 'zoom': ('entr', 53), 'wheel': ('entr', 21), 'type': ('entr', 10),
    'word': ('entr', 10), 'drop': ('entr', 2),
    'pulse': ('emph', 6), 'grow': ('emph', 6), 'spin': ('emph', 8), 'blink': ('emph', 35), 'teeter': ('emph', 32),
    'fadeout': ('exit', 10), 'flyout': ('exit', 2), 'zoomout': ('exit', 53), 'wipeout': ('exit', 22),
    'path': ('path', 0), 'orbit': ('path', 0), 'video': ('mediacall', 1),
}
ENTRANCES = {k for k, v in PRESETS.items() if v[0] == 'entr'}


def path_d(points, closed=False):
    """Motion-path string in slide fractions from [[dx, dy] ...] inch offsets (first point is the shape's
    own position, so a path normally starts at [0, 0]). A point [dx, dy, 'C', c1x, c1y, c2x, c2y] draws a
    cubic curve whose control points are also inch offsets."""
    fx = lambda v: f'{v / SLIDE_W_IN:.4f}'.rstrip('0').rstrip('.') if v else '0'  # noqa: E731
    fy = lambda v: f'{v / SLIDE_H_IN:.4f}'.rstrip('0').rstrip('.') if v else '0'  # noqa: E731
    out, types = [], []
    for i, pt in enumerate(points):
        if i == 0:
            out.append(f'M {fx(pt[0])} {fy(pt[1])}')
            types.append('A')
        elif len(pt) >= 7 and pt[2] == 'C':
            out.append(f'C {fx(pt[3])} {fy(pt[4])} {fx(pt[5])} {fy(pt[6])} {fx(pt[0])} {fy(pt[1])}')
            types.append('F')
        else:
            out.append(f'L {fx(pt[0])} {fy(pt[1])}')
            types.append('A')
    return ' '.join(out) + (' Z' if closed else ' E'), ''.join(types)


def orbit_points(rx, ry, start_deg=0, turns=1.0, n=8):
    """Closed elliptical path through cubic segments (offsets in inches, starting at the shape)."""
    pts = []
    k = 4 / 3 * math.tan(math.pi / (2 * n))
    a0 = math.radians(start_deg)
    cx, cy = -rx * math.cos(a0), -ry * math.sin(a0)
    seg = int(round(n * turns))
    for i in range(seg + 1):
        a = a0 + 2 * math.pi * i / n
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        if i == 0:
            pts.append([x, y])
            continue
        ap = a0 + 2 * math.pi * (i - 1) / n
        c1 = (cx + rx * (math.cos(ap) - k * math.sin(ap)), cy + ry * (math.sin(ap) + k * math.cos(ap)))
        c2 = (cx + rx * (math.cos(a) + k * math.sin(a)), cy + ry * (math.sin(a) - k * math.cos(a)))
        pts.append([x, y, 'C', c1[0], c1[1], c2[0], c2[1]])
    return pts


def effect_par(e, spid, delay, ids, node='withEffect', is_text=False, grp=0):
    """One <p:par> for effect dict e on shape spid, starting `delay` ms into its group."""
    fx = e.get('fx', 'fade')
    if fx not in PRESETS:
        raise ValueError(f'unknown effect {fx!r}; known: {", ".join(sorted(PRESETS))}')
    cls, pid = PRESETS[fx]
    ms = int(e.get('ms', {'blink': 1000, 'spin': 2000, 'path': 1600, 'orbit': 6000, 'pulse': 900, 'grow': 900}.get(fx, 700)))
    d = e.get('dir')
    d = DIR_ALIAS.get(d, d)   # 'u'/'d' as in transitions: the motion goes up = it comes from the bottom
    sub = 0
    kids = []
    if fx == 'appear':
        kids.append(_set_vis(ids, spid))
    elif fx in ('fade', 'type', 'word'):
        kids += [_set_vis(ids, spid), _filter(ids, spid, 'fade', ms)]
    elif fx in ('fly', 'drop'):
        d = d or ('t' if fx == 'drop' else 'b')
        sub = FLY_SUB[d]
        x0, y0 = FLY_FROM[d]
        kids += [_set_vis(ids, spid), _anim(ids, spid, 'ppt_x', x0, '#ppt_x', ms), _anim(ids, spid, 'ppt_y', y0, '#ppt_y', ms)]
    elif fx in ('float', 'rise'):
        dy = '#ppt_y+.06' if (d or 'b') == 'b' else '#ppt_y-.06'
        sub = 0
        kids += [_set_vis(ids, spid), _filter(ids, spid, 'fade', ms), _anim(ids, spid, 'ppt_x', '#ppt_x', '#ppt_x', ms),
                 _anim(ids, spid, 'ppt_y', dy, '#ppt_y', ms)]
    elif fx == 'wipe':
        sub, filt = WIPE[d or 'l']
        kids += [_set_vis(ids, spid), _filter(ids, spid, filt, ms)]
    elif fx == 'split':
        sub, filt = SPLIT[d or 'v']
        kids += [_set_vis(ids, spid), _filter(ids, spid, filt, ms)]
    elif fx == 'wheel':
        sub = 1
        kids += [_set_vis(ids, spid), _filter(ids, spid, 'wheel(1)', ms)]
    elif fx == 'zoom':
        sub = 16
        kids += [_set_vis(ids, spid), _anim(ids, spid, 'ppt_w', 0, '#ppt_w', ms, False), _anim(ids, spid, 'ppt_h', 0, '#ppt_h', ms, False),
                 _filter(ids, spid, 'fade', ms)]
    elif fx in ('pulse', 'grow'):
        s = float(e.get('scale', 1.08 if fx == 'pulse' else 1.25))
        v = int(round(s * 100000))
        rev = ' autoRev="1"' if (fx == 'pulse' or e.get('reverse')) else ''
        kids.append(f'<p:animScale><p:cBhvr><p:cTn id="{ids()}" dur="{ms}"{rev} fill="hold"/>{_tgt(spid)}</p:cBhvr><p:by x="{v}" y="{v}"/></p:animScale>')
    elif fx == 'spin':
        deg = float(e.get('deg', 360))
        kids.append(f'<p:animRot by="{int(deg * 60000)}"><p:cBhvr><p:cTn id="{ids()}" dur="{ms}" fill="hold"/>{_tgt(spid)}'
                    '<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
    elif fx == 'teeter':
        q = ms // 4
        for i, deg in enumerate((4, -8, 8, -4)):
            kids.append(f'<p:animRot by="{deg * 60000}"><p:cBhvr><p:cTn id="{ids()}" dur="{q}" fill="hold"><p:stCondLst><p:cond delay="{i * q}"/></p:stCondLst></p:cTn>{_tgt(spid)}'
                        '<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
    elif fx == 'blink':
        kids.append(f'<p:anim calcmode="discrete" valueType="str"><p:cBhvr override="childStyle"><p:cTn id="{ids()}" dur="{ms}" fill="hold"/>{_tgt(spid)}'
                    '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                    '<p:tavLst><p:tav tm="0"><p:val><p:strVal val="hidden"/></p:val></p:tav><p:tav tm="50000"><p:val><p:strVal val="visible"/></p:val></p:tav></p:tavLst></p:anim>')
    elif fx == 'fadeout':
        kids += [_filter(ids, spid, 'fade', ms, 'out'), _set_vis(ids, spid, 'hidden', ms - 1)]
    elif fx == 'wipeout':
        sub, filt = WIPE[d or 'l']
        kids += [_filter(ids, spid, filt, ms, 'out'), _set_vis(ids, spid, 'hidden', ms - 1)]
    elif fx == 'flyout':
        d = d or 'b'
        sub = FLY_SUB[d]
        x1, y1 = FLY_FROM[d]
        kids += [_anim(ids, spid, 'ppt_x', '#ppt_x', x1, ms), _anim(ids, spid, 'ppt_y', '#ppt_y', y1, ms), _set_vis(ids, spid, 'hidden', ms - 1)]
    elif fx == 'zoomout':
        sub = 16
        kids += [_anim(ids, spid, 'ppt_w', '#ppt_w', 0, ms, False), _anim(ids, spid, 'ppt_h', '#ppt_h', 0, ms, False),
                 _filter(ids, spid, 'fade', ms, 'out'), _set_vis(ids, spid, 'hidden', ms - 1)]
    elif fx in ('path', 'orbit'):
        if fx == 'orbit':
            pts = orbit_points(float(e.get('rx', 0.6)), float(e.get('ry', e.get('rx', 0.6))), float(e.get('start', 0)), float(e.get('turns', 1)))
        else:
            pts = e.get('path') or [[0, 0], [1, 0]]
            if pts[0][:2] != [0, 0] and not e.get('from_offset'):
                pts = [[0, 0]] + pts   # from_offset: the path starts away from the shape (no-Morph rebuild)
        dpath, types = path_d(pts, closed=False)
        rot = ' rAng="0"'
        kids.append(f'<p:animMotion origin="layout" path="{dpath}" pathEditMode="relative"{rot} ptsTypes="{types}">'
                    f'<p:cBhvr><p:cTn id="{ids()}" dur="{ms}" fill="hold"/>{_tgt(spid)}'
                    '<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>')
    elif fx == 'video':
        kids.append(f'<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="{ids()}" dur="{int(e.get("media_ms", ms))}" fill="hold"/>{_tgt(spid)}</p:cBhvr></p:cmd>')
    head = ids()
    extra = ''
    if e.get('loop'):
        extra += ' repeatCount="indefinite"'
    ease = e.get('ease')
    if ease is None and cls in ('entr', 'path') and fx not in ('appear', 'type', 'word', 'blink'):
        ease = [0, 60] if cls == 'entr' else [40, 40]
    if ease and cls != 'mediacall':
        if ease[0]:
            extra += f' accel="{int(ease[0] * 1000)}"'
        if ease[1]:
            extra += f' decel="{int(ease[1] * 1000)}"'
    grp_attr = f' grpId="{grp}"' if cls != 'mediacall' else ''
    iterate = ''
    by = e.get('by') or ('letter' if fx == 'type' else ('word' if fx == 'word' else None))
    if by and is_text:
        step = float(e.get('step', 8 if by == 'letter' else 25))
        iterate = f'<p:iterate type="{"lt" if by == "letter" else "wd"}"><p:tmPct val="{int(step * 1000)}"/></p:iterate>'
    return (f'<p:par><p:cTn id="{head}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}"{extra} fill="hold"{grp_attr} nodeType="{node}">'
            f'<p:stCondLst><p:cond delay="{int(delay)}"/></p:stCondLst>{iterate}<p:childTnLst>{"".join(kids)}</p:childTnLst></p:cTn></p:par>')


def build_timing(effects, media=(), text_ids=()):
    """The whole <p:timing> for one slide.

    effects: list of (effect dict, spid). 'click' = 0 plays automatically after the transition;
             1, 2 ... wait for that click; 'trigger' = an interactive sequence on that shape's click
             (resolved to 'trigger_spid' by the caller).
    media:   list of dicts {spid, ms, loop, mute, autoplay} for embedded videos.
    """
    ids = Ids(3)
    text_ids = set(map(str, text_ids))
    main, inter = {}, {}
    for e, spid in effects:
        if e.get('trigger_spid'):
            inter.setdefault(str(e['trigger_spid']), []).append((e, spid))
        else:
            main.setdefault(int(e.get('click', 0)), []).append((e, spid))
    for m in media:
        if m.get('autoplay', True):
            main.setdefault(0, []).append(({'fx': 'video', 'media_ms': m.get('ms', 10000), 'delay': m.get('delay', 0)}, m['spid']))
    groups = []
    bld = []
    for k in sorted(main):
        items = sorted(main[k], key=lambda it: int(it[0].get('delay', 0)))
        pars = []
        for i, (e, spid) in enumerate(items):
            node = ('afterEffect' if k == 0 else 'clickEffect') if i == 0 else 'withEffect'
            cls = PRESETS.get(e.get('fx', 'fade'), ('entr', 10))[0]
            g = 0
            is_text = str(spid) in text_ids
            pars.append(effect_par(e, spid, e.get('delay', 0), ids, node, is_text, g))
            if is_text and cls in ('entr', 'exit', 'emph', 'path'):
                bld.append(str(spid))
        start = '<p:cond delay="indefinite"/>' + ('<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>' if k == 0 else '')
        groups.append(f'<p:par><p:cTn id="{ids()}" fill="hold"><p:stCondLst>{start}</p:stCondLst><p:childTnLst>'
                      f'<p:par><p:cTn id="{ids()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                      + ''.join(pars) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    seqs = ''
    if groups:
        seqs += ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                 + ''.join(groups) +
                 '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                 '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>')
    for trig, items in inter.items():
        pars = []
        for i, (e, spid) in enumerate(sorted(items, key=lambda it: int(it[0].get('delay', 0)))):
            is_text = str(spid) in text_ids
            pars.append(effect_par(e, spid, e.get('delay', 0), ids, 'clickEffect' if i == 0 else 'withEffect', is_text, 0))
        seqs += (f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="{ids()}" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
                 f'<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="{trig}"/></p:tgtEl></p:cond></p:stCondLst>'
                 '<p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync><p:childTnLst>'
                 f'<p:par><p:cTn id="{ids()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                 + ''.join(pars) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                 f'<p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="{trig}"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>')
    for m in media:
        rep = ' repeatCount="indefinite"' if m.get('loop', True) else ''
        mute = ' mute="1"' if m.get('mute', True) else ''
        seqs += (f'<p:video><p:cMediaNode vol="80000"{mute}><p:cTn id="{ids()}"{rep} fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
                 f'{_tgt(m["spid"])}</p:cMediaNode></p:video>')
    if not seqs:
        return None
    bl = ''
    seen = []
    for s in bld:
        if s not in seen:
            seen.append(s)
    if seen:
        bl = '<p:bldLst>' + ''.join(f'<p:bldP spid="{s}" grpId="0"/>' for s in seen) + '</p:bldLst>'
    return (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            + seqs + '</p:childTnLst></p:cTn></p:par></p:tnLst>' + bl + '</p:timing>')


# name grammar: @fx<N>[dir]-label   (N = order on the slide; dir l|r|t|b for fly/wipe, h|v for split)
NAME_RE = re.compile(r'^@(fade|float|wipe|blink|fly|zoom|split|type|word|pulse|spin|appear|wheel|drop|rise)(\d+)([lrtbhv])?-')


def effect_from_name(name, stagger):
    m = NAME_RE.match(name or '')
    if not m:
        return None
    fx, n, d = m.group(1), int(m.group(2)), m.group(3)
    e = {'fx': fx, 'order': n, 'delay': None}
    if d:
        e['dir'] = d
    if fx in ('blink', 'pulse', 'spin'):
        e['loop'] = True
    return e


# ------------------------------------------------------------------ reading back (check_deck, preview)

def describe_transition(slide_root):
    """(name, ms) of the transition a slide plays in PowerPoint 2010+ (the mc:Choice branch), e.g. ('morph', 1300),
    ('curtains', 1600), ('push', 800). ('none', None) when the slide has no transition."""
    tr = None
    for el in slide_root.iter('{%s}transition' % P_NS):
        tr = el
        break  # the first one is the mc:Choice branch when wrapped
    if tr is None:
        return 'none', None
    ms = tr.get('{http://schemas.microsoft.com/office/powerpoint/2010/main}dur') or tr.get('spd')
    kids = [k for k in tr if isinstance(k.tag, str)]
    if not kids:
        return 'cut-in', ms
    k = kids[0]
    local = k.tag.split('}')[-1]
    if local == 'prstTrans':
        prst = k.get('prst', 'prstTrans')
        for name, (kind, el, _d) in TRANSITIONS.items():
            if kind == 'p15' and el == prst:
                return name, ms
        return prst, ms
    for name, (_, el, _d) in TRANSITIONS.items():
        if el == local:
            return name, ms
    return local, ms


def timing_census(slide_root):
    """What a slide's p:timing really asks PowerPoint to do, plus structural errors."""
    out = {'entr': 0, 'emph': 0, 'exit': 0, 'path': 0, 'media': 0, 'iterate': 0, 'trigger': 0, 'loop': 0,
           'click': 0, 'errors': []}
    timing = slide_root.find('{%s}timing' % P_NS)
    if timing is None:
        return out
    spids = {c.get('id') for c in slide_root.iter('{%s}cNvPr' % P_NS)}
    ids = Counter()
    for ctn in timing.iter('{%s}cTn' % P_NS):
        ids[ctn.get('id')] += 1
        pc = ctn.get('presetClass')
        if pc in ('entr', 'emph', 'exit', 'path', 'mediacall'):
            out['media' if pc == 'mediacall' else pc] += 1
        if ctn.get('nodeType') == 'clickEffect':
            out['click'] += 1
        if ctn.get('repeatCount') == 'indefinite':
            out['loop'] += 1
    out['iterate'] = len(list(timing.iter('{%s}iterate' % P_NS)))
    out['trigger'] = sum(1 for s in timing.iter('{%s}seq' % P_NS)
                         if s.find('{%s}cTn' % P_NS) is not None and s.find('{%s}cTn' % P_NS).get('nodeType') == 'interactiveSeq')
    dup = sorted(k for k, v in ids.items() if v > 1)
    if dup:
        out['errors'].append(f'duplicate timing node ids {dup[:6]} (PowerPoint will refuse to open or repair the slide)')
    missing = sorted({t.get('spid') for t in timing.iter('{%s}spTgt' % P_NS)} - spids)
    if missing:
        out['errors'].append(f'animation targets shape ids that are not on the slide: {missing[:6]}')
    return out
