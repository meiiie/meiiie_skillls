"""Hand-built architecture animation: one JSON diagram -> an animated MP4 AND the same diagram as
editable deck.json shapes. No clip-art, no AI pictures: boxes, pipes, arrows and flowing dots drawn
from the structure itself (the anatomy idea: the object is the explanation).

  python diagram_video.py diagram.json --mp4 WORK/assets/arch.mp4 --fragment WORK/design/arch-shapes.json
                          [--poster WORK/assets/arch.poster.png] [--fps 30] [--seconds 9] [--ppi 144]

diagram.json
  {"x": 0.9, "y": 1.6, "w": 11.5, "h": 5.0,          region on the slide, inches
   "palette": {"bg": "#0D2D52", "node": "#123A66", "line": "#E8F1FF", "ink": "#FFFFFF", "muted": "#B4CAE8",
               "accent": "#FFB627", "grid": "#FFFFFF"},   ("bg": null = transparent video is not possible
                                                          in MP4, so the bg is painted; match the slide)
   "font": "Space Grotesk", "label_pt": 14,
   "nodes": [{"id": "phin", "label": "Phin", "sub": "lọc", "x": 1, "y": 1, "w": 2, "h": 0.9,
              "kind": "box|pill|db|circle", "lit": true}],       x, y relative to the region
   "edges": [{"from": "a", "to": "b", "label": "nước 92°C", "route": "straight|hv|vh", "flow": true,
              "dash": false}],
   "notes": "..."}

What it makes
  MP4 (H.264, yuv420p): nodes pop in one by one, edges draw on with an arrow head, then dots flow
  along every "flow" edge in a loop, the lit node breathes. Frame 0 is empty; the last frame is the
  full diagram, so the poster (last frame) and the editable fallback show the same picture.
  Fragment: a list of build_deck shapes (rect/ellipse/text/line with "anim") that rebuild the same
  diagram natively: nodes zoom in staggered, edges wipe in their direction, flow dots run a looping
  motion path. Use the video where PowerPoint plays it, the fragment on the next keyframe (or on its
  own for Google Slides / Keynote / print), or both: video first, then Morph to the editable slide.

For mathematical or physical scenes (curves, vectors, equations) write a Manim scene instead:
references/diagram-video.md shows the manimgx route (`manimgx render scene.py`).
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def anchor(n, side):
    x, y, w, h = n['x'], n['y'], n['w'], n['h']
    return {'l': (x, y + h / 2), 'r': (x + w, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[side]


def route(a, b, mode='straight'):
    """Polyline (inches, region coords) from node a to node b."""
    ax, ay = a['x'] + a['w'] / 2, a['y'] + a['h'] / 2
    bx, by = b['x'] + b['w'] / 2, b['y'] + b['h'] / 2
    dx, dy = bx - ax, by - ay
    if mode == 'hv':
        p0 = anchor(a, 'r' if dx > 0 else 'l')
        p2 = anchor(b, 't' if dy > 0 else 'b')
        return [p0, (p2[0], p0[1]), p2]
    if mode == 'vh':
        p0 = anchor(a, 'b' if dy > 0 else 't')
        p2 = anchor(b, 'l' if dx > 0 else 'r')
        return [p0, (p0[0], p2[1]), p2]
    if abs(dx) >= abs(dy):
        return [anchor(a, 'r' if dx > 0 else 'l'), anchor(b, 'l' if dx > 0 else 'r')]
    return [anchor(a, 'b' if dy > 0 else 't'), anchor(b, 't' if dy > 0 else 'b')]


def length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def point_at(pts, t):
    """Point at fraction t of the polyline length, plus the segment direction."""
    total = length(pts) or 1e-6
    d = t * total
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if d <= seg or i == len(pts) - 2:
            f = 0 if seg == 0 else min(1, d / seg)
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
            return (x, y), (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        d -= seg
    return pts[-1], (1, 0)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def schedule(d):
    n, e = len(d['nodes']), len(d['edges'])
    T = d.get('seconds', 9.0)
    build = min(T * 0.55, 0.45 * n + 0.5 * e + 0.6)
    node_t = {nd['id']: 0.2 + i * 0.45 for i, nd in enumerate(d['nodes'])}
    edge_t = []
    for j, ed in enumerate(d['edges']):
        start = max(node_t[ed['from']], node_t[ed['to']]) + 0.35
        edge_t.append(start)
    return T, node_t, edge_t, build


def frame_svg(d, t, ppi):
    P = d['palette']
    W, H = d['w'] * ppi, d['h'] * ppi
    T, node_t, edge_t, _ = schedule(d)
    nodes = {n['id']: n for n in d['nodes']}
    font = d.get('font', 'Space Grotesk')
    lp = d.get('label_pt', 14) / 72 * ppi
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">',
           f'<rect width="100%" height="100%" fill="{P.get("bg", "#000000")}"/>']
    if P.get('grid'):
        step = 0.25 * ppi
        out.append(f'<g stroke="{P["grid"]}" stroke-opacity="0.06" stroke-width="1">')
        x = 0.0
        while x < W:
            out.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H:.1f}"/>'); x += step
        y = 0.0
        while y < H:
            out.append(f'<line x1="0" y1="{y:.1f}" x2="{W:.1f}" y2="{y:.1f}"/>'); y += step
        out.append('</g>')
    # edges
    for ed, t0 in zip(d['edges'], edge_t):
        pts = route(nodes[ed['from']], nodes[ed['to']], ed.get('route', 'straight'))
        k = ease((t - t0) / 0.6)
        if k <= 0:
            continue
        L = length(pts) * ppi
        path = 'M' + ' L'.join(f'{x * ppi:.1f},{y * ppi:.1f}' for x, y in pts)
        dash = ' stroke-dasharray="6 6"' if ed.get('dash') else ''
        if dash:
            out.append(f'<path d="{path}" fill="none" stroke="{P["line"]}" stroke-width="2.2" stroke-opacity="{k:.2f}"{dash}/>')
        else:
            out.append(f'<path d="{path}" fill="none" stroke="{P["line"]}" stroke-width="2.2" '
                       f'stroke-dasharray="{L:.1f}" stroke-dashoffset="{L * (1 - k):.1f}" stroke-linecap="round"/>')
        if k > 0.95:
            (hx, hy), (vx, vy) = point_at(pts, 1.0)
            a = math.atan2(vy, vx)
            s = 0.11 * ppi
            p1 = (hx * ppi, hy * ppi)
            p2 = (p1[0] - s * math.cos(a - 0.45), p1[1] - s * math.sin(a - 0.45))
            p3 = (p1[0] - s * math.cos(a + 0.45), p1[1] - s * math.sin(a + 0.45))
            out.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} Z" fill="{P["line"]}"/>')
        if ed.get('label') and k > 0.6:
            (mx, my), _ = point_at(pts, 0.5)
            out.append(f'<text x="{mx * ppi:.1f}" y="{my * ppi - 0.12 * ppi:.1f}" font-family="{font}" font-size="{lp * 0.8:.1f}" '
                       f'fill="{P.get("muted", P["ink"])}" text-anchor="middle" opacity="{(k - 0.6) / 0.4:.2f}">{esc(ed["label"])}</text>')
        if ed.get('flow', True) and t > t0 + 0.6:
            for m in range(3):
                f = ((t - t0 - 0.6) / 1.6 + m / 3) % 1
                (fx, fy), _ = point_at(pts, f)
                out.append(f'<circle cx="{fx * ppi:.1f}" cy="{fy * ppi:.1f}" r="{0.06 * ppi:.1f}" fill="{P["accent"]}"/>')
    # nodes
    for nd in d['nodes']:
        k = ease((t - node_t[nd['id']]) / 0.45)
        if k <= 0:
            continue
        cx, cy = (nd['x'] + nd['w'] / 2) * ppi, (nd['y'] + nd['h'] / 2) * ppi
        sc = 0.85 + 0.15 * k
        w, h = nd['w'] * ppi, nd['h'] * ppi
        lit = nd.get('lit')
        stroke = P['accent'] if lit else P['line']
        fill = P.get('node', P['bg'])
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) scale({sc:.3f})" opacity="{k:.2f}">']
        if lit and t > node_t[nd['id']] + 0.5:
            br = 0.5 + 0.5 * math.sin((t - node_t[nd['id']]) * 2.4)
            g.append(f'<rect x="{-w / 2 - 6:.1f}" y="{-h / 2 - 6:.1f}" width="{w + 12:.1f}" height="{h + 12:.1f}" rx="{min(w, h) * 0.22:.1f}" '
                     f'fill="none" stroke="{P["accent"]}" stroke-opacity="{0.15 + 0.35 * br:.2f}" stroke-width="5"/>')
        kind = nd.get('kind', 'box')
        if kind == 'circle':
            g.append(f'<ellipse rx="{w / 2:.1f}" ry="{h / 2:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        elif kind == 'db':
            e = h * 0.14
            g.append(f'<path d="M{-w / 2:.1f},{-h / 2 + e:.1f} v{h - 2 * e:.1f} a{w / 2:.1f},{e:.1f} 0 0 0 {w:.1f},0 v{-(h - 2 * e):.1f}" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
            g.append(f'<ellipse cy="{-h / 2 + e:.1f}" rx="{w / 2:.1f}" ry="{e:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        else:
            rx = h / 2 if kind == 'pill' else 0.06 * ppi
            g.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        dy = -lp * 0.15 if nd.get('sub') else lp * 0.35
        if kind == 'db':
            dy += h * 0.08
        g.append(f'<text y="{dy:.1f}" font-family="{font}" font-weight="700" font-size="{lp:.1f}" fill="{P["ink"]}" text-anchor="middle">{esc(nd["label"])}</text>')
        if nd.get('sub'):
            g.append(f'<text y="{dy + lp * 1.1:.1f}" font-family="{font}" font-size="{lp * 0.72:.1f}" fill="{P.get("muted", P["ink"])}" text-anchor="middle">{esc(nd["sub"])}</text>')
        g.append('</g>')
        out.extend(g)
    out.append('</svg>')
    return '\n'.join(out)


def render_mp4(d, mp4, fps=30, ppi=144, poster=None):
    import cairosvg
    T = d.get('seconds', 9.0)
    W, H = int(d['w'] * ppi) // 2 * 2, int(d['h'] * ppi) // 2 * 2
    mp4 = Path(mp4)
    mp4.parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(fps), '-i', '-',
                           '-vf', f'scale={W}:{H}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart',
                           str(mp4)], stdin=subprocess.PIPE)
    last = None
    for i in range(int(T * fps)):
        png = cairosvg.svg2png(bytestring=frame_svg(d, i / fps, ppi).encode('utf-8'))
        ff.stdin.write(png)
        last = png
    ff.stdin.close()
    ff.wait()
    if ff.returncode:
        raise SystemExit('ffmpeg failed')
    if poster and last:
        Path(poster).write_bytes(last)
    return mp4


def fragment(d, prefix='arch'):
    """Editable build_deck shapes for the same diagram (slide inches), with native animation."""
    P = d['palette']
    ox, oy = d['x'], d['y']
    nodes = {n['id']: n for n in d['nodes']}
    _, node_t, edge_t, _ = schedule(d)
    out = []
    for ed, t0 in zip(d['edges'], edge_t):
        pts = route(nodes[ed['from']], nodes[ed['to']], ed.get('route', 'straight'))
        for k in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[k], pts[k + 1]
            last = k == len(pts) - 2
            dirn = ('r' if x2 > x1 else 'l') if abs(x2 - x1) >= abs(y2 - y1) else ('b' if y2 > y1 else 't')
            out.append({'type': 'line', 'name': f'{prefix}-e-{ed["from"]}-{ed["to"]}-{k}', 'x1': ox + x1, 'y1': oy + y1,
                        'x2': ox + x2, 'y2': oy + y2, 'color': P['line'], 'width': 1.75, 'arrow': last,
                        **({'dash': 'dash'} if ed.get('dash') else {}),
                        'anim': {'fx': 'wipe', 'dir': {'r': 'l', 'l': 'r', 'b': 't', 't': 'b'}[dirn], 'ms': 450,
                                 'delay': int(t0 * 1000) + k * 200}})
        if ed.get('label'):
            (mx, my), _ = point_at(pts, 0.5)
            out.append({'type': 'text', 'name': f'{prefix}-el-{ed["from"]}-{ed["to"]}', 'text': ed['label'],
                        'x': ox + mx - 1.0, 'y': oy + my - 0.42, 'w': 2.0, 'h': 0.3, 'role': 'caption', 'align': 'c',
                        'color': P.get('muted', P['ink']), 'anim': {'fx': 'fade', 'delay': int(t0 * 1000) + 300}})
        if ed.get('flow', True):
            (sx, sy) = pts[0]
            rel = [[x - sx, y - sy] for x, y in pts]
            out.append({'type': 'ellipse', 'name': f'{prefix}-f-{ed["from"]}-{ed["to"]}', 'x': ox + sx - 0.06, 'y': oy + sy - 0.06,
                        'w': 0.12, 'h': 0.12, 'fill': P['accent'],
                        'anim': [{'fx': 'appear', 'delay': int(t0 * 1000) + 600},
                                 {'fx': 'path', 'path': rel, 'ms': int(1600 * max(0.6, length(pts) / 3)), 'loop': True}]})
    for nd in d['nodes']:
        kind = nd.get('kind', 'box')
        base = {'name': f'{prefix}-n-{nd["id"]}', 'x': ox + nd['x'], 'y': oy + nd['y'], 'w': nd['w'], 'h': nd['h'],
                'fill': P.get('node', P['bg']), 'line_color': P['accent'] if nd.get('lit') else P['line'], 'line_width': 1.75}
        if kind == 'circle':
            shp = {'type': 'ellipse', **base}
        else:
            shp = {'type': 'rect', **base, 'radius': 0.5 if kind == 'pill' else (0.12 if kind == 'db' else 0.06)}
        anim = [{'fx': 'zoom', 'ms': 450, 'delay': int(node_t[nd['id']] * 1000)}]
        if nd.get('lit'):
            anim.append({'fx': 'pulse', 'scale': 1.06, 'loop': True})
        shp['anim'] = anim
        out.append(shp)
        out.append({'type': 'text', 'name': f'{prefix}-t-{nd["id"]}', 'text': [{'text': nd['label'], 'role': 'cardtitle', 'size': d.get('label_pt', 14), 'color': P['ink']}]
                    + ([{'text': nd['sub'], 'role': 'caption', 'size': round(d.get('label_pt', 14) * 0.75), 'color': P.get('muted', P['ink'])}]
                       if nd.get('sub') else []),
                    'x': ox + nd['x'], 'y': oy + nd['y'] + (nd['h'] * 0.08 if kind == 'db' else 0), 'w': nd['w'], 'h': nd['h'],
                    'role': 'cardtitle', 'align': 'c', 'anchor': 'm', 'anim': {'fx': 'fade', 'ms': 300, 'delay': int(node_t[nd['id']] * 1000) + 200}})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('diagram')
    ap.add_argument('--mp4')
    ap.add_argument('--poster')
    ap.add_argument('--fragment')
    ap.add_argument('--prefix', default='arch')
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--ppi', type=int, default=144)
    ap.add_argument('--seconds', type=float)
    a = ap.parse_args(argv)
    d = json.loads(Path(a.diagram).read_text(encoding='utf-8'))
    if a.seconds:
        d['seconds'] = a.seconds
    ids = {n['id'] for n in d['nodes']}
    bad = [e for e in d['edges'] if e['from'] not in ids or e['to'] not in ids]
    if bad:
        raise SystemExit(f'edges point at unknown nodes: {bad}')
    if a.mp4:
        render_mp4(d, a.mp4, a.fps, a.ppi, a.poster)
        print('video  ->', a.mp4, f'({d.get("seconds", 9.0)} s)', '+ poster ' + a.poster if a.poster else '')
    if a.fragment:
        frag = fragment(d, a.prefix)
        Path(a.fragment).write_text(json.dumps(frag, ensure_ascii=False, indent=1), encoding='utf-8')
        print('shapes ->', a.fragment, f'({len(frag)} editable shapes; paste into a slide\'s "shapes" or use "include")')
    if not (a.mp4 or a.fragment):
        print('nothing to do: pass --mp4 and/or --fragment')


if __name__ == '__main__':
    sys.exit(main())
