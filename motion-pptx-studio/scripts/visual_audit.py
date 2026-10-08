"""Visual gates that v2 never measured: keyframe delta, image reuse, layout repetition.

v2 checked that a storyboard *declared* Morph layers and that CREDITS listed files. A 23-slide
Genshin Impact deck passed those gates while reusing ~7 screenshots (one on 6 slides), holding
the same photo still inside a scene so Morph only slid the words, and repeating one
text-left/image-right template. These checks fail that deck. They also run on a finished
.pptx or a PDF of the slides, so a reviewer can audit an output that has no project folder.

Thresholds (why these numbers, not the round examples):
  PIXEL_DELTA_MIN = 0.30   fraction of pixels whose channel delta exceeds 24, after both
                           frames are resized to 200×112. A global "every Morph pair must
                           clear 30%" rule false-fails the accepted ca trù and neko decks
                           (dark fields, counters, highlight walks). 30% is only the escape
                           hatch when a subject photo is otherwise stuck and big type still
                           changes the frame.
  SHAPE_MOVE_MIN = 0.06    of slide width. The brief's example was 10%. 10% false-fails
                           ca trù list-reveal callouts (~6.2%) and the neko cat grow (~9.8%).
                           6% still catches a photo that does not move. Do not drop this to
                           hide a pair that only moves ~1%.
  IMAGE_MOVE_MIN = 0.10    of slide width, box or crop. A push-in has to be visible.
                           Genshin's repeated photos move 0%.
  SUBJECT_REUSE_MAX = 4    dominant subject image on more than 4 slides is an error.
                           Ca trù's most reused photo is on exactly 4 slides; Genshin's
                           Mondstadt frame is on 6.
  PHOTO_LED_MIN = 0.40     distinct subject images must be >= consecutive runs only when
                           at least 40% of slides have a subject photo. Below that, a
                           typographic deck (neko: a handful of screens plus a circular
                           close) is not stretching one screenshot across every scene.
  LAYOUT_SCENE_MAX = 3     each storyboard layout value, and the editorial-left template
                           on a finished deck, may appear in at most 3 scenes.
  WORDS_AVG_MIN = 8        average on-slide words. This does not by itself fail the
                           Genshin deck (that deck is about 19 words/slide of slogans);
                           it fails a one-word deck. Slogan decks are caught by the fact-ID
                           rule when facts.md is in play.
  FACT_SLIDE_MIN = 0.40    of slides / storyboard rows must carry a fact ID defined in
                           facts.md. Enforced on the storyboard always, and on a finished
                           deck only when a facts file is passed or discovered. The two
                           accepted decks cite sources in speaker notes, not as fact IDs
                           on the slide, so a bare audit does not pretend they already pass.

A flat brand plate (low standard deviation and almost no edges) is not a subject photo.
Layered parts of similar area are not "one dominant image".

Measured on the three reference outputs (200×112, channel delta > 24):
  other.pdf, 23 slides — FAIL. Mondstadt hash 1f4144af dominant on slides 1, 2, 3, 19, 20, 21.
  7 distinct subject images < 8 runs (100% of slides are photo-led). Editorial-left on 5 scenes
  (slides 4–6, 9, 10–12, 13–15, 16–18). Stuck pairs 4→5, 13→14, 14→15, 16→17, 17→18, 22→23.
  One font family (Noto Sans; Noto Sans Display folded in). On-slide words average 22.7, so the
  word floor of 8 does not catch this deck; fact-ID coverage does, once facts.md is supplied.
  NEKO_CORE_motion.pptx, 34 slides — PASS. 6/34 slides carry a subject photo (18%, under the
  40% photo-led cutoff, so the cat's circular-close reuse is not an error). Max reuse 3.
  Editorial-left on 0 scenes. The cat on slides 2→3 moves 9.8% of slide width. Words average 59.5.
  Families: JetBrains Mono and Be Vietnam Pro.
  NEKO_CORE_CaTru_motion.pptx, 48 slides — one real defect, not a threshold bug. 22/48 slides
  carry a subject photo (46%), 9 distinct images and 9 runs, max reuse 4 (hash a535dcbe,
  slides 37–40). Editorial-left on 0 scenes. Words average 49.9. Families: Josefin Sans and
  Cormorant. Slides 31→32 share screenshot 52e451c0 with a 1.3% shape move and 2.8% pixel
  change: a near-duplicate. The 6% floor is what flags it; list-reveal pairs at 6.2% pass.
"""
import hashlib
import io
import re
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
P = '{%s}' % NS['p']
A = '{%s}' % NS['a']
R = '{%s}' % NS['r']

PIXEL_DELTA_MIN = 0.30
PIXEL_CHANNEL = 24
SHAPE_MOVE_MIN = 0.06
IMAGE_MOVE_MIN = 0.10
SUBJECT_REUSE_MAX = 4
PHOTO_LED_MIN = 0.40
LAYOUT_SCENE_MAX = 3
WORDS_AVG_MIN = 8
FACT_SLIDE_MIN = 0.40
FLAT_STD_MAX = 12.0
FLAT_EDGE_MAX = 4.0
SUBJECT_AREA_MIN = 0.12
SUBJECT_ONLY_MIN = 0.08
SUBJECT_MARGIN = 1.4
CONTENT_AREA_MIN = 0.05
KEYFRAME_MIN_SHARED = 2
MIN_SLIDES_FOR_DENSITY = 8

