"""Three-column highlight-walk keyframes.

Groups each role column into a p:grpSp named !!role1-3 (icon/rule/title/kicker/desc),
adds !!hl (glow panel) under the highlighted role, scales that role 1.15
(geometry + font sizes) and dims the others. Role 2 has no icon shape here so a
separate morphing object can stand in for it.

Usage:
  python roles.py PPT_DIR SLIDE.xml --template TEMPLATE.xml [--highlight 1|2|3]
      [--page TEXT] [--title TEXT] [--kick TEXT] [--desc N=TEXT]
      [--instrument-layers NAME,NAME] [--string-layers NAME,NAME]

PPT_DIR is the unpacked ppt directory (it contains slides/). TEMPLATE.xml is a
slide whose object geometry is the rest pose, often the group's first keyframe.
The source slide must already contain !!title, !!frame and the ROLE shape names.
Pass --instrument-layers and --string-layers for extra shapes that should dim
with role 2; leave them empty when the deck has no separate instrument.
"""
import argparse
from pathlib import Path

from lxml import etree

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
NS = {'a': A[1:-1], 'p': P[1:-1]}
E = 914400

# Object names this helper expects on the source slide. Change ROLE to match a
# deck that named the three columns differently. Role 2 omits an icon entry.
ROLE = {
    1: ['@fade2-ic0', '@wipe2-r0', '@float2-t0', '@float2-k0', '@fade2-d0'],
    2: ['@wipe3-r1', '@float3-t1', '@float3-k1', '@fade3-d1'],
    3: ['@fade4-ic2', '@wipe4-r2', '@float4-t2', '@float4-k2', '@fade4-d2'],
}
PART = ['icon', 'rule', 'title', 'kicker', 'desc']
COL_X = {1: 1.45, 2: 5.3, 3: 9.15}
BRIGHT = {'title': 'F6E2B4', 'kicker': 'EBCB86', 'desc': 'F3E6CC'}
MID = {'title': 'D9C29A', 'kicker': 'BFA983', 'desc': 'CDBB98'}
DIM = {'title': '9C8B6E', 'kicker': '8A7B62', 'desc': '9C8B6E'}


def _base(template):
    t = etree.parse(str(template))
    out = {}
    for c in t.iter(P + 'cNvPr'):
        sp = c.getparent().getparent()
        x = sp.find('./p:spPr/a:xfrm', NS)
        if x is None:
            continue
        o, e = x.find('a:off', NS), x.find('a:ext', NS)
        r = sp.find('.//a:rPr[@sz]', NS)
        out[c.get('name')] = (int(o.get('x')), int(o.get('y')), int(e.get('cx')), int(e.get('cy')), int(r.get('sz')) if r is not None else None)
    return out


def nm(sp):
    return sp.find('.//p:cNvPr', NS)


