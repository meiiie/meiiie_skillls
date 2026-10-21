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

  geometry     (v5.3) a per-slide fingerprint of what is actually drawn, never a layout label: the boxes of
               every picture/video that is neither a full-bleed ground (>= 85% of the slide) nor a speck
               (< 3%), quantised to a 6x4 grid, plus the 3x3 cell of the text mass (area-weighted centre of
               every text box set at >= 14 pt). Every slide counts, keyframes included: a Morph scene that
               keeps the same split on 3 keyframes IS the same layout three times on screen.
               ERROR  text-left / photo-right (main picture centred right of 55%, >= 12% of the slide, text
                      mass left of the picture) on SPLIT_MAX (4) or more slides; same for photo-left /
                      text-right; one geometry fingerprint on more than GEO_SHARE_MAX of the slides (decks of 10+)
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
SPLIT_MAX = 4          # v5.3: text-left/photo-right (or the mirror) on this many slides fails
GEO_SHARE_MAX = 0.3    # v5.3: one geometry fingerprint on more than this share of slides fails (10+ slides)

ENTR = {1: 'appear', 10: 'fade', 2: 'fly', 42: 'rise', 22: 'wipe', 16: 'split', 53: 'zoom', 21: 'wheel', 17: 'stretch'}
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


def geometry(slide_root):
    """(fingerprint, split) from the rendered geometry of one slide.

    split is 'TL-PR' (text left, picture right), 'PL-TR' (the mirror) or None."""
    boxes = _boxes(slide_root)
    media = [b for b in boxes if b[0] == 'media' and 0.03 <= min(1.0, b[3] * b[4]) < 0.85]
    texts = [b for b in boxes if b[0] == 'text' and b[5] >= 14]
    q = lambda v, n: min(n - 1, max(0, int(v * n + 1e-6)))
    pics = tuple(sorted((q(b[1], 6), q(b[2], 4), q(b[1] + b[3] - 1e-6, 6), q(b[2] + b[4] - 1e-6, 4)) for b in media))
    area = sum(b[3] * b[4] for b in texts)
    if area > 0:
        tx = sum((b[1] + b[3] / 2) * b[3] * b[4] for b in texts) / area
        ty = sum((b[2] + b[4] / 2) * b[3] * b[4] for b in texts) / area
        cell = (q(tx, 3), q(ty, 3))
    else:
        tx = ty = None
        cell = None
    split = None
    main = max(media, key=lambda b: b[3] * b[4], default=None)
    if main is not None and tx is not None and main[3] * main[4] >= 0.12:
        cx = main[1] + main[3] / 2
        if cx >= 0.55 and tx < main[1]:
            split = 'TL-PR'
        elif cx <= 0.45 and tx > main[1] + main[3]:
            split = 'PL-TR'
    # v5.3: a full-bleed plate and a big native drawing are part of the geometry too, so a
    # photo-free diagram slide is not fingerprinted the same as a bare centred title
    bleed = any(b[0] == 'media' and b[3] * b[4] >= 0.85 for b in boxes)
    # a drawing is often many small native parts (iso slabs, bars): take the bounding box of the cluster
    parts = [b for b in boxes if b[0] == 'shape' and 0.003 <= b[3] * b[4] < 0.85]
    graphic = None
    if parts:
        x0, y0 = min(b[1] for b in parts), min(b[2] for b in parts)
        x1, y1 = max(b[1] + b[3] for b in parts), max(b[2] + b[4] for b in parts)
        big = max(b[3] * b[4] for b in parts)
        if big >= 0.08 or (len(parts) >= 3 and (x1 - x0) * (y1 - y0) >= 0.08):
            graphic = (q((x0 + x1) / 2, 3), q((y0 + y1) / 2, 3))
    if bleed or graphic is not None:
        return (pics, cell, 'bleed' if bleed else '', graphic), split
    return (pics, cell), split


MOVING_MIN_AREA = 0.01   # v5.4: a moving layer smaller than 1% of the slide (a dot drifting) is not depth


def _id_boxes(slide_root):
    """{spid: (kind, x, y, w, h, filled_plate)} of top-level shapes."""
    tree = slide_root.find('.//' + P + 'spTree')
    out = {}
    if tree is None:
        return out
    for el in tree:
        tag = el.tag.split('}')[-1]
        nv = el.find('.//' + P + 'cNvPr')
        off, ext = el.find('.//' + A + 'off'), el.find('.//' + A + 'ext')
        if nv is None or off is None or ext is None:
            continue
        is_media = tag == 'pic' or el.find('.//' + A + 'videoFile') is not None
        has_text = any((t.text or '').strip() for t in el.iter(A + 't'))
        sppr = el.find(P + 'spPr')
        textured = el.find('.//' + A + 'blipFill') is not None or (sppr is not None and sppr.find(A + 'gradFill') is not None)
        out[nv.get('id')] = ('media' if is_media else ('text' if has_text else 'shape'),
                             _int(off.get('x')) / EMU_W, _int(off.get('y')) / EMU_H,
                             _int(ext.get('cx')) / EMU_W, _int(ext.get('cy')) / EMU_H, is_media or textured)
    return out