OFFICE_DEFAULTS = {
    'calibri', 'arial', 'times new roman', 'cambria', 'aptos',
    'carlito', 'liberation sans', 'liberation serif', 'liberation mono',
}
STYLE_WORDS = {
    'regular', 'bold', 'italic', 'medium', 'light', 'black', 'thin', 'semibold',
    'demibold', 'extrabold', 'extralight', 'ultralight', 'ultrabold', 'heavy',
    'book', 'roman', 'oblique', 'display', 'condensed', 'text', 'narrow', 'wide',
    'compressed', 'expanded', 'poster', 'caption', 'subhead', 'headline',
    'hairline', 'outline', 'shadow', 'rounded', 'variable', 'normal', 'semi',
}
SOURCE_CUE = re.compile(
    r'https?://|\b(?:from|source|brand|photo|lacquer|sample|pixel|board|dossier|'
    r'measured|eyedrop|pantone|sampled|swatch|nguồn|lấy từ)\b',
    re.I,
)
FACT_TOKEN = re.compile(r'\(([A-Za-z]{1,4}\d{1,3})\)')
FACT_ROW = re.compile(r'^\|\s*(\d+\.\d+)\s*\|')
HEX = re.compile(r'#[0-9A-Fa-f]{6}\b')
SCENE_ID = re.compile(r'\bS\d+\b', re.I)
IMG_EXT = re.compile(r'(?i)\b(?:(?:drawn|frame)\s*:\s*)?([^\s|,;`]+\.(?:jpe?g|png|webp|gif))\b')
DRAWN = re.compile(r'(?i)\bdrawn\s*:\s*([A-Za-z0-9][\w.-]*)')
WORD = re.compile(r"\w+", re.UNICODE)


class Audit:
    def __init__(self):
        self.errors, self.warns, self.infos = [], [], []
        self.n = 0

    def error(self, text):
        self.errors.append(text)

    def warn(self, text):
        self.warns.append(text)

    def info(self, text):
        self.infos.append(text)


def family_key(name):
    """Fold a typeface to a family. Noto Sans Display -> noto sans. Mono stays.

    CamelCase is split only for PostScript names with no spaces (NotoSansDisplay-Bold).
    A spaced name such as JetBrains Mono is not split on the internal capital.
    """
    if not name:
        return ''
    raw = re.sub(r'^[A-Z]{6}\+', '', name.strip())
    if not re.search(r'\s', raw):
        raw = raw.replace('_', ' ').replace('-', ' ')
        raw = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw)
        raw = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', raw)
    else:
        raw = raw.replace('_', ' ').replace('-', ' ')
    parts = [p for p in raw.split() if p]
    while parts and (parts[-1].lower() in STYLE_WORDS or re.fullmatch(r'\d+', parts[-1])):
        parts.pop()
    while len(parts) >= 2 and parts[-2].lower() == 'semi' and parts[-1].lower() in ('bold', 'light'):
        parts.pop()
        parts.pop()
    return ' '.join(parts).lower()


def counting_families(names):
    keys = []
    for n in names:
        k = family_key(n)
        if not k or k in OFFICE_DEFAULTS or k.startswith('+'):
            continue
        if k not in keys:
            keys.append(k)
    return keys


def font_family_from_file(path):
    try:
        from fontTools.ttLib import TTFont
        font = TTFont(str(path), fontNumber=0)
        table = font['name']
        fam = None
        for nid in (16, 1):
            for rec in table.names:
                if rec.nameID == nid:
                    try:
                        fam = rec.toUnicode()
                    except Exception:
                        continue
                    if fam:
                        break
            if fam:
                break
        font.close()
        if fam:
            return family_key(fam)
    except Exception:
        pass
    return family_key(Path(path).stem)


def words_of(text):
    return WORD.findall(text or '')


def fact_ids(facts_text):
    ids = []
    seen = set()
    for m in FACT_TOKEN.finditer(facts_text or ''):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    for line in (facts_text or '').splitlines():
        m = FACT_ROW.match(line.strip())
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    return ids


def cites_fact(text, ids):
    if not text or not ids:
        return False
    for i in ids:
        if re.search(r'(?<![\w.])' + re.escape(i) + r'(?![\w.])', text):
            return True
    return False


def visual_keys(cell):
    keys = []
    for m in IMG_EXT.finditer(cell or ''):
        keys.append('file:' + Path(m.group(1)).name.lower())
    for m in DRAWN.finditer(cell or ''):
        token = m.group(1)
        if not re.search(r'\.(?:jpe?g|png|webp|gif)$', token, re.I):
            keys.append('drawn:' + token.lower())
    return list(dict.fromkeys(keys))


