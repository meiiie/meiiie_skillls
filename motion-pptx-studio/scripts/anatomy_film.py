"""Signature moment from an Anatomy figure: MP4 film + poster + an editable PowerPoint version.

Anatomy (https://skills.wheresryan.sh/anatomy, MIT, github.com/wheresryan22/anatomy) draws a technical idea as a
real isometric machine of many small solid parts (its rule: "the object is the explanation"). This wrapper
renders a figure MODULE frame by frame with Anatomy's own kit and CSS in headless Chrome, encodes the film, and
converts the poster frame into native freeform shapes (deck.json `poly`/`ellipse` in one group) so the slide
still shows the machine in Google Slides, Keynote, print, LibreOffice, or when the video does not play.

  bash $S/setup_anatomy.sh                                   # once: clones Anatomy, checks node/chrome/ffmpeg
  python3 $S/anatomy_film.py WORK/design/anatomy/line.mjs --name haiphong-line --work WORK \
          --region 0.5,1.9,12.3,4.3 [--fps 25] [--scale 1.25] [--group-name '!!line'] [--max-shapes 4000]
  -> WORK/assets/film/<name>.mp4            H.264 yuv420p, 1920 px wide (insert as a `video` shape)
     WORK/assets/film/<name>.poster.png     the poster frame (the video's poster, the static render)
     WORK/assets/film/<name>.shapes.json    {"type": "group", "name": ..., "shapes": [poly...]} for deck.json
     WORK/assets/film/<name>/film.json      frames, fps, anchors (screen points the module exported, in
                                            inches on the slide after --region) for labels set as slide text
Write the module by the recipe in references/signature-moments.md §2 (bench, stations, a clock, paint back
to front, words outside the drawing). Look at the contact strip it prints before you use the film.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# v5.3.1: encode BT.709 limited range and SAY so, or players guess (BT.601 vs 709) and a white or blue film
# card no longer matches the page it sits on (references/signature-moments.md, "Film and page colour")
COLOUR_TAGS = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']

HERE = Path(__file__).resolve().parent


def css_hex(c):
    if not c:
        return None
    c = c.strip()
    if c.startswith('#'):
        return c.upper() if len(c) == 7 else '#' + ''.join(ch * 2 for ch in c[1:4]).upper()
    m = re.match(r'rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\)', c)
    if not m:
        return None
    return '#%02X%02X%02X' % tuple(int(round(float(v))) for v in m.groups()[:3])


def css_alpha(c):
    m = re.match(r'rgba\([^)]*[,\s/]([\d.]+)\)$', (c or '').strip())
    return float(m.group(1)) if m else 1.0


def simplify(pts, eps=0.15):
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    return out


def to_fragment(shapes_doc, region, name, min_pt=0.35, max_shapes=4000):
    """poster-shapes.json (viewBox px) -> one build_deck group (inches)."""
    W, H = shapes_doc['width'], shapes_doc['height']
    x0, y0, rw, rh = region
    s = min(rw / W, rh / H)
    ox, oy = x0 + (rw - W * s) / 2, y0 + (rh - H * s) / 2
    kids = []
    for i, sh in enumerate(shapes_doc['shapes']):
        fill, stroke = css_hex(sh.get('fill')), css_hex(sh.get('stroke'))
        fa = (sh.get('fillOpacity', 1) or 0) * css_alpha(sh.get('fill'))
        sa = (sh.get('strokeOpacity', 1) or 0) * css_alpha(sh.get('stroke'))
        sw = sh.get('strokeWidth', 0) or 0
        if fill and fa < 0.03:
            fill = None
        if stroke and (sa < 0.03 or sw <= 0):
            stroke = None
        if not fill and not stroke:
            continue
        k = {'name': f'{name.strip("!")}-{i}'}
        if sh['kind'] == 'circle':
            r = sh['r'] * s
            if r <= 0:
                continue
            k.update(type='ellipse', x=round(ox + sh['cx'] * s - r, 4), y=round(oy + sh['cy'] * s - r, 4), w=round(2 * r, 4), h=round(2 * r, 4))
        else:
            pts = simplify([[round(ox + px * s, 4), round(oy + py * s, 4)] for px, py in sh['pts']], eps=0.002)
            if len(pts) < 2 or (fill and len(pts) < 3):
                continue
            k.update(type='poly', points=pts, closed=bool(sh.get('closed') or fill))
        if fill:
            k['fill'] = fill
            if fa < 0.99:
                k['alpha'] = round(fa, 3)
        if stroke:
            k['line_color'] = stroke
            k['line_width'] = round(max(min_pt, sw * s * 72), 2)
            if sa < 0.99:
                k['line_alpha'] = round(sa, 3)
        kids.append(k)
    if len(kids) > max_shapes:
        raise SystemExit(f'{len(kids)} shapes > --max-shapes {max_shapes}: simplify the figure or raise the limit '
                         f'(PowerPoint handles a few thousand freeforms; LibreOffice renders them slowly)')
    return {'type': 'group', 'name': name, 'shapes': kids}, (ox, oy, s)


# v5.3.1 figure audit (references/signature-moments.md, "Density and contrast"). The VinFast proof's first battery pack
# had 69 solids, filled ~45 % of its frame and read as dark-on-dark; these numbers make that visible at film time.
MIN_SOLIDS, MIN_FILL_W, MIN_FILL_AREA = 120, 0.70, 0.40
MIN_LINE_CONTRAST, MIN_FACE_CONTRAST = 4.5, 2.2   # WCAG ratios against the card (faces: dark cards only)


def _lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def figure_audit(poster_png, poster_svg=None):
    """{'solids', 'fill_w', 'fill_area', 'line_contrast', 'face_contrast', 'warnings'} from the poster frame."""
    from PIL import Image
    im = Image.open(poster_png).convert('RGB')
    w, h = im.size
    sm = im.resize((max(1, w // 4), max(1, h // 4)))
    W, H = sm.size
    px = sm.load()
    border = [px[x, y] for x in range(W) for y in (0, H - 1)] + [px[x, y] for y in range(H) for x in (0, W - 1)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))
    fig = [(x, y) for y in range(H) for x in range(W) if max(abs(px[x, y][i] - bg[i]) for i in range(3)) > 14]
    out = {'bg': '#%02X%02X%02X' % bg, 'warnings': []}
    if fig:
        xs, ys = [p[0] for p in fig], [p[1] for p in fig]
        out['fill_w'] = round((max(xs) - min(xs) + 1) / W, 3)
        out['fill_area'] = round((max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1) / (W * H), 3)
        ratios = sorted(_ratio(px[x, y], bg) for x, y in fig)
        out['face_contrast'] = round(ratios[len(ratios) // 2], 2)
        full = im.load()   # thin edges vanish in the downscale: measure them at full size
        x0, x1, y0, y1 = min(xs) * 4, (max(xs) + 1) * 4, min(ys) * 4, (max(ys) + 1) * 4
        step = max(1, int(((x1 - x0) * (y1 - y0) / 400000) ** 0.5))
        fr = sorted(_ratio(full[x, y], bg) for y in range(y0, min(h, y1), step) for x in range(x0, min(w, x1), step)
                    if max(abs(full[x, y][i] - bg[i]) for i in range(3)) > 14)
        out['line_contrast'] = round(fr[int(len(fr) * 0.97)], 2) if fr else 1.0
    else:
        out.update(fill_w=0, fill_area=0, face_contrast=1, line_contrast=1)
    if poster_svg and Path(poster_svg).is_file():
        out['solids'] = Path(poster_svg).read_text(encoding='utf-8', errors='replace').count('iso-solid')
    if out.get('solids') is not None and out['solids'] < MIN_SOLIDS:
        out['warnings'].append(f"{out['solids']} solids < {MIN_SOLIDS}: a signature figure is a Hero (80-150 parts; Anatomy's "
                               'desk computer has ~110 solids). Add the parts a real one has: fasteners, cabinets, cables, racks')
    if out['fill_w'] < MIN_FILL_W or out['fill_area'] < MIN_FILL_AREA:
        out['warnings'].append(f"the figure fills {out['fill_w']:.0%} of the frame width / {out['fill_area']:.0%} of its area "
                               f'(want >= {MIN_FILL_W:.0%} / {MIN_FILL_AREA:.0%}): tighten fitProjection points to the assembled '
                               'state, cut explode heights, choose an azimuth that lays the long axis across the frame')
    if out['line_contrast'] < MIN_LINE_CONTRAST:
        out['warnings'].append(f"edges reach only {out['line_contrast']}:1 against the card (want >= {MIN_LINE_CONTRAST}:1): "
                               'lift --anatomy-hi / --anatomy-mid, or raise --anatomy-weight')
    if _lum(bg) < 0.2 and out['face_contrast'] < MIN_FACE_CONTRAST:   # light cards keep Anatomy's white faces
        out['warnings'].append(f"faces sit at {out['face_contrast']}:1 against the card (want >= {MIN_FACE_CONTRAST}:1): "
                               'on a dark card lift --anatomy-top and the shade ramp, on a light card darken the shades')
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('figure')
    ap.add_argument('--name', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--region', default='0.5,1.6,12.33,4.6', help='x,y,w,h in inches where the film sits on the slide')
    ap.add_argument('--fps', type=int, default=25)
    ap.add_argument('--scale', type=float, default=1.25)
    ap.add_argument('--width', type=int, default=1920, help='MP4 width in px')
    ap.add_argument('--group-name')
    ap.add_argument('--max-shapes', type=int, default=4000)
    ap.add_argument('--anatomy')
    ap.add_argument('--poster-only', action='store_true')
    a = ap.parse_args(argv)
    if not Path(a.figure).is_file():   # v5.7.1: say so instead of node's 'Cannot find module'
        raise SystemExit(f'figure not found: {a.figure} (was the .mjs written?)')
    work = Path(a.work).resolve()
    out = work / 'assets' / 'film'
    tmp = out / a.name
    out.mkdir(parents=True, exist_ok=True)
    node = shutil.which('node')
    if not node:
        raise SystemExit('node not found: install Node >= 20.10 (bash setup_anatomy.sh checks everything)')
    cmd = [node, str(HERE / 'anatomy' / 'film.mjs'), str(Path(a.figure).resolve()), '--out', str(tmp), '--fps', str(a.fps), '--scale', str(a.scale)]
    if a.anatomy:
        cmd += ['--anatomy', a.anatomy]
    if a.poster_only:
        cmd.append('--only-poster')
    r = subprocess.run(cmd)
    if r.returncode == 3:
        raise SystemExit('film.mjs: the figure module has a mistake (FIGURE ERROR above); fix the .mjs, setup is fine')
    if r.returncode:
        raise SystemExit(f'film.mjs failed ({r.returncode}); if node, Chrome or the kit is missing run bash {HERE}/setup_anatomy.sh')
    meta = json.loads((tmp / 'film.json').read_text())
    mp4 = out / f'{a.name}.mp4'
    if not a.poster_only:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', str(tmp / 'frames/f%05d.png'),
                        '-vf', f'scale={a.width}:-2:flags=lanczos:out_color_matrix=bt709:out_range=tv', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
                        '-pix_fmt', 'yuv420p', *COLOUR_TAGS, '-movflags', '+faststart', str(mp4)], check=True)
        strip = out / f'{a.name}.strip.jpg'
        step = max(1, meta['frames'] // 8)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(mp4), '-vf',
                        f"select='not(mod(n\\,{step}))',scale=640:-1,tile=2x4", '-frames:v', '1', str(strip)], check=True)
        shutil.rmtree(tmp / 'frames', ignore_errors=True)
    shutil.copy(tmp / 'poster.png', out / f'{a.name}.poster.png')
    region = [float(v) for v in a.region.split(',')]
    frag, (ox, oy, s) = to_fragment(json.loads((tmp / 'poster-shapes.json').read_text()), region, a.group_name or f'!!{a.name}', max_shapes=a.max_shapes)
    (out / f'{a.name}.shapes.json').write_text(json.dumps(frag), encoding='utf-8')
    if not meta.get('anchors') and 'anchors' in Path(a.figure).read_text(encoding='utf-8', errors='replace'):
        print('WARN the figure mentions anchors but none were exported: check the anchors key (object or (t) => object)')
    meta['anchors_in'] = {k: [round(ox + v[0] * s, 3), round(oy + v[1] * s, 3)] for k, v in meta.get('anchors', {}).items()}
    meta['region'] = region
    meta['fit'] = {'x': round(ox, 3), 'y': round(oy, 3), 'w': round(meta['width'] * s, 3), 'h': round(meta['height'] * s, 3)}
    meta['audit'] = figure_audit(out / f'{a.name}.poster.png', tmp / 'poster.svg')
    (tmp / 'film.json').write_text(json.dumps(meta, indent=1), encoding='utf-8')
    au = meta['audit']
    print(f"audit    {au.get('solids', '?')} solids, fills {au['fill_w']:.0%} wide / {au['fill_area']:.0%} area, "
          f"edges {au['line_contrast']}:1, faces {au['face_contrast']}:1 on {au['bg']}")
    for w in au['warnings']:
        print('WARN    ', w)
    print(f'film     {mp4 if not a.poster_only else "(poster only)"}')
    if not a.poster_only:   # v5.7.1: the gate-6 motion rule, at render time
        import film_check
        ferr, fm = film_check.check(mp4, quiet=True)
        meta['audit'].update(fm)
        (tmp / 'film.json').write_text(json.dumps(meta, indent=1), encoding='utf-8')
        print(f'motion   {fm["motion"]}/255 over {fm["seconds"]} s' + ('' if not ferr else '  FAIL: ' + '; '.join(ferr)))
    print(f'poster   {out / (a.name + ".poster.png")}')
    print(f'editable {out / (a.name + ".shapes.json")}  ({len(frag["shapes"])} native shapes, group {frag["name"]!r})')
    print(f'fit      x={meta["fit"]["x"]} y={meta["fit"]["y"]} w={meta["fit"]["w"]} h={meta["fit"]["h"]} in; anchors {meta["anchors_in"]} (slide inches: film.json "anchors_in"; "anchors" there are figure pixels)')
    print('NEXT: look at the .strip.jpg, then a video shape {"type":"video","path":..., "poster":...} at the fit box, '
          'and the .shapes.json group on the editable keyframe (references/signature-moments.md §4)')


if __name__ == '__main__':
    main()
