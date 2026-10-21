"""Construction-based motion for native diagrams (v5.5): Anatomy's "the object is the explanation" and
Manim's Create / GrowFromEdge / Write / LaggedStart / Transform / MovingCamera, written as editable
PowerPoint shapes and effects.

A `construct` component in deck.json draws a MODEL (parts in model units) into a box and, on the slide
where it is first shown, builds it part by part in the order the object is made: base first, then what
rests on it, the mechanism, the controls, the one lit subject, and the words around it last. Every part
keeps the name `!!<component>.<part id>`, so the next keyframe slide can show the same model in another
STATE (Transform: the parts Morph to their new geometry) or through another CAMERA (MovingCamera: the
whole model is scaled and moved so one part fills the frame) and PowerPoint's Morph does the motion.

  {"type": "construct", "name": "lock", "x": 1, "y": 1.2, "w": 7, "h": 5,
   "model": "design/lock.model.json"            or inline "frame": [W, H], "parts": [...]
   "state": "rest",                              which state the parts are drawn in (default: none)
   "camera": {"focus": "pin3" | [mx, my], "zoom": 2.2},   default: the whole frame, zoom 1
   "reveal": true | ["id", ...] | false,         build every part / only these (new) parts / nothing
   "ms": 650, "total_ms": 4200, "start": 0,      one part's run and the whole build (LaggedStart fits it)
   "indicate": ["pin3"],                         a short Indicate pulse after the build
   "trace": [{"part": "key", "path": [[mx, my], ...], "ms": 1400}]}   a part moves along a model path

A part:
  {"id": "plug", "kind": "rect|ellipse|poly|line|arc|text|image|iso_box|iso_cyl",
   "at": [x, y, w, h]             rect/ellipse/image (model units, y down); text: x, y in the model, w, h in inches
                                  (words keep their size under a camera zoom; "scale_box": true scales them too)
   "points": [[x, y], ...]        poly ("open": true = a stroke path), line = two points
   "box": [x, y, z, w, d, h]      iso_box / iso_cyl (world units, z up; drawn in the one isometric camera)
   "layer": "base|structure|mechanism|control|subject|label",
   "on": "<id of the part it rests on>",          the build order follows it (Anatomy: each part sits on another)
   "fill": "surface", "line": "ink", "width": 1.25, "alpha": 0.2, "radius": 0.1, "role": "label", "text": "...",
   "lit": true                    the ONE accent part (Anatomy: one lit part per frame; parts sharing a "group" count as one)
   "verb": "auto|create|grow|write|sweep|zoom|wipe|fade|none", "dir": "b"   override the chosen verb
   "step": 3                      parts with the same step build together (AnimationGroup)
   "states": {"open": {"at": [...], "points": [...], "box": [...], "fill": "...", "hide": true, "text": "..."}}}

Verbs (auto) — how a thing is made, never a generic fade:
  line / open poly  -> create : wipe that follows the stroke from its first point (Manim Create)
  outline circle    -> sweep  : clockwise wheel from 12 o'clock (Create on a circle)
  solid on a part   -> grow   : Stretch out of the edge it rests on (GrowFromEdge); a base grows from the bottom
  solid inside one  -> zoom   : grows from its centre (GrowFromCenter)
  text              -> write  : letter by letter (Write), after the part it names
  image             -> wipe   : revealed from the side it faces
  iso solids        -> grow from the bottom, faces together (a solid is one step)
Order: depth along `on`, then layer rank, then the order written; `step` groups. The lag between steps is
fitted so the whole build lasts `total_ms` (default 600 ms per step, at most 5 s): LaggedStart, lag_ratio < 1.
"""
import json
import math
from pathlib import Path

LAYERS = ['base', 'structure', 'mechanism', 'control', 'subject', 'label']
ISO = (math.cos(math.radians(30)), math.sin(math.radians(30)))