def scene_token(cell):
    cell = (cell or '').strip()
    if not cell or cell.lower().startswith('todo'):
        return ''
    return re.split(r'\s+', cell)[0]


def storyboard_visual_errors(rows, col):
    """rows: list of dicts. col(row, name) -> cell. Returns error strings."""
    counts = Counter()
    scenes = {}
    where = defaultdict(list)
    for r in rows:
        sc = scene_token(col(r, 'scene')) or '?'
        scenes.setdefault(sc, 0)
        num = col(r, '#').strip() or '?'
        for k in visual_keys(col(r, 'visual')):
            counts[k] += 1
            where[k].append(num)
            scenes[sc] += 1
    errors = []
    for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n > SUBJECT_REUSE_MAX:
            errors.append(
                f'visual {k} is referenced on {n} rows (max {SUBJECT_REUSE_MAX}): rows {where[k]}'
            )
    if scenes and len(counts) < len(scenes):
        errors.append(
            f'{len(counts)} distinct visuals referenced < {len(scenes)} scenes '
            f'(drawn:<motif> counts; do not leave a scene without its own visual)'
        )
    return errors


def storyboard_layout_errors(rows, col):
    by = defaultdict(set)
    for r in rows:
        lay = col(r, 'layout').strip()
        if not lay or lay in ('-', '—') or 'todo' in lay.lower():
            continue
        sc = scene_token(col(r, 'scene')) or '?'
        by[lay.lower()].add(sc)
    errors = []
    for lay, scs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        if len(scs) > LAYOUT_SCENE_MAX:
            errors.append(
                f'layout {lay!r} is used in {len(scs)} scenes (max {LAYOUT_SCENE_MAX}): {sorted(scs)}'
            )
    return errors


def storyboard_density_errors(rows, col, facts_text):
    errors = []
    if not rows:
        return errors
    totals = []
    for r in rows:
        totals.append(len(words_of(col(r, 'on-slide'))))
    avg = sum(totals) / len(totals)
    if avg < WORDS_AVG_MIN:
        thin = [col(r, '#').strip() for r, n in zip(rows, totals) if n < WORDS_AVG_MIN]
        errors.append(
            f'on-slide text averages {avg:.1f} words/row (min {WORDS_AVG_MIN:g}); '
            f'rows under the floor: {thin[:12]}'
        )
    ids = fact_ids(facts_text)
    if not ids:
        errors.append('facts.md defines no fact IDs (S1) or table ids (1.1) to cite on slides')
        return errors
    hit = sum(1 for r in rows if cites_fact(col(r, 'on-slide'), ids))
    frac = hit / len(rows)
    if frac < FACT_SLIDE_MIN:
        errors.append(
            f'{hit}/{len(rows)} rows ({frac:.0%}) cite a fact ID on the slide (min {FACT_SLIDE_MIN:.0%})'
        )
    return errors


def colour_arc_ok(text):
    """True when text names >= 2 hexes and >= 2 scene ids (S1, S2, ...)."""
    live = '\n'.join(l for l in (text or '').splitlines() if 'TODO' not in l)
    hexes = set(h.upper() for h in HEX.findall(live))
    scenes = set(s.upper() for s in SCENE_ID.findall(live))
    return len(hexes) >= 2 and len(scenes) >= 2, sorted(hexes), sorted(scenes)


def palette_report(text):
    """Return (distinct hexes, unsourced hexes). TODO lines are ignored."""
    by = defaultdict(list)
    for line in (text or '').splitlines():
        if 'TODO' in line:
            continue
        found = HEX.findall(line)
        if not found:
            continue
        sourced = SOURCE_CUE.search(line) is not None
        for h in found:
            by[h.upper()].append(sourced)
    unsourced = sorted(h for h, flags in by.items() if not any(flags))
    return sorted(by), unsourced


def _xml(src_read, name):
    from lxml import etree
    return etree.fromstring(src_read(name))


class _Zip:
    def __init__(self, path):
        self.path = Path(path)
        self.zip = zipfile.ZipFile(path) if self.path.is_file() else None

    def names(self):
        if self.zip:
            return self.zip.namelist()
        return [p.relative_to(self.path).as_posix() for p in self.path.rglob('*') if p.is_file()]

    def read(self, name):
        if self.zip:
            return self.zip.read(name)
        return (self.path / name).read_bytes()

    def exists(self, name):
        if self.zip:
            return name in self.zip.namelist()
        return (self.path / name).is_file()


def _abs_box(el):
    chain = []
    node = el
    while node is not None:
        if node.tag in (P + 'sp', P + 'pic', P + 'cxnSp', P + 'grpSp'):
            xfrm = None
            for child in node:
                if child.tag in (P + 'spPr', P + 'grpSpPr'):
                    xfrm = child.find(A + 'xfrm')
                    break
            if xfrm is not None:
                off, ext = xfrm.find(A + 'off'), xfrm.find(A + 'ext')
                choff, chext = xfrm.find(A + 'chOff'), xfrm.find(A + 'chExt')

                def num(node, attr):
                    return int(node.get(attr) or 0) if node is not None else 0

                chain.append((
                    num(off, 'x'), num(off, 'y'), num(ext, 'cx'), num(ext, 'cy'),
                    num(choff, 'x'), num(choff, 'y'), num(chext, 'cx'), num(chext, 'cy'),
                ))
        node = node.getparent()
    if not chain:
        return None
    x, y, cx, cy = chain[0][:4]
    for g in chain[1:]:
        gx, gy, gw, gh, cox, coy, cw, ch = g
        if cw and ch:
            x = gx + (x - cox) * gw / cw
            y = gy + (y - coy) * gh / ch
            cx = cx * gw / cw
            cy = cy * gh / ch
        else:
            x += gx
            y += gy
    return x, y, cx, cy


