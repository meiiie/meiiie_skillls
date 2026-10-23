#!/usr/bin/env python3
"""Art gates on rendered slides (render.sh output). Measures, never judges taste; look at what it flags.

  python3 art_check.py renders/rN --pptx deck/NAME.pptx [--max-run 2] [--min-grain 4]
- layout runs (WARN only; a crude signature, it cannot judge composition): zone of the biggest picture and title per slide;
  near-identical maps (cosine >= .92) means one composition is repeating (three-directions, art-direction).
- flat grounds: fine-detail sigma in the slide's emptiest cells; under --min-grain the material is invisible
  at 2x (surface-and-depth). Photos/films are not grounds: only empty cells are sampled.
- chapter materials: the ground statistics of each slide; identical ground on every chapter is reported.
Flags are prompts to look, not verdicts (a good deck can have a quiet flat page). --strict exits 1.
"""
import re
import sys, glob, argparse
import numpy as np
from PIL import Image, ImageFilter

def stats(p):
    im = Image.open(p).convert('L').resize((960, 540))
    a = np.asarray(im, float)
    edges = np.asarray(im.filter(ImageFilter.FIND_EDGES), float)
    hp = a - np.asarray(im.filter(ImageFilter.GaussianBlur(6)), float)
    cells, quiet = [], []
    for j in range(4):
        for i in range(6):
            sl = (slice(j * 135, (j + 1) * 135), slice(i * 160, (i + 1) * 160))
            cells.append(edges[sl].mean() + abs(a[sl].mean() - np.median(a)) * .5)
            quiet.append((edges[sl].mean(), hp[sl].std()))
    v = np.array(cells); v = v / (np.linalg.norm(v) + 1e-9)
    quiet.sort()
    return v, float(np.median([q[1] for q in quiet[:5]])), round(float(np.median(a)) / 8)

def zone(sh, W, H):
    cx, cy = (sh.left + sh.width / 2) / W, (sh.top + sh.height / 2) / H
    big = 'F' if sh.width * sh.height > .6 * W * H else min(2, int(cx * 3)) + 3 * min(2, int(cy * 3))
    return big

def layouts(path):
    """Composition signature per slide: zone of the biggest picture/film and of the biggest text."""
    from pptx import Presentation
    pr = Presentation(path); W, H = pr.slide_width, pr.slide_height; out = []
    for s in pr.slides:
        pics = [x for x in s.shapes if x.shape_type in (13, 16) and x.width * x.height < .95 * W * H]
        txt = [x for x in s.shapes if x.has_text_frame and x.text_frame.text.strip()]
        P = max(pics, key=lambda x: x.width * x.height, default=None)
        T = max(txt, key=lambda x: max((r.font.size or 0) for p in x.text_frame.paragraphs for r in p.runs) if x.text_frame.paragraphs else 0, default=None)
        out.append((zone(P, W, H) if P else '-', zone(T, W, H) if T else '-'))
    return out