def _hex(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _mixhex(a, b, k):
    ca, cb = _hex(a), _hex(b)
    return '#' + ''.join(f'{round(x + (y - x) * k):02X}' for x, y in zip(ca, cb))


def tones(spec, colour):
    """Anatomy's four tones by facing: top lightest, then three side shades (toward / across / away from the light)."""
    base = spec.color(colour) if spec else colour
    base = '#' + base.lstrip('#')
    return {'top': _mixhex(base, '#FFFFFF', 0.28), 'right': base, 'left': _mixhex(base, '#000000', 0.18),
            'away': _mixhex(base, '#000000', 0.34)}


def iso(x, y, z):
    """World (x right, y back, z up) -> model plane (u right, v down), one isometric camera."""
    return ((x - y) * ISO[0], (x + y) * ISO[1] - z)


def load_model(sh, root=None):
    m = sh.get('model')
    if isinstance(m, str):
        p = Path(m)
        if not p.is_absolute() and root:
            p = Path(root) / p
        m = json.loads(p.read_text(encoding='utf-8'))
    m = dict(m or {})
    for k in ('frame', 'parts'):
        if k in sh:
            m[k] = sh[k]
    if 'parts' not in m:
        raise SystemExit(f'construct {sh.get("name")!r}: needs "parts" (inline or in "model")')
    return m


def part_in_state(p, state):
    q = dict(p)
    if state and state in (p.get('states') or {}):
        q.update(p['states'][state])
    return q


def model_bbox(parts):
    xs, ys = [], []
    for p in parts:
        if p.get('kind') == 'text':
            continue    # words live around the drawing; they never set its fit
        for (u, v) in outline(p):
            xs.append(u)
            ys.append(v)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 1, 1)


def outline(p):
    """Model-plane points that bound a part (for fitting and contact edges)."""
    k = p.get('kind', 'rect')
    if k in ('iso_box', 'iso_cyl'):
        x, y, z, w, d, h = p['box']
        return [iso(x + a, y + b, z + c) for a in (0, w) for b in (0, d) for c in (0, h)]
    if k in ('poly', 'line'):
        return [tuple(q) for q in p['points']]
    if 'at' in p:
        x, y, w, h = p['at']
        return [(x, y), (x + w, y + h)]
    return []


class Camera:
    """Model units -> slide inches. fit = the whole frame in the box; focus/zoom = MovingCamera."""

    def __init__(self, box, frame, cam=None, parts=None):
        bx, by, bw, bh = box
        fx0, fy0, fx1, fy1 = frame if len(frame) == 4 else (0, 0, frame[0], frame[1])
        fw, fh = fx1 - fx0, fy1 - fy0
        self.k = min(bw / fw, bh / fh)
        self.cx, self.cy = bx + bw / 2, by + bh / 2
        cam = cam or {}
        self.zoom = float(cam.get('zoom', 1.0))
        f = cam.get('focus')
        if isinstance(f, str):
            hit = [p for p in (parts or []) if p.get('id') == f]
            if not hit:
                raise SystemExit(f'construct camera: focus part {f!r} not in the model')
            x0, y0, x1, y1 = model_bbox(hit)
            f = [(x0 + x1) / 2, (y0 + y1) / 2]
        self.fx, self.fy = f if f else ((fx0 + fx1) / 2, (fy0 + fy1) / 2)
        if cam.get('at'):   # where the focus lands on the slide (inches), default the box centre
            self.cx, self.cy = cam['at']

    def pt(self, u, v):
        s = self.k * self.zoom
        return (round(self.cx + (u - self.fx) * s, 3), round(self.cy + (v - self.fy) * s, 3))

    def length(self, d):
        return d * self.k * self.zoom


def _depths(parts):
    by = {p['id']: p for p in parts}
    memo = {}

    def depth(i, seen=()):
        if i in memo:
            return memo[i]
        p = by[i]
        on = p.get('on')
        if on and on not in by:
            raise SystemExit(f'construct: part {i!r} rests on {on!r}, which is not in the model')
        if on in seen:
            raise SystemExit(f'construct: parts rest on each other in a loop ({" -> ".join(seen + (i,))})')
        memo[i] = 0 if not on else depth(on, seen + (i,)) + 1
        return memo[i]
    return {i: depth(i) for i in by}