def _crop(el):
    src = el.find('.//' + A + 'srcRect')
    if src is None:
        return (0.0, 0.0, 0.0, 0.0)
    return tuple(int(src.get(k) or 0) / 100000 for k in ('l', 't', 'r', 'b'))


def _flat(blob):
    try:
        from PIL import Image, ImageFilter, ImageStat
    except ImportError:
        return False
    try:
        im = Image.open(io.BytesIO(blob)).convert('L')
    except Exception:
        return False
    std = ImageStat.Stat(im).stddev[0]
    edge = ImageStat.Stat(im.resize((160, 90)).filter(ImageFilter.FIND_EDGES)).mean[0]
    return std < FLAT_STD_MAX and edge < FLAT_EDGE_MAX


def _slide_order(z):
    from lxml import etree
    rels = etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rid = {}
    for r in rels:
        if (r.get('Type') or '').endswith('/slide'):
            rid[r.get('Id')] = 'ppt/slides/' + Path(r.get('Target')).name
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    sz = pres.find('p:sldSz', NS)
    sw, sh = int(sz.get('cx')), int(sz.get('cy'))
    order = [rid[s.get(R + 'id')] for s in pres.find('p:sldIdLst', NS)]
    return order, sw, sh


def _notes_text(z, slide):
    from lxml import etree
    rp = slide.replace('slides/', 'slides/_rels/') + '.rels'
    if not z.exists(rp):
        return ''
    target = None
    for r in etree.fromstring(z.read(rp)):
        if (r.get('Type') or '').endswith('/notesSlide'):
            target = 'ppt/notesSlides/' + Path(r.get('Target')).name
    if not target or not z.exists(target):
        return ''
    return ''.join(t.text or '' for t in etree.fromstring(z.read(target)).iter(A + 't'))


def _para_lines(el, sw, sh):
    box = _abs_box(el)
    if not box:
        return []
    x, y, cx, cy = box[0] / sw, box[1] / sh, box[2] / sw, box[3] / sh
    lines = []
    for p in el.iter(A + 'p'):
        text = ''.join(t.text or '' for t in p.iter(A + 't')).strip()
        if not text:
            continue
        size = 0
        fonts = []
        for rpr in p.iter(A + 'rPr'):
            if rpr.get('sz'):
                size = max(size, int(rpr.get('sz')) / 100)
            lat = rpr.find(A + 'latin')
            if lat is not None and lat.get('typeface'):
                fonts.append(lat.get('typeface'))
        lines.append({'x': x, 'y': y, 'w': cx, 'h': cy, 'size': size, 'text': text, 'fonts': fonts})
    return lines


def load_pptx_slides(path):
    z = _Zip(path)
    order, sw, sh = _slide_order(z)
    media_cache = {}

    def media_info(fn):
        if fn not in media_cache:
            blob = z.read('ppt/media/' + fn)
            media_cache[fn] = (hashlib.sha256(blob).hexdigest()[:12], _flat(blob))
        return media_cache[fn]

    slides = []
    for part in order:
        from lxml import etree
        t = etree.fromstring(z.read(part))
        rp = part.replace('slides/', 'slides/_rels/') + '.rels'
        rmap = {}
        if z.exists(rp):
            for r in etree.fromstring(z.read(rp)):
                tgt = r.get('Target') or ''
                if 'media/' in tgt:
                    rmap[r.get('Id')] = Path(tgt).name
        pics = []
        for el in t.iter(P + 'pic'):
            blip = el.find('.//' + A + 'blip')
            if blip is None:
                continue
            fn = rmap.get(blip.get(R + 'embed'))
            if not fn:
                continue
            box = _abs_box(el)
            if not box:
                continue
            digest, flat = media_info(fn)
            area = (box[2] * box[3]) / (sw * sh)
            pics.append({
                'hash': digest, 'flat': flat, 'area': area,
                'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3],
                'crop': _crop(el),
            })
        shapes = {}
        for el in list(t.iter(P + 'sp')) + list(t.iter(P + 'pic')) + list(t.iter(P + 'cxnSp')):
            c = el.find('.//' + P + 'cNvPr')
            if c is None:
                continue
            nm = c.get('name') or ''
            if not nm.startswith('!!'):
                continue
            box = _abs_box(el)
            if box:
                shapes[nm] = box  # x, y, cx, cy in EMU
        lines = []
        fonts = []
        for el in t.iter(P + 'sp'):
            for line in _para_lines(el, sw, sh):
                lines.append(line)
                fonts.extend(line['fonts'])
        for el in t.iter(A + 'latin'):
            tf = el.get('typeface')
            if tf:
                fonts.append(tf)
        onslide = '\n'.join(ln['text'] for ln in lines)
        notes = _notes_text(z, part)
        marker = None
        m = re.search(r'(?:Cảnh|Scene)\s*(\d+)', notes, re.I)
        if m:
            marker = m.group(1)
        slides.append({
            'pics': pics, 'shapes': shapes, 'lines': lines, 'fonts': fonts,
            'onslide': onslide, 'notes': notes, 'marker': marker,
            'sw': sw, 'sh': sh,
        })
    return slides


