"""Variety audit (v5.2): does the deck move and compose like a directed piece, or like one trick repeated?

Measured from the real slide XML (what PowerPoint will play), not from deck.json:

  techniques   every effect node is named by what it LOOKS like: entr:fade, entr:fly, entr:letters (an
               iterate under fade), entr:words, emph:pulse-loop, emph:grow, emph:spin(-loop), path,
               path:loop, path:curve, media:video ... plus the slide transition types.
  share        the most used effect technique as a fraction of all effect nodes.
  composition  a coarse layout signature per scene cut (slides entered by Morph are camera moves inside
               the previous composition and are skipped): dominant picture/video coverage and side, the
               largest plain shape, the cell (3x3) of the largest text, and the text-box count bucket.
               Two cuts with the same signature use the same layout grammar.
  depth        a slide has moving depth when it stacks a background plate (full-bleed picture/video or
               a large shape), something that moves on a path or loops, and foreground text; parallax
               when two or more paths of clearly different lengths play on the slide.

Thresholds for decks of DECK_MIN slides or more (smaller decks scale them down):
  WARN (ERROR with --variety strict)
    - fewer than TECH_MIN distinct effect techniques
    - one effect technique above SHARE_MAX of all effect nodes
    - fewer than TRANS_MIN distinct transition types
    - distinct composition signatures under COMP_MIN of the slides, or the same signature on
      3 consecutive slides
    - fewer than DEPTH_MIN of the slides with moving depth
The thresholds come from references/pro-craft.md (measured Earth deck v5.2, 22 slides: 18 techniques, top entr:fade 28%, 11 transition types,
12/14 composition signatures, moving depth 13/22;
slidewppt.vn reference: fade alone 52% of transitions, which reads as template motion).
"""
import re
from collections import Counter

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = '{%s}' % P_NS
A = '{%s}' % A_NS
EMU_W, EMU_H = 12192000, 6858000

DECK_MIN = 15
TECH_MIN = 10
SHARE_MAX = 0.35
TRANS_MIN = 5
COMP_MIN = 0.6
DEPTH_MIN = 0.2

ENTR = {1: 'appear', 10: 'fade', 2: 'fly', 42: 'rise', 22: 'wipe', 16: 'split', 53: 'zoom', 21: 'wheel'}
EMPH = {6: 'scale', 8: 'spin', 35: 'blink', 32: 'teeter'}
EXIT = {10: 'fade', 2: 'fly', 53: 'zoom', 22: 'wipe'}