def build_order(parts):
    """Steps (lists of part ids) in the order the object is made. Labels follow what they name."""
    depth = _depths(parts)
    rank = {n: i for i, n in enumerate(LAYERS)}
    idx = {p['id']: i for i, p in enumerate(parts)}
    explicit = {p['id']: p['step'] for p in parts if 'step' in p}
    solid = [p for p in parts if p.get('layer') != 'label' and p.get('kind') != 'text']
    words = [p for p in parts if p not in solid]
    key = lambda p: (explicit.get(p['id'], 10 ** 6), depth[p['id']], rank.get(p.get('layer', 'structure'), 1), idx[p['id']])
    steps, cur = [], None
    for p in sorted(solid, key=key):
        s = explicit.get(p['id'])
        if s is not None and steps and cur == s:
            steps[-1].append(p['id'])
        else:
            steps.append([p['id']])
        cur = s
    for w in sorted(words, key=lambda p: (explicit.get(p['id'], 10 ** 6), idx[p['id']])):
        tgt = w.get('on')
        pos = max((i for i, st in enumerate(steps) if tgt in st), default=len(steps) - 1)
        steps.insert(pos + 1, [w['id']]) if pos + 1 <= len(steps) else steps.append([w['id']])
    return steps


def contact_edge(p, parent, cam):
    """The edge of p that touches what it rests on (the edge it grows FROM)."""
    if parent is None:
        return 'b'
    (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = model_bbox([p]), model_bbox([parent])
    pcx, pcy = (ax0 + ax1) / 2, (ay0 + ay1) / 2
    inside = ax0 >= bx0 - 1e-6 and ax1 <= bx1 + 1e-6 and ay0 >= by0 - 1e-6 and ay1 <= by1 + 1e-6
    if inside:
        return 'c'
    gaps = {'b': ay1 - by0 if pcy < by0 + (by1 - by0) / 2 else None, 't': by1 - ay0 if pcy > by0 + (by1 - by0) / 2 else None}
    if pcy <= by0:
        return 'b'      # above its support: rises off it
    if pcy >= by1:
        return 't'      # hangs below it
    return 'l' if pcx >= bx1 else ('r' if pcx <= bx0 else 'b')


def stroke_dir(points):
    (x0, y0), (x1, y1) = points[0], points[-1]
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) >= abs(dy):
        return 'l' if dx >= 0 else 'r'
    return 't' if dy >= 0 else 'b'


def choose_verb(p, parent, cam):
    k = p.get('kind', 'rect')
    v = p.get('verb', 'auto')
    if v not in ('auto', None):
        return v, p.get('dir')
    if k == 'text' or p.get('layer') == 'label':
        return 'write', None
    if k == 'line' or (k == 'poly' and p.get('open')) or k == 'arc':
        return 'create', stroke_dir(p['points'])
    if k == 'ellipse' and not p.get('fill'):
        return 'sweep', None
    if k == 'image':
        return 'wipe', 'l'
    edge = contact_edge(p, parent, cam)
    if edge == 'c':
        return 'zoom', None
    return 'grow', edge


VERB_FX = {'create': 'wipe', 'grow': 'stretch', 'write': 'type', 'sweep': 'wheel', 'zoom': 'zoom', 'wipe': 'wipe',
           'fade': 'fade', 'rise': 'rise', 'fly': 'fly'}


def anims_for(verb, d, delay, ms):
    if verb in ('none', None):
        return []
    fx = VERB_FX.get(verb, verb)
    a = {'fx': fx, 'delay': int(delay), 'ms': int(ms)}
    if d and fx in ('wipe', 'stretch', 'fly'):
        a['dir'] = 'h' if (fx == 'stretch' and d == 'c') else d
    if fx == 'type':
        a['by'] = 'letter'
        a['step'] = 6
        a['ms'] = max(300, int(ms * 0.6))
    return [a]