def _dominant(pics):
    content = [p for p in pics if not p['flat'] and p['area'] >= CONTENT_AREA_MIN]
    content.sort(key=lambda p: p['area'], reverse=True)
    if not content:
        return None
    top = content[0]
    second = content[1]['area'] if len(content) > 1 else 0
    if top['area'] >= SUBJECT_AREA_MIN and (second == 0 or top['area'] >= SUBJECT_MARGIN * second):
        return top
    if len(content) == 1 and top['area'] >= SUBJECT_ONLY_MIN:
        return top
    return None


def _kicker(lines):
    for ln in lines:
        if ln['x'] < 0.22 and ln['y'] < 0.115 and 10 <= ln['size'] <= 18 and ln['w'] < 0.5:
            text = re.sub(r'\s+', ' ', ln['text']).strip()
            if 2 <= len(text) <= 40 and not text.isdigit():
                return text.casefold()
    return ''


def _editorial(slide):
    """The Genshin template: small left section kicker, large left title, bottom caption,
    subject image full-bleed or on the right, no right-side running header, no 3 body columns.
    """
    lines = slide['lines']
    kicker = _kicker(lines)
    if not kicker:
        return False
    right_header = any(
        ln['x'] > 0.55 and ln['y'] < 0.14 and ln['size'] <= 18 and 0.08 < ln['w'] < 0.5 and len(ln['text']) >= 2
        for ln in lines
    )
    if right_header:
        return False
    title = any(
        ln['x'] < 0.35 and 0.15 <= ln['y'] <= 0.70 and 40 <= ln['size'] <= 120 and ln['w'] < 0.75
        for ln in lines
    )
    if not title:
        return False
    caption = any(
        ln['x'] < 0.45 and ln['y'] >= 0.78 and 14 <= ln['size'] <= 32 and ln['w'] < 0.65
        and 6 <= len(ln['text']) <= 90
        for ln in lines
    )
    if not caption:
        return False
    # body columns
    bodies = [ln for ln in lines if 12 <= ln['size'] <= 28 and 0.40 <= ln['y'] <= 0.85 and ln['w'] < 0.42]
    centers = sorted(ln['x'] + ln['w'] / 2 for ln in bodies)
    cols, last = 0, -1
    for c in centers:
        if c - last > 0.18:
            cols += 1
            last = c
    if cols >= 3:
        return False
    sub = slide.get('subject')
    if not sub:
        return False
    cx = (sub['x'] + sub['w'] / 2) / slide['sw']
    width = sub['w'] / slide['sw']
    if width >= 0.85 or sub['area'] >= 0.75 or cx >= 0.55:
        return True
    return False


def _move(a, b, slide_w):
    if not a or not b:
        return 0.0
    return max(abs(a[i] - b[i]) for i in range(4)) / slide_w


def _crop_move(a, b):
    if not a or not b:
        return 0.0
    return max(abs(x - y) for x, y in zip(a, b))


def pixel_delta(im_a, im_b):
    from PIL import Image
    a = im_a.convert('RGB').resize((200, 112))
    b = im_b.convert('RGB').resize((200, 112))
    da, db = a.tobytes(), b.tobytes()
    changed = 0
    n = 200 * 112
    for i in range(n):
        o = i * 3
        if max(abs(da[o] - db[o]), abs(da[o + 1] - db[o + 1]), abs(da[o + 2] - db[o + 2])) > PIXEL_CHANNEL:
            changed += 1
    return changed / n


def _load_renders(directory):
    if not directory:
        return {}
    directory = Path(directory)
    out = {}
    if not directory.is_dir():
        return out
    from PIL import Image
    for p in directory.iterdir():
        m = re.search(r'(?:slide|page)[-_]?(\d+)\.(?:png|jpe?g)$', p.name, re.I)
        if m:
            out[int(m.group(1))] = Image.open(p).convert('RGB')
    return out


