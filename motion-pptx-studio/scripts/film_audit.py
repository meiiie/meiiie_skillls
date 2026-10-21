"""v5.3.1 film checks for slides that carry a video (signature films, diagram videos).

1. video_covers_text (ERROR): a text shape that sits BELOW a video in z-order and overlaps its frame is hidden
   while the film plays (seen in the VinFast proof: station sub-labels under the line film). Text above the video
   (later in the shape tree) is a deliberate overlay and passes; text that only touches the frame by < 0.04 in passes.
2. film_edge_match (ERROR / WARN, needs --renders): a film drawn on a flat ground (Anatomy card, Manim
   background) must match the page it sits on, or the frame shows as a pale or dark rectangle. The median colour of
   the poster's outer border is compared with the rendered slide just outside the video box. A visible step
   (max channel difference > 6) on a flat poster border is an ERROR; 3-6 is a WARN. Films that run edge to edge
   with picture content (a non-uniform border) are skipped: they are meant to read as a frame.
Fix: give the film slide a solid ground of the film's background (deck.json "bg": "#FFFFFF") or set the film's card
token to the page colour; move labels outside the frame or above the video."""
import io
import re
import statistics
from pathlib import Path

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P, A, R = '{%s}' % P_NS, '{%s}' % A_NS, '{%s}' % R_NS
EMU = 914400.0
OVERLAP_MIN = 0.04   # inches in both directions


def _box(el):
    off, ext = el.find('.//' + A + 'off'), el.find('.//' + A + 'ext')
    if off is None or ext is None:
        return None
    x, y = int(off.get('x', 0)) / EMU, int(off.get('y', 0)) / EMU
    return x, y, x + int(ext.get('cx', 0)) / EMU, y + int(ext.get('cy', 0)) / EMU


def _name(el):
    c = el.find('.//' + P + 'cNvPr')
    return c.get('name', '') if c is not None else ''


def _is_video(el):
    return el.find('.//' + A + 'videoFile') is not None


def _texts(el):
    """(name, box) of every text-bearing shape inside el (el itself if it is a text shape; recurses groups)."""
    tag = el.tag.split('}')[-1]
    if tag == 'grpSp':
        out = []
        for k in el:
            if k.tag.split('}')[-1] in ('sp', 'grpSp'):
                out += _texts(k)
        return out
    if tag == 'sp' and any((t.text or '').strip() for t in el.iter(A + 't')):
        b = _box(el)
        return [(_name(el), b)] if b else []
    return []


def video_covers_text(slide_root):
    tree = slide_root.find('.//' + P + 'spTree')
    if tree is None:
        return []
    kids = [k for k in tree if k.tag.split('}')[-1] in ('sp', 'pic', 'grpSp', 'graphicFrame', 'cxnSp')]
    out = []
    for i, v in enumerate(kids):
        if not _is_video(v):
            continue
        vb = _box(v)
        if vb is None:
            continue
        for below in kids[:i]:
            for nm, tb in _texts(below):
                ox = min(vb[2], tb[2]) - max(vb[0], tb[0])
                oy = min(vb[3], tb[3]) - max(vb[1], tb[1])
                if ox > OVERLAP_MIN and oy > OVERLAP_MIN:
                    out.append(f'text {nm!r} sits under the video {_name(v)!r} ({ox:.2f} x {oy:.2f} in overlap) and is hidden while it '
                               'plays: move it outside the frame or above the video in the shape order')
    return out


def _median(px):
    return tuple(int(statistics.median(c)) for c in zip(*px)) if px else None


def _poster_border(img):
    w, h = img.size
    s = max(2, int(min(w, h) * 0.015))
    px = []
    step = max(1, (w * h) // 40000)
    data = img.load()
    for x in range(0, w, step):
        for y in list(range(0, s)) + list(range(h - s, h)):
            px.append(data[x, y])
    for y in range(0, h, step):
        for x in list(range(0, s)) + list(range(w - s, w)):
            px.append(data[x, y])
    med = _median(px)
    spread = max(statistics.pstdev([p[i] for p in px]) for i in range(3))
    return med, spread


def _ring(render, box, slide_w=13.333, slide_h=7.5, gap=0.06, width=0.1):
    W, H = render.size
    sx, sy = W / slide_w, H / slide_h
    x0, y0, x1, y1 = box
    data = render.load()
    px = []
    for side in ('t', 'b', 'l', 'r'):
        if side in 'tb':
            yy = y0 - gap - width / 2 if side == 't' else y1 + gap + width / 2
            for k in range(60):
                xx = x0 + (x1 - x0) * (k + 0.5) / 60
                X, Y = int(xx * sx), int(yy * sy)
                if 0 <= X < W and 0 <= Y < H:
                    px.append(data[X, Y])
        else:
            xx = x0 - gap - width / 2 if side == 'l' else x1 + gap + width / 2
            for k in range(40):
                yy = y0 + (y1 - y0) * (k + 0.5) / 40
                X, Y = int(xx * sx), int(yy * sy)
                if 0 <= X < W and 0 <= Y < H:
                    px.append(data[X, Y])
    return _median(px)


def film_edge_match(read, slide_part, slide_root, render_path):
    """read(name) -> bytes. Returns (errors, warns)."""
    from PIL import Image
    errors, warns = [], []
    if not render_path or not Path(render_path).is_file():
        return errors, warns
    rels_name = re.sub(r'slides/(slide\d+\.xml)$', r'slides/_rels/\1.rels', slide_part)
    try:
        from lxml import etree
        rels = {r.get('Id'): r.get('Target') for r in etree.fromstring(read(rels_name))}
    except Exception:
        return errors, warns
    render = None
    for v in slide_root.iter(P + 'pic'):
        if not _is_video(v):
            continue
        blip = v.find('.//' + A + 'blip')
        box = _box(v)
        if blip is None or box is None:
            continue
        target = rels.get(blip.get(R + 'embed'), '')
        if not target:
            continue
        media = 'ppt/' + target.replace('../', '')
        try:
            poster = Image.open(io.BytesIO(read(media))).convert('RGB')
        except Exception:
            continue
        med, spread = _poster_border(poster)
        if spread > 6:
            continue                                  # picture runs to the edge: a frame on purpose
        if render is None:
            render = Image.open(render_path).convert('RGB')
        page = _ring(render, box)
        if page is None:
            continue
        diff = max(abs(a - b) for a, b in zip(med, page))
        msg = (f'video {_name(v)!r}: the film background {"#%02X%02X%02X" % med} differs from the page around it '
               f'{"#%02X%02X%02X" % page} by {diff}: the frame shows as a rectangle. Give the slide a solid "bg" of the '
               'film colour or set the film card token to the page colour')
        if diff > 6:
            errors.append(msg)
        elif diff > 2:
            warns.append(msg)
    return errors, warns