def shapes_for(p, base, cam, spec, lit_colour):
    """Primitive deck shapes for one part (in its state)."""
    k = p.get('kind', 'rect')
    name = f'!!{base}.{p["id"]}' if base else f'!!{p["id"]}'
    fill = p.get('fill')
    if p.get('lit'):
        fill = lit_colour
    common = {}
    for key in ('alpha', 'shadow', 'gradient', 'angle', 'line_alpha', 'dash', 'cap'):
        if key in p:
            common[key] = p[key]
    lw = p.get('width', 1.25)
    out = []
    if k in ('rect', 'ellipse', 'image', 'text'):
        x, y, w, h = p['at']
        if k == 'text' and not p.get('scale_box'):
            # a label is anchored in the model (its top-left follows the camera) but its box is in inches:
            # words keep their size when the camera zooms (Anatomy: text lives around the drawing)
            sx, sy = cam.pt(x, y)
            box = {'x': sx, 'y': sy, 'w': w, 'h': h}
        else:
            (sx, sy), (ex, ey) = cam.pt(x, y), cam.pt(x + w, y + h)
            box = {'x': sx, 'y': sy, 'w': round(ex - sx, 3), 'h': round(ey - sy, 3)}
        if k == 'image':
            out.append({'type': 'image', 'name': name, 'path': p['path'], 'fit': p.get('fit', 'cover'), **box, **common})
        elif k == 'text':
            t = {'type': 'text', 'name': name, 'text': p.get('text', ''), 'role': p.get('role', 'label'), **box}
            for key in ('color', 'align', 'size', 'valign', 'bold'):
                if key in p:
                    t[key] = p[key]
            if p.get('scale_text') and 'size' in p:
                t['size'] = round(p['size'] * cam.zoom, 1)
            out.append(t)
        else:
            s = {'type': k, 'name': name, **box, **common}
            if fill:
                s['fill'] = fill
            if p.get('line'):
                s['line_color'], s['line_width'] = p['line'], lw
            if p.get('radius'):
                s['radius'] = p['radius']
            out.append(s)
    elif k in ('poly', 'line', 'arc'):
        pts = [list(cam.pt(u, v)) for u, v in p['points']]
        if k == 'line' and len(pts) == 2:
            out.append({'type': 'line', 'name': name, 'x1': pts[0][0], 'y1': pts[0][1], 'x2': pts[1][0], 'y2': pts[1][1],
                        'color': p.get('line', 'ink'), 'width': lw, **common})
        else:
            s = {'type': 'poly', 'name': name, 'points': pts, **common}
            if p.get('open') or k == 'arc':
                s['open'] = True
            if fill and not s.get('open'):
                s['fill'] = fill
            if p.get('line') or s.get('open'):
                s['line_color'], s['line_width'] = p.get('line', 'ink'), lw
            out.append(s)
    elif k == 'iso_box':
        x, y, z, w, d, h = p['box']
        tn = tones(spec, fill or 'surface')
        P = lambda a, b, c: list(cam.pt(*iso(a, b, c)))
        faces = {
            'left': [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)],
            'right': [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)],
            'top': [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)],
        }
        for f in ('left', 'right', 'top'):
            s = {'type': 'poly', 'name': f'{name}.{f}', 'points': faces[f], 'fill': tn[f], **common}
            s['line_color'], s['line_width'] = p.get('line', tn['away']), p.get('width', 0.75)
            out.append(s)
    elif k == 'iso_cyl':
        x, y, z, w, d, h = p['box']
        r = min(w, d) / 2
        cxw, cyw = x + w / 2, y + d / 2
        tn = tones(spec, fill or 'surface')
        n = 24
        ring = lambda zz: [list(cam.pt(*iso(cxw + r * math.cos(2 * math.pi * i / n), cyw + r * math.sin(2 * math.pi * i / n), zz))) for i in range(n)]
        lo, hi = ring(z), ring(z + h)
        # the visible half of the body: the side facing the camera (angles 0..180 in world = toward +x,+y)
        idx = [i for i in range(n) if ((360 * i / n) + 45) % 360 <= 180]   # the half facing the camera: -45..135 deg
        idx = sorted(idx, key=lambda i: ((360 * i / n) + 45) % 360)
        body = [lo[i] for i in idx] + [hi[i] for i in reversed(idx)]
        shade = {'gradient': [[tn['away'], 1, 0], [tn['left'], 1, 28], [tn['top'], 1, 64], [tn['right'], 1, 82], [tn['left'], 1, 100]],
                 'angle': 0} if not p.get('flat') else {'fill': tn['left']}
        out.append({'type': 'poly', 'name': f'{name}.body', 'points': body, **shade, 'line_color': p.get('line', tn['away']),
                    'line_width': p.get('width', 0.75), **common})
        out.append({'type': 'poly', 'name': f'{name}.top', 'points': hi, 'fill': tn['top'], 'line_color': p.get('line', tn['away']),
                    'line_width': p.get('width', 0.75), **common})
    else:
        raise SystemExit(f'construct part {p.get("id")!r}: unknown kind {k!r}')
    for s in out:
        s['bleed'] = True        # a camera move may carry parts past the edge on purpose
        s['overlay'] = True      # parts sit on each other: the collision check is for text blocks
    return out