def _render_pptx(path):
    """Render a pptx to page images once. Returns {1-based index: PIL image} or {}."""
    path = Path(path)
    if not path.is_file():
        return {}
    soffice = None
    for cand in ('soffice', 'libreoffice'):
        from shutil import which
        soffice = which(cand)
        if soffice:
            break
    if not soffice:
        return {}
    key = hashlib.sha256(f'{path.resolve()}:{path.stat().st_mtime_ns}:{path.stat().st_size}'.encode()).hexdigest()[:16]
    cache = Path(tempfile.gettempdir()) / 'motion-visual-audit' / key
    done = cache / 'slide-01.png'
    if not done.exists():
        cache.mkdir(parents=True, exist_ok=True)
        profile = cache / 'profile'
        subprocess.run(
            [soffice, f'-env:UserInstallation=file://{profile}', '--headless', '--convert-to', 'pdf',
             '--outdir', str(cache), str(path)],
            capture_output=True, timeout=600,
        )
        pdfs = list(cache.glob('*.pdf'))
        if not pdfs:
            return {}
        subprocess.run(['pdftoppm', '-png', '-r', '40', str(pdfs[0]), str(cache / 'slide')],
                       capture_output=True, timeout=180)
        for f in cache.glob('slide-*.png'):
            n = int(f.stem.split('-')[-1])
            dest = cache / f'slide-{n:02d}.png'
            if f != dest:
                f.rename(dest)
    return _load_renders(cache)


def _scene_keys(slides):
    marked = sum(1 for s in slides if s.get('marker'))
    if marked >= 0.5 * max(1, len(slides)):
        keys, last = [], None
        for i, s in enumerate(slides):
            if s.get('marker'):
                last = 'm' + s['marker']
                keys.append(last)
            else:
                keys.append(last or f'u{i}')
        return keys
    keys, last, n = [], None, 0
    for s in slides:
        k = s.get('kicker') or ''
        if k and k == last:
            keys.append(f'k{n}:{k}')
        else:
            n += 1
            last = k or None
            keys.append(f'k{n}:{k or i_label(n)}')
    return keys


def i_label(n):
    return str(n)


def _apply_subject(slides):
    for s in slides:
        s['subject'] = _dominant(s['pics'])
        s['kicker'] = _kicker(s['lines'])
        s['editorial'] = _editorial(s)


def _reuse_and_runs(slides, audit):
    counts = Counter()
    where = defaultdict(list)
    runs = []
    for i, s in enumerate(slides, 1):
        sub = s.get('subject')
        h = sub['hash'] if sub else None
        if h:
            counts[h] += 1
            where[h].append(i)
        if h and runs and runs[-1][0] == h:
            runs[-1][1].append(i)
        elif h:
            runs.append((h, [i]))
    for h, n in counts.most_common():
        if n > SUBJECT_REUSE_MAX:
            audit.error(
                f'image reuse: {h} is the dominant subject image on {n} slides '
                f'(max {SUBJECT_REUSE_MAX}): slides {where[h]}'
            )
    photo_slides = sum(1 for s in slides if s.get('subject'))
    frac = photo_slides / max(1, len(slides))
    distinct = len(counts)
    audit.info(
        f'images: {photo_slides}/{len(slides)} slides have a subject photo '
        f'({frac:.0%}); {distinct} distinct; {len(runs)} consecutive runs; '
        f'most reused {counts.most_common(3)}'
    )
    if frac >= PHOTO_LED_MIN and distinct < len(runs):
        run_desc = ', '.join(f'{h} slides {ix}' for h, ix in runs)
        audit.error(
            f'image reuse: {distinct} distinct subject images < {len(runs)} consecutive runs '
            f'on a photo-led deck ({frac:.0%} of slides). {run_desc}'
        )


def _layout_repetition(slides, audit):
    keys = _scene_keys(slides)
    scenes = defaultdict(list)
    labels = {}
    for s, key in zip(slides, keys):
        if s.get('editorial'):
            scenes[key].append(s['_n'])
            labels[key] = s.get('kicker') or key
    n = len(scenes)
    if n > LAYOUT_SCENE_MAX:
        bits = [f'{labels[k]!r} slides {sorted(v)}' for k, v in scenes.items()]
        audit.error(
            f'layout: editorial-left (section kicker, title on the left, caption, image on the right '
            f'or full-bleed) on {n} scenes (max {LAYOUT_SCENE_MAX}): ' + '; '.join(bits)
        )
    else:
        audit.info(f'layout: editorial-left on {n} scene(s) (max {LAYOUT_SCENE_MAX})')