def build(fn, ppt_dir, template, hl=None, descs=None, page=None, title=None, kick=None,
          instrument_layers=(), string_layers=()):
    W = Path(ppt_dir)
    base = _base(template)
    f = W / 'slides' / fn
    t = etree.parse(str(f))
    tree = t.getroot().find('.//p:spTree', NS)
    byname = {nm(sp).get('name'): sp for sp in tree if nm(sp) is not None}
    nid = 200
    for r, names in ROLE.items():
        if f'!!role{r}' in byname:
            continue
        parts = [byname[n] for n in names]
        idx = list(tree).index(parts[0])
        g = etree.Element(P + 'grpSp')
        g.append(etree.fromstring(f'<p:nvGrpSpPr xmlns:p="{NS["p"]}"><p:cNvPr id="{nid}" name="!!role{r}"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'))
        nid += 1
        g.append(etree.fromstring(f'<p:grpSpPr xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'))
        labels = PART if r != 2 else PART[1:]
        for sp, lab in zip(parts, labels):
            nm(sp).set('name', f'role{r} {lab}')
            g.append(sp)
        tree.insert(idx, g)
    t.write(str(f), xml_declaration=True, encoding='UTF-8', standalone=True)
    # second pass: styling, scaling, hl, bbox
    t = etree.parse(str(f))
    tree = t.getroot().find('.//p:spTree', NS)
    byname = {c.get('name'): c.getparent().getparent() for c in t.iter(P + 'cNvPr')}
    if descs:
        for r, d in descs.items():
            sp = byname[f'role{r} desc']
            runs = sp.findall('.//a:r', NS)
            runs[0].find('a:t', NS).text = d
            for x in runs[1:]:
                x.getparent().remove(x)
    for r in (1, 2, 3):
        g = byname[f'!!role{r}']
        state = 'bright' if hl == r else ('dim' if hl else 'mid')
        pal = {'bright': BRIGHT, 'mid': MID, 'dim': DIM}[state]
        s = 1.15 if state == 'bright' else 1.0
        x0 = COL_X[r]
        y0 = 2.45 if r == 3 else 2.75
        ty = (4.715 - (4.85 - y0) * s) if state == 'bright' else y0  # scaled role: rule lands at 4.715 for every column
        for sp in g:
            c = sp.find('.//p:cNvPr', NS)
            if c is None or c.getparent().tag == P + 'nvGrpSpPr':
                continue
            lab = c.get('name').split(' ', 1)[1]
            o, e = sp.find('./p:spPr/a:xfrm/a:off', NS), sp.find('./p:spPr/a:xfrm/a:ext', NS)
            bx, by, bw, bh, bsz = base[ROLE[r][(PART if r != 2 else PART[1:]).index(lab)]]
            if lab == 'desc':
                bh, bw = max(bh, int(1.0 * E)), (int(3.2 * E) if s > 1 else bw)
            o.set('x', str(int(x0 * E + (bx - x0 * E) * s)))
            o.set('y', str(int(ty * E + (by - y0 * E) * s)))
            e.set('cx', str(int(bw * s)))
            e.set('cy', str(int(bh * s)))
            if lab == 'icon' and state == 'bright' and int(o.get('y')) < int(2.25 * E):
                o.set('y', str(int(2.25 * E)))
            if lab == 'icon':
                blip = sp.find('.//a:blip', NS)
                for a in blip.findall('a:alphaModFix', NS):
                    blip.remove(a)
                amt = {'bright': None, 'mid': '70000', 'dim': '35000'}[state]
                if amt:
                    blip.insert(0, etree.Element(A + 'alphaModFix', amt=amt))
            elif lab == 'rule':
                clr = sp.find('.//a:ln//a:srgbClr', NS)
                if clr is not None:
                    for a in clr.findall('a:alpha', NS):
                        clr.remove(a)
                    if state != 'bright':
                        etree.SubElement(clr, A + 'alpha', val='45000' if state == 'dim' else '75000')
            else:
                for rp in sp.iter(A + 'rPr', A + 'endParaRPr'):
                    if rp.get('sz') is None or bsz is None:
                        continue
                    rp.set('sz', str(int(round(int(bsz) * (1.0 if lab == 'desc' else s) / 100.0)) * 100))
                    clr = rp.find('.//a:srgbClr', NS)
                    if clr is not None:
                        clr.set('val', pal[lab])
        # template font sizes remembered in a custom attr would be invalid XML; store in cNvPr descr of group
        kids = [k for k in g if k.find('./p:spPr/a:xfrm', NS) is not None]
        xs = [(int(k.find('./p:spPr/a:xfrm/a:off', NS).get('x')), int(k.find('./p:spPr/a:xfrm/a:off', NS).get('y')),
               int(k.find('./p:spPr/a:xfrm/a:ext', NS).get('cx')), int(k.find('./p:spPr/a:xfrm/a:ext', NS).get('cy'))) for k in kids]
        L, T = min(a[0] for a in xs), min(a[1] for a in xs)
        R, B = max(a[0] + a[2] for a in xs), max(a[1] + a[3] for a in xs)
        gx = g.find('./p:grpSpPr/a:xfrm', NS)
        for tag, vals in (('a:off', (L, T)), ('a:chOff', (L, T))):
            gx.find(tag, NS).set('x', str(vals[0]))
            gx.find(tag, NS).set('y', str(vals[1]))
        for tag in ('a:ext', 'a:chExt'):
            gx.find(tag, NS).set('cx', str(R - L))
            gx.find(tag, NS).set('cy', str(B - T))
    # Dim optional extra shapes that stand in for role 2's icon.
    for n in instrument_layers:
        blip = byname[n].find('.//a:blip', NS)
        for a in blip.findall('a:alphaModFix', NS):
            blip.remove(a)
        amt = None if hl == 2 else ('35000' if hl else '70000')
        if amt:
            blip.insert(0, etree.Element(A + 'alphaModFix', amt=amt))
    for n in string_layers:
        sp = byname[n]
        for clr in sp.findall('.//a:srgbClr', NS):
            for a in clr.findall('a:alpha', NS):
                clr.remove(a)
            if hl != 2:
                etree.SubElement(clr, A + 'alpha', val='35000' if hl else '70000')
    # !!hl glow panel behind the highlighted role
    if '!!hl' in byname:
        tree.remove(byname['!!hl'])
    if hl:
        x0 = COL_X[hl] - 0.15
        w = 3.2 * 1.15 + 0.3
        y = 2.15
        h = 7.0 - y
        hlx = etree.fromstring(
            f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="190" name="!!hl"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{int(x0*E)}" y="{int(y*E)}"/><a:ext cx="{int(w*E)}" cy="{int(h*E)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 4000"/></a:avLst></a:prstGeom>'
            '<a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="EBCB86"><a:alpha val="4000"/></a:srgbClr></a:gs><a:gs pos="100000"><a:srgbClr val="EBCB86"><a:alpha val="20000"/></a:srgbClr></a:gs></a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>'
            '<a:ln w="12700"><a:solidFill><a:srgbClr val="D9B26A"><a:alpha val="60000"/></a:srgbClr></a:solidFill></a:ln></p:spPr></p:sp>'
        )
        frame = byname['!!frame']
        tree.insert(list(tree).index(frame) + 1, hlx)

    def settext(name, text):
        sp = byname[name]
        runs = sp.findall('.//a:r', NS)
        runs[0].find('a:t', NS).text = text
        for x in runs[1:]:
            x.getparent().remove(x)

    if page:
        settext([k for k in byname if k.startswith('Text ')][0], page)
    if title:
        settext('!!title', title)
    if kick:
        settext('!!kick', kick)
    for name in ('!!title',):
        for rp in byname[name].iter(A + 'rPr'):
            c = rp.find('.//a:srgbClr', NS)
            if c is not None:
                c.set('val', 'D9C29A')
    t.write(str(f), xml_declaration=True, encoding='UTF-8', standalone=True)


def _layers(value):
    if not value:
        return ()
    return tuple(part for part in value.split(',') if part)


def _descs(items):
    if not items:
        return None
    out = {}
    for item in items:
        key, value = item.split('=', 1)
        out[int(key)] = value
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build three-column highlight-walk states on one unpacked slide.')
    parser.add_argument('ppt_dir', help='unpacked ppt directory (contains slides/)')
    parser.add_argument('slide', help='slide filename inside slides/, e.g. slide9.xml')
    parser.add_argument('--template', required=True, help='slide XML used as the rest-pose geometry')
    parser.add_argument('--highlight', type=int, choices=(1, 2, 3), help='role column to brighten; omit to keep all mid')
    parser.add_argument('--page', help='page label written into the first shape named "Text ..."')
    parser.add_argument('--title', help='replacement text for !!title')
    parser.add_argument('--kick', help='replacement text for !!kick')
    parser.add_argument('--desc', action='append', default=[], metavar='N=TEXT', help='replacement description for role N')
    parser.add_argument('--instrument-layers', default='', help='comma-separated picture shapes that dim with role 2')
    parser.add_argument('--string-layers', default='', help='comma-separated line shapes that dim with role 2')
    args = parser.parse_args(argv)
    build(
        args.slide, args.ppt_dir, args.template, hl=args.highlight, descs=_descs(args.desc),
        page=args.page, title=args.title, kick=args.kick,
        instrument_layers=_layers(args.instrument_layers), string_layers=_layers(args.string_layers),
    )


if __name__ == '__main__':
    main()