def comp_construct(spec, sh, root=None):
    base = sh.get('name') or 'fig'
    model = load_model(sh, root or getattr(spec, 'root', None))
    state = sh.get('state')
    parts0 = model['parts']
    ids = [p.get('id') for p in parts0]
    if None in ids or len(set(ids)) != len(ids):
        raise SystemExit(f'construct {base!r}: every part needs a unique "id"')
    parts = [part_in_state(p, state) for p in parts0]
    frame = model.get('frame') or list(model_bbox(parts0))   # the REST geometry fixes the fit: every state and camera shares it
    fw, fh = (frame[2] - frame[0], frame[3] - frame[1]) if len(frame) == 4 else frame
    box = (sh['x'], sh['y'], sh['w'], sh.get('h', sh['w'] * fh / fw))
    cam = Camera(box, frame, sh.get('camera'), parts)
    lit = sh.get('lit', model.get('lit', 'lit'))
    lits = sorted({p.get('group', p['id']) for p in parts if p.get('lit') and not p.get('hide')})
    if len(lits) > 1 and not sh.get('allow_many_lit'):
        raise SystemExit(f'construct {base!r}: {len(lits)} lit parts {lits}: one lit part (or one "group") per frame (Anatomy); '
                         'set "allow_many_lit" to override')
    by = {p['id']: p for p in parts}
    shown = [p for p in parts if not p.get('hide')]
    reveal = sh.get('reveal', False)
    to_build = set(by) if reveal is True else (set(reveal) if isinstance(reveal, list) else set())
    unknown = to_build - set(by)
    if unknown:
        raise SystemExit(f'construct {base!r}: reveal names unknown parts {sorted(unknown)}')
    steps = [[i for i in st if i in to_build and not by[i].get('hide')] for st in build_order(shown)]
    steps = [s for s in steps if s]
    ms = int(sh.get('ms', 650))
    total = int(sh.get('total_ms', min(5000, max(ms, 600 * len(steps)))))
    lag = (total - ms) / max(1, len(steps) - 1) if len(steps) > 1 else 0
    lag = max(60, min(lag, ms))      # lag_ratio between ~0.1 and 1: overlapping, never a slideshow of parts
    start = int(sh.get('start', 0))
    when = {i: start + n * lag for n, st in enumerate(steps) for i in st}
    out = []
    order_note = []
    for p in parts:
        if p.get('hide'):
            continue
        prims = shapes_for(p, base, cam, spec, lit)
        if p['id'] in when:
            verb, d = choose_verb(p, by.get(p.get('on')), cam)
            if p.get('kind') in ('iso_box', 'iso_cyl') and verb in ('grow', 'zoom'):
                d = 'b'
                verb = 'grow'
            a = anims_for(verb, d, when[p['id']], ms)
            for s in prims:
                if a:
                    s['anim'] = [dict(x) for x in a]
            order_note.append((when[p['id']], p['id'], verb))
        out.extend(prims)
    end = start + (max(when.values()) + ms if when else 0)
    for i in sh.get('indicate', []):
        hits = [s for s in out if s['name'].startswith(f'!!{base}.{i}')]
        if not hits:
            raise SystemExit(f'construct {base!r}: indicate names an unknown or hidden part {i!r}')
        for s in hits:
            s.setdefault('anim', []).append({'fx': 'indicate', 'delay': int(end + 150), 'ms': 450})
    for tr in sh.get('trace', []):
        hits = [s for s in out if s['name'] == f'!!{base}.{tr["part"]}' or s['name'].startswith(f'!!{base}.{tr["part"]}.')]
        if not hits:
            raise SystemExit(f'construct {base!r}: trace names an unknown part {tr["part"]!r}')
        pts = tr['path']
        rel = [[round(cam.length(u - pts[0][0]), 3), round(cam.length(v - pts[0][1]), 3)] for u, v in pts]
        for s in hits:
            s.setdefault('anim', []).append({'fx': 'path', 'path': rel, 'delay': int(tr.get('delay', end + 200)),
                                             'ms': int(tr.get('ms', 1400))})
    if hasattr(spec, 'notes_construct'):
        spec.notes_construct.append((base, sorted(order_note)))
    return out