def text_extent(sh):
    """v6.22: approximate inked box of a text frame (EMU): longest line x 0.55 em per char, lines x 1.2 em,
    honouring centre/right alignment; never larger than the shape itself."""
    lines, pt, al = [], 18.0, 1
    for p_ in sh.text_frame.paragraphs:
        sz = max([r.font.size.pt for r in p_.runs if r.font.size] or [pt]); pt = max(pt, sz) if lines else sz
        lines += [(ln, sz) for ln in (p_.text or '').split('\v')]
        if p_.alignment is not None: al = int(p_.alignment)
    w = min(sh.width, int(max((len(t) * z * 0.55 for t, z in lines), default=0) * 12700) + 2 * 91440)
    h = min(sh.height, int(sum(z * 1.2 for _, z in lines) * 12700) + 91440)
    left = sh.left + ((sh.width - w) // 2 if al == 2 else (sh.width - w) if al == 3 else 0)
    return left, sh.top, w, h


def real_photo(im):
    """v6.11 photo vs rendered illustration: a photograph has many colours and almost no flat (noise-free) regions;
    a render or vector illustration has few colours and large flat areas. Tested on 12 past decks."""
    try:   # v6.21: a camera photo of calm sky/sea/fog is flat but real - trust camera EXIF
        ex = im.getexif()
        if ex and (ex.get(271) or ex.get(272)): return True
    except Exception: pass
    im = im.convert('RGBA'); im.thumbnail((256, 256))
    a = np.asarray(im)[..., 3] > 200; cover = a.mean()
    if cover < 0.05: return False
    rgb = np.asarray(im.convert('RGB'))
    cols = len(np.unique((rgb[a] // 8).astype(np.int32) @ np.array([1024, 32, 1])))
    g = np.asarray(im.convert('L').filter(ImageFilter.MedianFilter(3)), float)
    mx = np.asarray(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), float)
    mn = np.asarray(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.MinFilter(5)), float)
    flat = ((mx - mn) <= 6)[a].mean()
    return bool(flat < 0.12 or (flat < 0.35 and cols >= 450 * max(cover, 0.3)) or (flat < 0.75 and cols >= 1400 * max(cover, 0.3)))   # v6.21 smooth skies keep many colours

def iso_score(im):
    """v6.13 share of edges at the isometric +-30 deg; >= 0.10 = an isometric block scene (default fallback)."""
    g = np.asarray(im.convert('L').resize((256, 256)), float)
    gx = np.diff(g, axis=1)[:-1]; gy = np.diff(g, axis=0)[:, :-1]; k = np.hypot(gx, gy) > 25
    if k.sum() < 200: return 0.0
    a = (np.degrees(np.arctan2(gy[k], gx[k])) + 180) % 180
    return float((np.abs(a - 60) < 6).mean() + (np.abs(a - 120) < 6).mean())


POSTER_PT = int(__import__('os').environ.get('POSTER_PT', 150))

def photo_read(pptx_path, render_dir, deck_json=None):
    """v6.7 photo-reading gates. Returns (fails, notes). Hard: text over busy photo areas, big empty zones on many
    slides, a chapter without a full-bleed photo or without a cut-out."""
    import io, json
    from pptx import Presentation
    pr = Presentation(pptx_path); W, H = pr.slide_width, pr.slide_height
    renders = sorted(glob.glob(f'{render_dir}/slide-*.jpg') + glob.glob(f'{render_dir}/slide-*.png'))
    chapters = None
    if deck_json:
        sl = [x for x in json.load(open(deck_json)).get('slides', []) if not x.get('hidden')]
        if any('chapter' in x for x in sl):
            chapters = [str(x.get('chapter', '')) for x in sl]
    fails, notes, info = [], [], []
    small_cut, header, hero, nphoto, isos = [], [], [], [], []
    for k, slide in enumerate(pr.slides):
        bleed = cut = film = False; photos = []
        for blip in slide._element.xpath('./p:cSld/p:bg//a:blip'):   # slide background image = full-bleed
            rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            try:
                im = Image.open(io.BytesIO(slide.part.related_part(rid).blob))
                if real_photo(im):
                    bleed = True; nphoto.append(k + 1)
            except Exception:
                pass
        for sh in slide.shapes:
            if sh.shape_type == 16 and sh.width * sh.height >= 0.2 * W * H: film = True
            if sh.shape_type == 16 and sh.width * sh.height >= 0.9 * W * H:
                bleed = True   # a full-bleed film counts as the chapter's bleed
            if sh.shape_type != 13:
                continue
            try:
                im = Image.open(io.BytesIO(sh.image.blob))
            except Exception:
                continue
            area = sh.width * sh.height / (W * H)
            g = np.asarray(im.convert('L').resize((64, 36)), float)
            is_photo = real_photo(im)
            if not is_photo and area >= 0.06 and iso_score(im) >= 0.10: isos.append(k + 1)
            if is_photo and area >= 0.06: nphoto.append(k + 1)
            if im.mode in ('RGBA', 'LA', 'P') and 'A' in im.convert('RGBA').getbands():
                a = np.asarray(im.convert('RGBA').getchannel('A'))
                edge = sh.left <= 0 or sh.top <= 0 or sh.left + sh.width >= W or sh.top + sh.height >= H
                if 0.1 < (a < 20).mean() < 0.9 and (area >= 0.12 or edge):
                    cut = True
                    if is_photo: nphoto.append(k + 1)
                    continue
                if 0.1 < (a < 20).mean() < 0.9:
                    small_cut.append(k + 1); continue
            if is_photo:
                photos.append(sh)
                if area >= 0.9: bleed = True
        big_pt, big_sh = 0, None
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                for p_ in sh.text_frame.paragraphs:
                    for r_ in p_.runs:
                        if r_.font.size and r_.font.size.pt > big_pt: big_pt, big_sh = r_.font.size.pt, sh
        if big_sh is not None and big_sh.top < 0.2 * H and big_sh.left < 0.15 * W and big_pt < 48:
            header.append(k + 1)
        if big_pt >= 180 or bleed or cut or any(p.width * p.height >= 0.5 * W * H for p in photos):
            hero.append(k + 1)
        busy = []
        if k < len(renders) and photos:
            r = Image.open(renders[k]).convert('L'); rw, rh = r.size
            med = r.filter(ImageFilter.MedianFilter(9))
            for sh in slide.shapes:
                if not sh.has_text_frame or len(sh.text_frame.text.strip()) < 3:
                    continue
                tl, tt, tw_, th_ = text_extent(sh)   # v6.22: the inked text area, not the text-box width
                for ph in photos:
                    x0, y0 = max(tl, ph.left), max(tt, ph.top)
                    x1, y1 = min(tl + tw_, ph.left + ph.width), min(tt + th_, ph.top + ph.height)
                    if x1 - x0 > 0 and y1 - y0 > 0:
                        box = tuple(int(v) for v in (x0 / W * rw, y0 / H * rh, x1 / W * rw, y1 / H * rh))
                        if box[2] - box[0] > 8 and box[3] - box[1] > 8:
                            sd = np.asarray(med.crop(box), float).std()
                            if sd > 28: busy.append(round(sd))
        has_pic = any(sh.shape_type in (13, 16) for sh in slide.shapes)
        if k < len(renders) and has_pic and (k + 1) not in nphoto and iso_score(Image.open(renders[k])) >= 0.10: isos.append(k + 1)   # v6.21: not photos/text-only slides
        empty = 0.0
        if k < len(renders):
            g = Image.open(renders[k]).convert('L').resize((160, 90)).filter(ImageFilter.GaussianBlur(1.5))
            e = np.asarray(g.filter(ImageFilter.FIND_EDGES), float)
            cells = np.array([[e[j*15:(j+1)*15, i*20:(i+1)*20].mean() < 2.0 for i in range(8)] for j in range(6)])
            empty = largest_block(cells) / 48
        src = any('nguồn' in (sh.text_frame.text[:40].lower()) or 'source' in sh.text_frame.text[:40].lower()
                  for sh in slide.shapes if sh.has_text_frame)
        alltxt = ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame).lower()
        head = (big_sh.text_frame.text.strip().lower()[:30] if big_sh is not None else '')
        srcslide = head.startswith(('nguồn', 'source', 'tài liệu', 'credits', 'tham khảo')) or \
            sum(alltxt.count(w) for w in ('http', 'wikimedia', 'cc by', 'cc0', 'public domain', 'nguồn')) >= 4
        card = not (srcslide or film or cut or big_pt >= POSTER_PT or (k + 1) in nphoto)
        info.append({'film': film, 'src': src, 'bleed': bleed, 'cut': cut, 'busy': busy, 'empty': empty, 'card': card})
        if busy: fails.append(f'TEXT    slide {k+1}: text over a busy photo area (median-filtered sigma {busy}, need <= 28): '
                              'move it to the quiet side (photo_layout analyze) or add a light falloff')
    if len(header) > len(info) / 3:
        fails.append(f'HEADER  {len(header)}/{len(info)} slides are a small top-left headline over content {header}: '
                     'a template, not a stage - let hero/photo/film slides speak without it (one-type-scale)')
    if small_cut:
        notes.append(f'small cut-outs (not counted; need >= 12 % of the slide or a bleed): slides {sorted(set(small_cut))}')
    hashes = []
    for k, f in enumerate(renders[:len(info)]):
        g = np.asarray(Image.open(f).convert('L').resize((17, 16)), float)
        hashes.append((g[:, 1:] > g[:, :-1]).flatten())
    dup = [(i + 1, j + 1) for i in range(len(hashes)) for j in range(i + 1, min(len(hashes), i + 4))
           if (hashes[i] != hashes[j]).mean() < 0.26 and not (info[i]['src'] and info[j]['src']) and not (info[i]['film'] or info[j]['film'])]
    if dup:
        fails.append(f'DUPLICATE near-identical slides {dup}: a picture appears once; move the camera or change the idea (data-as-object)')
    cards = [k + 1 for k, i in enumerate(info) if i['card']]
    if len(cards) > max(2, len(info) // 6):   # v6.18: WARN only (gamed by 150 pt words); the per-slide critic judges
        notes.append(f'WARN CARDS   {len(cards)} card slides {cards} (no real photo, film, cut-out or type >= {POSTER_PT} pt; max {max(2, len(info) // 6)}): '
                     'turn each into a metaphor-object photo, a typographic poster or a lit 3-D still (abstract-illustration)')
    elif cards: notes.append(f'cards   {cards} (allowed <= {max(2, len(info) // 6)})')
    many_empty = [k + 1 for k, i in enumerate(info) if i['empty'] > 0.5]
    if len(many_empty) > max(2, len(info) // 6):
        fails.append(f'EMPTY   {len(many_empty)} slides are more than half empty field {many_empty}: scale the subject up or merge slides')
    elif many_empty: notes.append(f'empty   {many_empty} (allowed: a few deliberate quiet pages)')
    if chapters is None:
        chapters = [str(i // 6) for i in range(len(info))]; notes.append('no "chapter" keys in deck.json: checked in windows of 6 slides')
    for c in dict.fromkeys(chapters):
        idx = [k for k, x in enumerate(chapters[:len(info)]) if x == c]
        if len(idx) < 3 or not c: continue
        if re.match(r'(?i)^(nguồn|sources?|credits?|tài liệu|tham khảo|ghi chú|end|kết)', c): continue   # v6.22 sources/credits chapter exempt
        if not any(info[k]['bleed'] for k in idx):
            fails.append(f'BLEED   chapter {c!r} (slides {idx[0]+1}-{idx[-1]+1}) has no full-bleed REAL photo or full-bleed film (photo-arrangement)')
        if not any(k + 1 in hero for k in idx):
            fails.append(f'HERO    chapter {c!r} has no hero-scale slide (type >= 180 pt, full-bleed, a big cut-out or photo >= 50 %)')
        if not any(info[k]['cut'] for k in idx):
            notes.append(f'cutout  chapter {c!r} has no cut-out (optional since 6.11)')
        if False:
            fails.append(f'CUTOUT  chapter {c!r} (slides {idx[0]+1}-{idx[-1]+1}) has no cut-out (photo_layout.py cutout -> PNG with alpha)')
    why = deck_json and json.load(open(deck_json)).get('no_photo_reason')
    np_ = sorted(set(nphoto))
    if len(np_) < max(3, len(info) // 5) and not why:
        fails.append(f'PHOTOS  only {len(np_)} slides carry a real photograph {np_} (renders and illustrations do not count): '
                     'every subject has a physical thing - fetch credited photos (fetch_commons.py), or set deck.json '
                     '"no_photo_reason" with an honest reason (abstract-illustration)')
    notes.append(f'real photos on slides {np_}')
    iso_ = sorted(set(isos))
    if len(iso_) >= 4:
        fails.append(f'ISO     {len(iso_)} slides are isometric block scenes {iso_}: the default fallback - use a photo of the thing, '
                     'macro, collage, type or a lit 3-D still (abstract-illustration)')
    elif iso_: notes.append(f'ISO-LOOK isometric-looking slides {iso_}: keep only those that draw a real structure (max 2)')
    return fails, notes


def largest_block(cells):
    """Largest all-True axis-aligned rectangle (in cells)."""
    R, C = cells.shape; best = 0; hgt = [0] * C
    for r in range(R):
        hgt = [hgt[c] + 1 if cells[r, c] else 0 for c in range(C)]
        for c in range(C):
            m = hgt[c]
            for d in range(c, C):
                m = min(m, hgt[d])
                if not m: break
                best = max(best, m * (d - c + 1))
    return best


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--max-run', type=int, default=2)
    ap.add_argument('--min-grain', type=float, default=4.0); ap.add_argument('--pptx'); ap.add_argument('--strict', action='store_true'); ap.add_argument('--deck'); a = ap.parse_args()
    files = sorted(glob.glob(f'{a.dir}/slide-*.jpg') + glob.glob(f'{a.dir}/slide-*.png'))
    S = [stats(f) for f in files]; fail = False
    if a.pptx:
        L = layouts(a.pptx); run = 1
        for k in range(1, len(L)):
            run = run + 1 if L[k] == L[k - 1] and L[k] != ('-', '-') else 1
            if run == a.max_run + 1:
                print(f'LAYOUT  slides {k - a.max_run + 1}-{k + 1}: same composition {L[k]} (picture zone, title zone): look, vary if unintended')
        from collections import Counter
        c = Counter(L).most_common(1)[0]
        print(f'layouts: {len(set(L))} distinct over {len(L)} slides; most common {c[0]} on {c[1]}')
        if c[1] > len(L) // 3: print('LAYOUT  one composition carries over a third of the deck: look')
    flat = [k + 1 for k, s in enumerate(S) if s[1] < a.min_grain - 0.5]   # v6.21: 0.5 hysteresis, tiny grain changes no longer flip it
    if flat:
        print(f'FLAT    {len(flat)}/{len(S)} slides have no visible material (fine sigma < {a.min_grain}): {flat}'); fail |= len(flat) > len(S) // 4
    g = [round(s[1]) for s in S]
    print('grain sigma per slide:', g)
    hard = []
    if a.pptx:
        hard, notes = photo_read(a.pptx, a.dir, a.deck)
        for n in notes: print(n)
        for h in hard: print('FAIL   ', h)
    print('art_check:', 'FAIL (photo reading)' if hard else ('LOOK at the flagged slides' if fail else 'ok'))
    sys.exit(1 if hard or (fail and a.strict) else 0)

if __name__ == '__main__':
    main()