def _int(v, d=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return d


def effect_techniques(slide_root):
    """List of technique names, one per effect node on the slide."""
    out = []
    timing = slide_root.find(P + 'timing')
    if timing is None:
        return out
    for ctn in timing.iter(P + 'cTn'):
        cls = ctn.get('presetClass')
        if cls not in ('entr', 'emph', 'exit', 'path', 'mediacall'):
            continue
        pid = _int(ctn.get('presetID'))
        loop = ctn.get('repeatCount') == 'indefinite' or any(
            c.get('repeatCount') == 'indefinite' for c in ctn.iter(P + 'cTn'))
        it = ctn.find('.//' + P + 'iterate')
        if cls == 'entr':
            name = 'entr:' + ENTR.get(pid, f'id{pid}')
            if it is not None:
                name = 'entr:' + ('words' if it.get('type') == 'wd' else 'letters')
        elif cls == 'emph':
            base = EMPH.get(pid, f'id{pid}')
            name = 'emph:' + ('pulse' if base == 'scale' and loop else ('grow' if base == 'scale' else base))
            if loop and base != 'scale':
                name += '-loop'
        elif cls == 'exit':
            name = 'exit:' + EXIT.get(pid, f'id{pid}')
        elif cls == 'path':
            m = ctn.find('.//' + P + 'animMotion')
            d = (m.get('path') if m is not None else '') or ''
            name = 'path:loop' if loop else ('path:curve' if ' C ' in f' {d} ' else 'path')
        else:
            name = 'media:video'
        out.append(name)
    return out


def path_lengths(slide_root):
    lens = []
    for m in slide_root.iter(P + 'animMotion'):
        nums = [float(x) for x in re.findall(r'-?\d*\.?\d+(?:[eE]-?\d+)?', m.get('path') or '')]
        pts = list(zip(nums[0::2], nums[1::2]))
        L = sum(((x1 - x0) * 13.333) ** 2 + ((y1 - y0) * 7.5) ** 2 for (x0, y0), (x1, y1) in zip(pts, pts[1:])) ** 0.5 if len(pts) > 1 else 0
        lens.append(L)
    return lens


def _boxes(slide_root):
    """(kind, x, y, w, h, max_font_pt) of every top-level shape, in slide fractions."""
    tree = slide_root.find('.//' + P + 'spTree')
    out = []
    if tree is None:
        return out
    for el in tree:
        tag = el.tag.split('}')[-1]
        if tag not in ('sp', 'pic', 'grpSp', 'graphicFrame', 'cxnSp'):
            continue
        off = el.find('.//' + A + 'off')
        ext = el.find('.//' + A + 'ext')
        if off is None or ext is None:
            continue
        x, y = _int(off.get('x')) / EMU_W, _int(off.get('y')) / EMU_H
        w, h = _int(ext.get('cx')) / EMU_W, _int(ext.get('cy')) / EMU_H
        sizes = [_int(r.get('sz')) / 100 for r in el.iter(A + 'rPr') if r.get('sz')]
        has_text = any((t.text or '').strip() for t in el.iter(A + 't'))
        is_media = tag == 'pic' or el.find('.//' + A + 'videoFile') is not None
        kind = 'media' if is_media else ('text' if has_text else 'shape')
        out.append((kind, x, y, w, h, max(sizes) if sizes else 0))
    return out


def composition_signature(slide_root):
    boxes = _boxes(slide_root)
    media = [b for b in boxes if b[0] == 'media']
    big = max(media, key=lambda b: b[3] * b[4], default=None)
    if big is None:
        cover, side = 0, '-'
    else:
        area = min(1.0, big[3] * big[4])
        cover = 3 if area >= 0.5 else (2 if area >= 0.15 else 1)
        cx = big[1] + big[3] / 2
        side = 'L' if cx < 0.4 else ('R' if cx > 0.6 else 'C')
    shapes = [b for b in boxes if b[0] == 'shape']
    big_shape = max((b[3] * b[4] for b in shapes), default=0)
    texts = [b for b in boxes if b[0] == 'text']
    lead = max(texts, key=lambda b: b[5], default=None)
    if lead is None:
        cell = '-'
    else:
        cx, cy = lead[1] + lead[3] / 2, lead[2] + lead[4] / 2
        cell = f'{min(2, max(0, int(cx * 3)))}{min(2, max(0, int(cy * 3)))}'
    n = len(texts)
    nb = 'few' if n <= 4 else ('mid' if n <= 10 else 'many')
    shape_b = 'plate' if big_shape >= 0.3 else ('obj' if big_shape >= 0.05 else 'flat')
    return (cover, side, shape_b, cell, nb)


def moving_depth(slide_root, techs):
    boxes = _boxes(slide_root)
    plate = any(b[0] in ('media', 'shape') and b[3] * b[4] >= 0.3 for b in boxes)
    fg_text = any(b[0] == 'text' for b in boxes)
    moving = any(t.startswith('path') or t.endswith('-loop') or t == 'emph:pulse' or t == 'media:video' for t in techs)
    lens = sorted(l for l in path_lengths(slide_root) if l > 0.05)
    parallax = len(lens) >= 2 and lens[-1] >= 1.6 * lens[0]
    return plate and fg_text and moving, parallax


def audit(slides, describe_transition, strict=False):
    """slides: [(tag, slide_root)]. Returns (errors, warns, info)."""
    errors, warns, info = [], [], []
    n = len(slides)
    if n == 0:
        return errors, warns, info
    scale = min(1.0, n / DECK_MIN)
    techs, trans, sigs = Counter(), Counter(), []
    depth = parallax = 0
    scene_sigs = []   # composition is judged per scene cut: a Morph-entered slide is a camera move inside one composition
    for tag, root in slides:
        t = effect_techniques(root)
        techs.update(t)
        tr = describe_transition(root)[0]
        trans[tr] += 1
        sig = composition_signature(root)
        sigs.append(sig)
        if tr != 'morph' or not scene_sigs:
            scene_sigs.append((tag, sig))
        d, p = moving_depth(root, t)
        depth += d
        parallax += p
    total = sum(techs.values())
    top, top_n = (techs.most_common(1)[0] if techs else ('-', 0))
    share = top_n / total if total else 0
    m = len(scene_sigs)
    distinct_sig = len(set(sg for _, sg in scene_sigs))
    runs = [scene_sigs[i][0] for i in range(2, m) if scene_sigs[i][1] == scene_sigs[i - 1][1] == scene_sigs[i - 2][1]]
    info.append(f'variety: {len(techs)} effect techniques over {total} effect nodes (top {top} {share:.0%}); '
                f'{len(trans)} transition types; {distinct_sig}/{m} composition signatures across scene cuts; '
                f'moving depth on {depth}/{n} slides, parallax on {parallax}')
    info.append('variety census: ' + ', '.join(f'{k}×{v}' for k, v in techs.most_common()))
    if n < 8:
        return errors, warns, info
    bad = errors if strict else warns
    need_t = max(4, round(TECH_MIN * scale))
    if len(techs) < need_t:
        bad.append(f'variety: {len(techs)} distinct effect techniques (min {need_t} for {n} slides): '
                   'see references/pro-craft.md, "Motion vocabulary per scene"')
    if total >= 20 and share > SHARE_MAX:
        bad.append(f'variety: {top} is {share:.0%} of all effects (max {SHARE_MAX:.0%}): one trick repeated reads as a template')
    need_tr = max(2, round(TRANS_MIN * scale))
    if len(trans) < need_tr:
        bad.append(f'variety: {len(trans)} transition types (min {need_tr}): choose the transition from the cut grammar in pro-craft.md')
    if m >= 5 and distinct_sig < COMP_MIN * m:
        bad.append(f'composition: {distinct_sig} distinct layout signatures across {m} scene cuts (min {COMP_MIN:.0%}): '
                   'vary scale, side and depth (pro-craft.md, "Composition systems")')
    if runs:
        bad.append(f'composition: the same layout signature on 3 scene cuts in a row ending at {runs[:4]}')
    if depth < DEPTH_MIN * n:
        bad.append(f'depth: moving depth (plate + moving layer + text) on {depth}/{n} slides (min {DEPTH_MIN:.0%})')
    return errors, warns, info