def _moving_targets(slide_root):
    """spids animated by a path, a loop, a pulse or a video play."""
    ids = set()
    timing = slide_root.find(P + 'timing')
    if timing is None:
        return ids
    for ctn in timing.iter(P + 'cTn'):
        cls = ctn.get('presetClass')
        loop = ctn.get('repeatCount') == 'indefinite' or any(c.get('repeatCount') == 'indefinite' for c in ctn.iter(P + 'cTn'))
        if cls == 'path' or cls == 'mediacall' or (cls == 'emph' and loop):
            for t in ctn.iter(P + 'spTgt'):
                ids.add(t.get('spid'))
    return ids


def is_still(slide_root):
    csld = slide_root.find(P + 'cSld')
    return csld is not None and '[still]' in (csld.get('name') or '')


def moving_depth(slide_root, techs):
    """Plate + moving layer + text. v5.4: the plate is a picture, a video or a textured/gradient shape (a flat
    rectangle is not a plate), and the moving layer is another shape of >= 1% of the slide that overlaps it."""
    boxes = _boxes(slide_root)
    ib = _id_boxes(slide_root)
    plates = [(k, b) for k, b in ib.items() if b[0] in ('media', 'shape') and b[3] * b[4] >= 0.3 and b[5]]
    fg_text = any(b[0] == 'text' for b in boxes)
    movers = [ib[i] for i in _moving_targets(slide_root) if i in ib]

    def overlaps(m, p):
        return min(m[1] + m[3], p[1] + p[3]) > max(m[1], p[1]) and min(m[2] + m[4], p[2] + p[4]) > max(m[2], p[2])
    moving = any(m[3] * m[4] >= MOVING_MIN_AREA and any(m is not p and overlaps(m, p) for _, p in plates) for m in movers)
    if not ib:   # no ids to resolve (a synthetic tree): fall back to the technique list
        plate = any(b[0] in ('media', 'shape') and b[3] * b[4] >= 0.3 for b in boxes)
        moving = plate and any(t.startswith('path') or t.endswith('-loop') or t == 'emph:pulse' or t == 'media:video' for t in techs)
    elif any(p[0] == 'media' for _, p in plates) and any(t == 'media:video' for t in techs):
        moving = True   # the plate itself is a playing film
    plate = bool(plates) or not ib
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
    depth = parallax = stills = 0
    scene_sigs = []   # composition is judged per scene cut: a Morph-entered slide is a camera move inside one composition
    geos, splits = Counter(), {'TL-PR': [], 'PL-TR': []}
    for tag, root in slides:
        fp, split = geometry(root)
        geos[fp] += 1
        if split:
            splits[split].append(tag)
        t = effect_techniques(root)
        techs.update(t)
        tr = describe_transition(root)[0]
        trans[tr] += 1
        sig = composition_signature(root)
        sigs.append(sig)
        if tr != 'morph' or not scene_sigs:
            scene_sigs.append((tag, sig))
        d, p = moving_depth(root, t)
        if is_still(root):
            stills += 1
        else:
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
                f'moving depth on {depth}/{n - stills} slides ({stills} still), parallax on {parallax}')
    info.append('variety census: ' + ', '.join(f'{k}×{v}' for k, v in techs.most_common()))
    top_fp, top_fp_n = geos.most_common(1)[0]
    info.append(f'geometry: {len(geos)} distinct picture/text fingerprints on {n} slides (most common on {top_fp_n}); '
                f'text-left/photo-right on {len(splits["TL-PR"])}, photo-left/text-right on {len(splits["PL-TR"])}')
    for kind, tags in splits.items():   # v5.3: hard, whatever the deck size and the --variety mode
        if len(tags) >= SPLIT_MAX:
            label = 'text-left / photo-right' if kind == 'TL-PR' else 'photo-left / text-right'
            errors.append(f'geometry: {label} split on {len(tags)} slides (max {SPLIT_MAX - 1}): {", ".join(t.split()[1] for t in tags[:8])} — '
                          'this is the template look; give those slides another composition (references/pro-craft.md §2, signature-moments.md)')
    if n >= 10 and top_fp_n > GEO_SHARE_MAX * n and top_fp_n >= 4 and (top_fp[0] or top_fp[1]):
        errors.append(f'geometry: one picture/text fingerprint repeats on {top_fp_n}/{n} slides (max {GEO_SHARE_MAX:.0%}): {top_fp}')
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
    moving_n = n - min(stills, n // 4)   # v5.4: declared still pages ("still": true) do not count, up to a quarter
    if stills > n // 4:
        bad.append(f'depth: {stills} slides declare "still" (max {n // 4}, a quarter of the deck)')
    if depth < DEPTH_MIN * moving_n:
        bad.append(f'depth: moving depth (picture/texture plate + a moving layer over it + text) on {depth}/{moving_n} '
                   f'slides (min {DEPTH_MIN:.0%}{f"; {stills} still page(s) excluded" if stills else ""})')
    return errors, warns, info