def _keyframe_pairs(slides, renders, audit, kind):
    failing = []
    measured = []
    for i in range(1, len(slides)):
        a, b = slides[i - 1], slides[i]
        sa, sb = a.get('subject'), b.get('subject')
        if not sa or not sb or sa['hash'] != sb['hash']:
            continue
        if kind == 'pptx':
            shared = set(a['shapes']) & set(b['shapes'])
            if len(shared) < KEYFRAME_MIN_SHARED:
                continue
            shape = 0.0
            for name in shared:
                shape = max(shape, _move(a['shapes'][name], b['shapes'][name], a['sw']))
        else:
            shared, shape = set(), 0.0
        box = _move((sa['x'], sa['y'], sa['w'], sa['h']), (sb['x'], sb['y'], sb['w'], sb['h']), a['sw'])
        crop = _crop_move(sa.get('crop'), sb.get('crop'))
        moved = box >= IMAGE_MOVE_MIN or crop >= IMAGE_MOVE_MIN or shape >= SHAPE_MOVE_MIN
        pix = None
        if not moved and renders.get(i) is not None and renders.get(i + 1) is not None:
            pix = pixel_delta(renders[i], renders[i + 1])
        line = (
            f'{i:02d}->{i+1:02d} image {sa["hash"]} box {box:.1%} crop {crop:.1%} '
            f'shape {shape:.1%} shared!! {len(shared)} pixels {("n/a" if pix is None else f"{pix:.1%}")}'
        )
        measured.append(line)
        stuck = (not moved) and (pix is None or pix < PIXEL_DELTA_MIN)
        if stuck:
            pix_txt = 'pixels not available' if pix is None else f'pixels changed {pix:.1%} < {PIXEL_DELTA_MIN:.0%}'
            failing.append(
                f'keyframe delta: slides {i}→{i+1} share subject image {sa["hash"]} '
                f'but it does not move (box {box:.0%} of slide width, crop {crop:.0%}, '
                f'largest shared !! shape {shape:.0%}; {pix_txt}). '
                f'Need a box/crop move ≥ {IMAGE_MOVE_MIN:.0%}, a !! shape move ≥ {SHAPE_MOVE_MIN:.0%}, '
                f'or ≥ {PIXEL_DELTA_MIN:.0%} of pixels changed.'
            )
    for line in measured:
        audit.info('keyframe ' + line)
    for msg in failing:
        audit.error(msg)
    if not measured:
        audit.info('keyframe: no consecutive slides share a dominant subject image')


def _density_and_fonts(slides, audit, facts_text, min_slides=MIN_SLIDES_FOR_DENSITY):
    totals = [len(words_of(s['onslide'])) for s in slides]
    avg = sum(totals) / max(1, len(totals))
    audit.info(f'on-slide words: avg {avg:.1f} (min floor {WORDS_AVG_MIN:g}, shortest {min(totals) if totals else 0})')
    if len(slides) >= min_slides and avg < WORDS_AVG_MIN:
        thin = [n for n, c in enumerate(totals, 1) if c < WORDS_AVG_MIN]
        audit.error(
            f'content density: on-slide text averages {avg:.1f} words/slide (min {WORDS_AVG_MIN:g}); '
            f'slides under the floor: {thin[:15]}'
        )
    fams = counting_families(f for s in slides for f in s.get('fonts', []))
    audit.info(f'font families: {fams or ["(none)"]}')
    if len(slides) >= min_slides and len(fams) < 2:
        audit.error(
            f'art direction: {len(fams)} font family on the slides ({", ".join(fams) or "none"}). '
            f'Need ≥ 2. Noto Sans and Noto Sans Display count as one family; '
            f'Calibri/Arial/Aptos and other Office defaults do not count.'
        )
    if facts_text:
        ids = fact_ids(facts_text)
        if not ids:
            audit.error('facts.md defines no fact IDs to match against on-slide text')
        else:
            hit = sum(1 for s in slides if cites_fact(s['onslide'], ids))
            frac = hit / max(1, len(slides))
            audit.info(f'fact IDs on slides: {hit}/{len(slides)} ({frac:.0%})')
            if frac < FACT_SLIDE_MIN:
                missing = [i for i, s in enumerate(slides, 1) if not cites_fact(s['onslide'], ids)]
                audit.error(
                    f'content density: {hit}/{len(slides)} slides ({frac:.0%}) carry a fact ID '
                    f'from facts.md (min {FACT_SLIDE_MIN:.0%}). Slides without one: {missing[:18]}'
                )


def audit_slides(slides, renders, facts_text, kind):
    audit = Audit()
    audit.n = len(slides)
    for i, s in enumerate(slides, 1):
        s['_n'] = i
    _apply_subject(slides)
    _reuse_and_runs(slides, audit)
    _layout_repetition(slides, audit)
    # Render only if some same-image pair is geometrically stuck, and renders are missing.
    _keyframe_pairs(slides, renders, audit, kind)
    _density_and_fonts(slides, audit, facts_text)
    return audit


def _needs_pixels(slides, kind):
    for i in range(1, len(slides)):
        a, b = slides[i - 1], slides[i]
        sa, sb = a.get('subject'), b.get('subject')
        if not sa or not sb or sa['hash'] != sb['hash']:
            continue
        if kind == 'pptx':
            shared = set(a['shapes']) & set(b['shapes'])
            if len(shared) < KEYFRAME_MIN_SHARED:
                continue
            shape = max((_move(a['shapes'][n], b['shapes'][n], a['sw']) for n in shared), default=0)
        else:
            shape = 0
        box = _move((sa['x'], sa['y'], sa['w'], sa['h']), (sb['x'], sb['y'], sb['w'], sb['h']), a['sw'])
        crop = _crop_move(sa.get('crop'), sb.get('crop'))
        if box < IMAGE_MOVE_MIN and crop < IMAGE_MOVE_MIN and shape < SHAPE_MOVE_MIN:
            return True
    return False


