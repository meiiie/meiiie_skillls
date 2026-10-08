"""Build a 16:9 motion deck from a JSON spec, with named shapes ready for Morph.

  python build_deck.py deck.json --out deck/build.pptx [--base template.pptx]

Why: any agent (no slide service needed) can write a spec, render it, look, fix, rebuild.
Keyframe runs are written as "from": "prev" + small changes, so a 4-slide motion stays consistent.

Spec (units: inches on a 13.333 x 7.5 canvas; colours "#RRGGBB" or a palette key):
{
  "palette": {"bg": "#0E0A07", "ink": "#F1E4C8", "gold": "#C79A3B"},
  "fonts":   {"display": "Cormorant Garamond", "body": "Be Vietnam Pro"},
  "slides": [
    {"id": "s1", "bg": "bg", "notes": "Lời đọc...\\n[ngừng 2 giây]",
     "shapes": [
       {"type": "image", "name": "!!photo", "path": "assets/03_dan_day.jpg", "x": 0, "y": 0, "w": 13.333, "h": 7.5,
        "fit": "cover", "focus": [0.5, 0.4], "alpha": 1.0},
       {"type": "rect", "name": "!!veil", "x": 0, "y": 0, "w": 13.333, "h": 7.5, "fill": "#000000", "alpha": 0.55},
       {"type": "rect", "name": "scrim", "x": 0, "y": 4, "w": 13.333, "h": 3.5,
        "gradient": [["#000000", 0.0, 0], ["#000000", 0.85, 100]], "angle": 90},
       {"type": "text", "name": "!!title", "text": "Ca trù", "x": 0.9, "y": 5.2, "w": 8, "h": 1.3,
        "font": "display", "size": 60, "color": "ink", "align": "l", "anchor": "b", "spacing": 0, "line": 0.95},
       {"type": "text", "name": "@fade1-kick", "text": ["Dòng 1", {"text": "Dòng 2", "size": 18, "color": "gold"}], ...},
       {"type": "line", "name": "!!str1", "x1": 6, "y1": 0.5, "x2": 6, "y2": 7, "color": "gold", "width": 1.25},
       {"type": "ellipse", "name": "!!dot0", "x": 1, "y": 1, "w": 0.2, "h": 0.2, "fill": "gold"}
     ]},
    {"id": "s2", "from": "prev", "notes": "...",
     "set":  {"!!photo": {"x": -1.5, "y": -0.8, "w": 16.3, "h": 9.2}, "!!veil": {"alpha": 0.2}},
     "drop": ["@fade1-kick"],
     "add":  [{"type": "text", "name": "@float1-cap", "text": "Đàn đáy — 3 dây", ...}]}
  ]
}
Shape keys: name (required for anything that moves: "!!x" = Morph pair, "@fade1-x" entrance),
rot (deg), alpha (0..1), line_color/line_width for rect/ellipse outlines, radius (0..0.5) for rounded rect.
Text keys: text (string | list of paragraphs; a paragraph may be a dict with its own text/size/
color/font/bold/italic), font (palette key in "fonts" or a family), size (pt), bold, italic, color,
align l|c|r, anchor t|m|b, spacing (pt letter spacing), line (line-spacing multiple), caps.
Image keys: path, fit cover|contain|stretch (default cover: crops instead of stretching), focus [fx, fy].
"from": "prev" | "<id>" copies that slide's shapes and bg; "set" overrides keys by name;
"drop" removes names; "add" appends; "front": [names] moves names to the top of the z-order.
After building: ooxml.py unpack -> motion.py -> ooxml.py pack -> check_deck.py -> render.sh.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

W, H = 13.333, 7.5


class Spec:
    def __init__(self, data, root):
        self.pal = data.get('palette', {})
        self.fonts = data.get('fonts', {})
        self.root = root

    def color(self, c):
        c = self.pal.get(c, c)
        if not (isinstance(c, str) and c.startswith('#') and len(c) == 7):
            raise SystemExit(f'bad colour {c!r}: use "#RRGGBB" or a palette key')
        return c[1:].upper()

    def font(self, f):
        return self.fonts.get(f, f)

    def path(self, p):
        q = Path(p)
        return q if q.is_absolute() else (self.root / q)


def resolve(slides):
    """Expand from/set/drop/add into full shape lists."""
    out, by_id = [], {}
    for i, s in enumerate(slides):
        s = copy.deepcopy(s)
        src = s.get('from')
        if src:
            base = out[-1] if src == 'prev' else by_id.get(src)
            if base is None:
                raise SystemExit(f'slide {i + 1}: "from": {src!r} not found')
            shapes = copy.deepcopy(base['shapes'])
            s.setdefault('bg', base.get('bg'))
            names = [sh.get('name') for sh in shapes]
            for n, over in s.get('set', {}).items():
                if n not in names:
                    raise SystemExit(f'slide {i + 1}: set {n!r} — no shape with that name in the source slide')
                shapes[names.index(n)].update(over)
            drop = set(s.get('drop', []))
            missing = drop - set(names)
            if missing:
                raise SystemExit(f'slide {i + 1}: drop {sorted(missing)} — not in the source slide')
            shapes = [sh for sh in shapes if sh.get('name') not in drop]
            shapes += s.get('add', [])
            s['shapes'] = shapes
        for n in s.get('front', []):
            idx = [k for k, sh in enumerate(s['shapes']) if sh.get('name') == n]
            for k in idx:
                s['shapes'].append(s['shapes'].pop(k))
        s.setdefault('shapes', [])
        names = [sh.get('name') for sh in s['shapes'] if sh.get('name', '').startswith('!!')]
        dup = {n for n in names if names.count(n) > 1}
        if dup:
            raise SystemExit(f'slide {i + 1}: duplicate !! names {sorted(dup)} (Morph pairs by name: must be unique per slide)')
        out.append(s)
        if s.get('id'):
            by_id[s['id']] = s
    return out


def set_alpha_fill(shape, hexcol, alpha):
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(hexcol)
    if alpha is not None and alpha < 1:
        clr = shape.fill._xPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
        a = etree.SubElement(clr, qn('a:alpha'))
        a.set('val', str(int(alpha * 100000)))


def set_gradient(shape, stops, angle, spec):
    spPr = shape.fill._xPr
    for tag in ('a:solidFill', 'a:noFill', 'a:gradFill', 'a:blipFill', 'a:pattFill'):
        for e in spPr.findall(qn(tag)):
            spPr.remove(e)
    grad = etree.Element(qn('a:gradFill'), rotWithShape='1')
    lst = etree.SubElement(grad, qn('a:gsLst'))
    for st in stops:  # [colour, alpha 0..1, position 0..100]
        col, alpha, pos = st[0], st[1], st[2]
        gs = etree.SubElement(lst, qn('a:gs'), pos=str(int(pos * 1000)))
        c = etree.SubElement(gs, qn('a:srgbClr'), val=spec.color(col))
        etree.SubElement(c, qn('a:alpha'), val=str(int(alpha * 100000)))
    etree.SubElement(grad, qn('a:lin'), ang=str(int(angle * 60000)), scaled='0')
    # gradFill must come right after the geometry element
    geom = spPr.find(qn('a:prstGeom'))
    geom.addnext(grad)


def no_line(shape):
    shape.line.fill.background()


def add_box(slide, sh, spec, kind):
    geo = {'rect': MSO_SHAPE.RECTANGLE, 'ellipse': MSO_SHAPE.OVAL}[kind]
    if kind == 'rect' and sh.get('radius'):
        geo = MSO_SHAPE.ROUNDED_RECTANGLE
    shp = slide.shapes.add_shape(geo, Inches(sh['x']), Inches(sh['y']), Inches(sh['w']), Inches(sh['h']))
    if kind == 'rect' and sh.get('radius'):
        shp.adjustments[0] = sh['radius']
    if sh.get('gradient'):
        set_gradient(shp, sh['gradient'], sh.get('angle', 90), spec)
    elif sh.get('fill'):
        set_alpha_fill(shp, spec.color(sh['fill']), sh.get('alpha'))
    else:
        shp.fill.background()
    if sh.get('line_color'):
        shp.line.color.rgb = RGBColor.from_string(spec.color(sh['line_color']))
        shp.line.width = Pt(sh.get('line_width', 1))
    else:
        no_line(shp)
    shp.shadow.inherit = False
    if shp.has_text_frame:
        shp.text_frame.text = ''
    return shp


def add_line(slide, sh, spec):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(sh['x1']), Inches(sh['y1']), Inches(sh['x2']), Inches(sh['y2']))
    ln.line.color.rgb = RGBColor.from_string(spec.color(sh.get('color', '#FFFFFF')))
    ln.line.width = Pt(sh.get('width', 1))
    if sh.get('alpha') is not None and sh['alpha'] < 1:
        clr = ln.line._get_or_add_ln().find(qn('a:solidFill')).find(qn('a:srgbClr'))
        etree.SubElement(clr, qn('a:alpha'), val=str(int(sh['alpha'] * 100000)))
    return ln


def add_image(slide, sh, spec):
    p = spec.path(sh['path'])
    if not p.exists():
        raise SystemExit(f'image not found: {p}')
    pic = slide.shapes.add_picture(str(p), Inches(sh['x']), Inches(sh['y']), Inches(sh['w']), Inches(sh['h']))
    fit = sh.get('fit', 'cover')
    iw, ih = Image.open(p).size
    box = sh['w'] / sh['h']
    img = iw / ih
    fx, fy = sh.get('focus', [0.5, 0.5])
    if fit == 'cover' and abs(img - box) > 0.005:
        if img > box:  # too wide: crop left/right
            keep = box / img
            left = (1 - keep) * fx
            pic.crop_left, pic.crop_right = left, 1 - keep - left
        else:
            keep = img / box
            top = (1 - keep) * fy
            pic.crop_top, pic.crop_bottom = top, 1 - keep - top
    elif fit == 'contain' and abs(img - box) > 0.005:
        if img > box:
            nh = sh['w'] / img
            pic.top = Inches(sh['y'] + (sh['h'] - nh) / 2)
            pic.height = Inches(nh)
        else:
            nw = sh['h'] * img
            pic.left = Inches(sh['x'] + (sh['w'] - nw) / 2)
            pic.width = Inches(nw)
    if sh.get('alpha') is not None and sh['alpha'] < 1:
        blip = pic._element.find('.//' + qn('a:blip'))
        etree.SubElement(blip, qn('a:alphaModFix'), amt=str(int(sh['alpha'] * 100000)))
    return pic


def style_run(run, d, spec, base):
    f = run.font
    f.name = spec.font(d.get('font', base.get('font', 'body')))
    f.size = Pt(d.get('size', base.get('size', 20)))
    f.bold = d.get('bold', base.get('bold', False))
    f.italic = d.get('italic', base.get('italic', False))
    f.color.rgb = RGBColor.from_string(spec.color(d.get('color', base.get('color', '#FFFFFF'))))
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):  # same family for every script slot (Vietnamese renders via latin)
        e = rPr.find(qn(tag))
        if e is None:
            e = etree.SubElement(rPr, qn(tag))
        e.set('typeface', f.name)
    sp = d.get('spacing', base.get('spacing'))
    if sp:
        rPr.set('spc', str(int(sp * 100)))
    if d.get('caps', base.get('caps')):
        rPr.set('cap', 'all')
    a = d.get('alpha', base.get('alpha'))
    if a is not None and a < 1:
        clr = rPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
        etree.SubElement(clr, qn('a:alpha'), val=str(int(a * 100000)))


def add_text(slide, sh, spec):
    tb = slide.shapes.add_textbox(Inches(sh['x']), Inches(sh['y']), Inches(sh['w']), Inches(sh['h']))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
        setattr(tf, side, 0)
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[sh.get('anchor', 't')]
    paras = sh['text'] if isinstance(sh['text'], list) else [sh['text']]
    for i, para in enumerate(paras):
        d = para if isinstance(para, dict) else {'text': para}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[d.get('align', sh.get('align', 'l'))]
        if sh.get('line') or d.get('line'):
            p.line_spacing = d.get('line', sh.get('line'))
        if d.get('space_before'):
            p.space_before = Pt(d['space_before'])
        runs = d.get('runs') or [d]
        for rd in runs:
            r = p.add_run()
            r.text = rd.get('text', '')
            style_run(r, {**{k: v for k, v in d.items() if k not in ('text', 'runs')}, **rd}, spec, sh)
    return tb


def build(data, root, base=None):
    spec = Spec(data, root)
    prs = Presentation(base) if base else Presentation()
    if not base:
        prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[-1]
    slides = resolve(data['slides'])
    for n, s in enumerate(slides, 1):
        sl = prs.slides.add_slide(layout)
        for ph in list(sl.placeholders):
            ph._element.getparent().remove(ph._element)
        bg = s.get('bg')
        if bg:
            f = sl.background.fill
            f.solid()
            f.fore_color.rgb = RGBColor.from_string(spec.color(bg))
        for sh in s['shapes']:
            t = sh.get('type')
            if t == 'image':
                obj = add_image(sl, sh, spec)
            elif t == 'text':
                obj = add_text(sl, sh, spec)
            elif t in ('rect', 'ellipse'):
                obj = add_box(sl, sh, spec, t)
            elif t == 'line':
                obj = add_line(sl, sh, spec)
            else:
                raise SystemExit(f'slide {n}: unknown shape type {t!r}')
            if sh.get('name'):
                obj.name = sh['name']
            if sh.get('rot'):
                obj.rotation = sh['rot']
        if s.get('notes'):
            sl.notes_slide.notes_text_frame.text = s['notes']
        else:
            sl.notes_slide  # create an empty notes page so notes-set can fill it later
    return prs, len(slides)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--out', required=True)
    ap.add_argument('--base', help='optional .pptx whose masters/theme to reuse (its slides are kept; usually pass an empty one)')
    a = ap.parse_args(argv)
    sp = Path(a.spec)
    data = json.loads(sp.read_text(encoding='utf-8'))
    prs, n = build(data, sp.parent.resolve(), a.base)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    prs.save(a.out)
    print(f'built {n} slides -> {a.out}')
    print('NEXT: ooxml.py unpack -> motion.py -> ooxml.py pack -> check_deck.py -> render.sh, then LOOK at the contact sheet')


if __name__ == '__main__':
    sys.exit(main())