def discover_facts(deck_path, explicit):
    if explicit:
        p = Path(explicit)
        return p.read_text(encoding='utf-8') if p.is_file() else ''
    deck_path = Path(deck_path)
    candidates = [
        deck_path.parent / 'facts.md',
        deck_path.parent / 'research' / 'facts.md',
        deck_path.parent.parent / 'research' / 'facts.md',
    ]
    for c in candidates:
        if c.is_file():
            return c.read_text(encoding='utf-8')
    return None


def audit_pptx(path, renders_dir=None, facts_text=None):
    slides = load_pptx_slides(path)
    _apply_subject(slides)
    renders = _load_renders(renders_dir)
    if _needs_pixels(slides, 'pptx'):
        missing = any(
            renders.get(i) is None or renders.get(i + 1) is None
            for i in range(1, len(slides))
        )
        if missing and Path(path).is_file():
            try:
                rendered = _render_pptx(path)
            except (OSError, subprocess.SubprocessError):
                rendered = {}
            for k, v in rendered.items():
                renders.setdefault(k, v)
    return audit_slides(slides, renders, facts_text, 'pptx')


def load_pdf_slides(path):
    import pymupdf
    from PIL import Image
    doc = pymupdf.open(path)
    slides = []
    renders = {}
    for i, page in enumerate(doc, 1):
        pw, ph = page.rect.width, page.rect.height
        pics = []
        for info in page.get_image_info(xrefs=True):
            xref = info.get('xref')
            if not xref:
                continue
            raw = doc.extract_image(xref)
            blob = raw['image']
            rect = pymupdf.Rect(info['bbox'])
            # Store geometry in the same EMU-like space as fractions * page width,
            # so _move divides by slide width (pw).
            pics.append({
                'hash': hashlib.sha256(blob).hexdigest()[:12],
                'flat': _flat(blob),
                'area': (rect.width * rect.height) / (pw * ph),
                'x': rect.x0, 'y': rect.y0, 'w': rect.width, 'h': rect.height,
                'crop': (0, 0, 0, 0),
            })
        lines = []
        fonts = []
        for block in page.get_text('dict')['blocks']:
            if block.get('type') != 0:
                continue
            for line in block['lines']:
                spans = line.get('spans') or []
                if not spans:
                    continue
                text = ''.join(s['text'] for s in spans).strip()
                if not text:
                    continue
                s0 = spans[0]
                x0, y0, x1, y1 = s0['bbox']
                # union of span boxes
                x0 = min(s['bbox'][0] for s in spans)
                y0 = min(s['bbox'][1] for s in spans)
                x1 = max(s['bbox'][2] for s in spans)
                y1 = max(s['bbox'][3] for s in spans)
                size = max(s['size'] for s in spans)
                for s in spans:
                    fonts.append(s.get('font') or '')
                lines.append({
                    'x': x0 / pw, 'y': y0 / ph, 'w': (x1 - x0) / pw, 'h': (y1 - y0) / ph,
                    'size': size, 'text': text, 'fonts': [],
                })
        pix = page.get_pixmap(matrix=pymupdf.Matrix(0.22, 0.22), alpha=False)
        renders[i] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        slides.append({
            'pics': pics, 'shapes': {}, 'lines': lines, 'fonts': fonts,
            'onslide': '\n'.join(ln['text'] for ln in lines),
            'notes': '', 'marker': None, 'sw': pw, 'sh': ph,
        })
    return slides, renders


def audit_pdf(path, renders_dir=None, facts_text=None):
    try:
        slides, renders = load_pdf_slides(path)
    except ImportError:
        audit = Audit()
        audit.error('PDF audit needs pymupdf (pip install pymupdf). A .pptx can be audited without it.')
        return audit
    extra = _load_renders(renders_dir)
    renders.update(extra)
    return audit_slides(slides, renders, facts_text, 'pdf')


def audit_path(path, renders_dir=None, facts_path=None):
    path = Path(path)
    facts = discover_facts(path, facts_path)
    if path.suffix.lower() == '.pdf':
        return audit_pdf(path, renders_dir, facts)
    return audit_pptx(path, renders_dir, facts)


def print_audit(path, audit):
    print(f'deck: {path}  slides: {audit.n}')
    for line in audit.infos:
        print('  ' + line)
    for w in audit.warns:
        print('WARN ', w)
    for e in audit.errors:
        print('ERROR', e)
    print('RESULT:', 'FAIL' if audit.errors else 'PASS',
          f'({len(audit.errors)} errors, {len(audit.warns)} warnings)')


def main(argv=None):
    import argparse
    import sys
    ap = argparse.ArgumentParser(description='Audit keyframe delta, image reuse and layout repetition on a pptx or PDF.')
    ap.add_argument('deck')
    ap.add_argument('--renders', help='folder of slide-NN.png/jpg from render.sh (skips LibreOffice when the pair is already rendered)')
    ap.add_argument('--facts', help='facts.md; without it, fact-ID coverage is not an error')
    a = ap.parse_args(argv)
    audit = audit_path(a.deck, a.renders, a.facts)
    print_audit(a.deck, audit)
    sys.exit(1 if audit.errors else 0)


if __name__ == '__main__':
    main()
