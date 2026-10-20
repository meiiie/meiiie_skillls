"""Whole-deck motion/accuracy audit for a .pptx, an unpacked deck folder, or a slide PDF.

Checks (ERROR = must fix, WARN = look at it):
  ERROR  a slide without exactly one transition (Morph wrapper counts as one)
  ERROR  duplicate !! names on one slide; the same !! name with different shape kinds on
         neighbouring slides (Morph cannot pair a picture with a text box)
  ERROR  forbidden characters in on-slide text (default: Han/CJK ideographs; --forbid-notes also scans notes)
  ERROR  template leftovers (Lorem ipsum, Click to add, Sample text, ...)
  ERROR  deck bigger than --max-mb
  ERROR  keyframe delta: a consecutive pair that shares a dominant subject image does not move it
         (box/crop < 10% of slide width, no shared !! shape moves ≥ 6%, and < 30% of pixels change)
  ERROR  image reuse: one subject image is dominant on more than 4 slides, or a photo-led deck
         has fewer distinct subject images than consecutive runs of the same image
  ERROR  layout: the editorial-left template (kicker, left title, caption, image right or full-bleed)
         appears in more than 3 scenes
  ERROR  fewer than 2 font families (Noto Sans Display counts as Noto Sans; Office defaults do not count)
  ERROR  average on-slide words under 8, on a deck of 8 or more slides
  ERROR  no persistent system: no !! shape on 60% of the slides (craft_audit.py)
  WARN   a hold beat (one still photo pair per scene, at most 10% of transitions); text overflow;
         text outside the safe area; more than 10 text sizes; flat grounds; low contrast (with --renders);
         under 40% of slides citing a fact ID on the slide or in the notes (with --facts)
  WARN   slides without speaker notes; !! names that never pair; fonts used but not installed;
         images wider than 2560 px; byte-identical media (run finish_dedupe.py)
  ERROR  animation XML that targets a shape id not on the slide, or repeats a timing node id
  WARN   motion monotony: 12+ slides, >85% Morph, no emphasis/path/exit/letter/video effect
  WARN   variety (v5.2, --variety strict makes these ERRORs; 15+ slides, scaled down for smaller decks):
         < 10 distinct effect techniques, one technique > 35% of effect nodes, < 5 transition types,
         < 60% distinct layout signatures across scene cuts or 3 equal cuts in a row,
         < 20% of slides with moving depth (plate + moving layer + text)
  ERROR  no-Morph (v5.1, --compat or motion.json "compat"): in safe mode any Morph left, or a shared !! shape
         that moves with no classic replacement (path/entrance); with --nomorph-render DIR the deck is
         rendered with every Morph replaced by its fallback and each slide must match the --renders end state
  WARN   no-Morph: visible text boxes that overlap in a slide's end state
  INFO   per-slide transition (Morph or which other) and duration, effect census, entrance count, shared !! layers, measured keyframe deltas

A PDF has no !! names or transitions. On a PDF the keyframe, image-reuse, layout, font-family
and word-count checks still run from the rendered pages and the embedded images.

Usage:
  python check_deck.py DECK.pptx|UNPACKED_DIR|DECK.pdf [--max-mb 25] [--anchor "Hỏi trước, rồi mới làm."]
         [--anchor-count 3] [--expect-slides 34] [--forbid-notes] [--extra-forbid "歌籌,MIT"]
         [--renders DIR] [--facts research/facts.md] [--compat morph|safe|dual] [--nomorph-render DIR]
         [--variety warn|strict|off]
Exit code 1 when any ERROR is found.
"""
import argparse
import hashlib
import io
import re
import subprocess
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motionlib  # noqa: E402

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
P, A, R, MC = ('{%s}' % NS[k] for k in ('p', 'a', 'r', 'mc'))
HAN = re.compile('[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002FA1F\u3040-\u30FF\uAC00-\uD7AF]')
LEFTOVERS = re.compile(r'lorem ipsum|click to add|sample text|your text here|title here|vertical title|'
                       r'description photo|name title or position|add a heading|subtitle here|placeholder', re.I)
SLIDE_T = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'


class Src:
    """Read parts from a .pptx zip or an unpacked folder with the same API."""
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
        return name in set(self.names())

    def size(self):
        if self.zip:
            return self.path.stat().st_size
        return sum((self.path / n).stat().st_size for n in self.names())


def xml(src, name):
    return etree.fromstring(src.read(name))


def slide_order(src):
    rels = xml(src, 'ppt/_rels/presentation.xml.rels')
    rid = {r.get('Id'): 'ppt/slides/' + Path(r.get('Target')).name for r in rels if r.get('Type') == SLIDE_T}
    pres = xml(src, 'ppt/presentation.xml')
    lst = pres.find('p:sldIdLst', NS)
    return [rid[s.get(R + 'id')] for s in lst] if lst is not None else []


def notes_part(src, slide):
    rp = slide.replace('slides/', 'slides/_rels/') + '.rels'
    if not src.exists(rp):
        return None
    for r in xml(src, rp):
        if r.get('Type', '').endswith('/notesSlide'):
            return 'ppt/notesSlides/' + Path(r.get('Target')).name
    return None


def text_of(el):
    return '\n'.join(''.join(t.text or '' for t in p.iter(A + 't')) for p in el.iter(A + 'p'))


def notes_text(src, part):
    if not part:
        return ''
    t = xml(src, part)
    for sp in t.iter(P + 'sp'):
        ph = sp.find('.//p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type') == 'body':
            return text_of(sp)
    return ''


def installed_fonts():
    try:
        out = subprocess.run(['fc-list', ':', 'family'], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    fams = set()
    for line in out.splitlines():
        for f in line.split(','):
            fams.add(f.strip().lower())
    return fams


def nomorph_render(src, deck, out_dir, intended=None):
    """Write DECK with every Morph replaced by its mc:Fallback, render it (render.sh) and compare it with the
    intended render folder. Returns (errors, infos)."""
    import compat
    import tempfile
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stripped = out / (Path(deck).stem + '-nomorph.pptx')
    n = 0
    with zipfile.ZipFile(stripped, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in src.names():
            data = src.read(name)
            if re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
                root = etree.fromstring(data)
                k = compat.strip_morph(root)
                if k:
                    n += k
                    data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            z.writestr(name, data)
    infos = [f'no-Morph copy: {n} Morph transition(s) replaced by their fallback -> {stripped}']
    r = subprocess.run(['bash', str(Path(__file__).resolve().parent / 'render.sh'), str(stripped), str(out)],
                       capture_output=True, text=True)
    if r.returncode or not list(out.glob('slide-*.jpg')):
        return [f'no-Morph render failed: {(r.stderr or r.stdout).strip()[-300:]}'], infos
    if not intended:
        infos.append('no-Morph render done; pass --renders to compare it with the intended end states')
        return [], infos
    e, i = compat.compare_renders(intended, out)
    return e, infos + i


def main(argv=None):
    ap = argparse.ArgumentParser(description='Audit a motion deck.')
    ap.add_argument('deck')
    ap.add_argument('--max-mb', type=float, default=25.0)
    ap.add_argument('--anchor', action='append', default=[], help='anchor phrase to count (on-slide text)')
    ap.add_argument('--anchor-count', type=int, default=3)
    ap.add_argument('--expect-slides', type=int)
    ap.add_argument('--forbid-notes', action='store_true', help='also scan speaker notes for forbidden characters')
    ap.add_argument('--extra-forbid', default='', help='comma-separated strings that must not appear on slides')
    ap.add_argument('--no-han-check', action='store_true', help='allow CJK characters (only if the user wants them)')
    ap.add_argument('--renders', help='slide-NN images from render.sh; used when a stuck photo needs a pixel measurement')
    ap.add_argument('--facts', help='facts.md; fact-ID coverage is an error only when this (or a nearby facts.md) exists')
    ap.add_argument('--compat', choices=('morph', 'safe', 'dual'),
                    help='no-Morph mode to audit (default: "compat" in a motion.json next to the deck, else morph)')
    ap.add_argument('--nomorph-render', help='render the deck with Morph stripped into this folder and compare it with --renders')
    ap.add_argument('--variety', choices=('warn', 'strict', 'off'), default='warn',
                    help='v5.2 variety audit (techniques, max share, transitions, composition, moving depth): '
                         'warn (default) or strict (errors); see variety_audit.py and references/pro-craft.md')
    a = ap.parse_args(argv)
    if Path(a.deck).suffix.lower() == '.pdf':
        from visual_audit import audit_path, print_audit
        audit = audit_path(a.deck, a.renders, a.facts)
        print_audit(a.deck, audit)
        sys.exit(1 if audit.errors else 0)
    src = Src(a.deck)
    errors, warns, info = [], [], []
    order = slide_order(src)
    if a.expect_slides and len(order) != a.expect_slides:
        errors.append(f'deck has {len(order)} slides, expected {a.expect_slides}')
    extra = [s for s in a.extra_forbid.split(',') if s]
    prev_kinds = None
    seen_names = Counter()
    fonts = Counter()
    anchor_hits = Counter()
    tr_census, fx_census = Counter(), Counter()
    for pos, part in enumerate(order, 1):
        t = xml(src, part)
        fname = Path(part).name
        tag = f'pos {pos:2} ({fname})'
        # transitions
        n_wrap = sum(1 for ac in t.findall(MC + 'AlternateContent') if ac.find('.//' + P + 'transition') is not None)
        n_plain = len(t.findall(P + 'transition'))
        n_tr = n_wrap + n_plain
        morph = t.find('.//{http://schemas.microsoft.com/office/powerpoint/2015/09/main}morph')
        if n_tr != 1:
            errors.append(f'{tag}: {n_tr} transitions (need exactly 1; re-run motion.py)')
        dur = None
        for tr in t.iter(P + 'transition'):
            dur = tr.get('{http://schemas.microsoft.com/office/powerpoint/2010/main}dur') or dur
        timing = t.find(P + 'timing')
        custom = ''
        tr_name, _ms = motionlib.describe_transition(t)
        cen = motionlib.timing_census(t)
        for e in cen['errors']:
            errors.append(f'{tag}: {e}')
        tr_census[tr_name] += 1
        fx_census.update({k: v for k, v in cen.items() if k != 'errors' and v})
        extra_fx = ', '.join(f'{v} {k}' for k, v in cen.items() if k not in ('errors', 'entr', 'click') and v)
        if timing is not None:
            s = etree.tostring(timing).decode()
            n_entr = s.count('presetClass="entr"')
        else:
            n_entr = 0
        # names / kinds
        kinds, names = {}, []
        for c in t.iter(P + 'cNvPr'):
            nm = c.get('name') or ''
            if nm.startswith('!!'):
                names.append(nm)
                kinds[nm] = etree.QName(c.getparent().getparent()).localname
        dups = sorted(n for n, k in Counter(names).items() if k > 1)
        if dups:
            errors.append(f'{tag}: duplicate !! names {dups}')
        shared = 0
        if prev_kinds is not None:
            common = set(kinds) & set(prev_kinds)
            shared = len(common)
            mism = sorted(n for n in common if kinds[n] != prev_kinds[n])
            if mism:
                errors.append(f'{tag}: !! kind mismatch with previous slide {[(n, prev_kinds[n], kinds[n]) for n in mism]}')
        for n in set(names):
            seen_names[n] += 1
        prev_kinds = kinds
        # text checks
        slide_txt = text_of(t)
        if not a.no_han_check:
            hits = HAN.findall(slide_txt)
            if hits:
                errors.append(f'{tag}: forbidden CJK characters on slide: {"".join(hits)[:20]}')
        for s in extra:
            if s in slide_txt:
                errors.append(f'{tag}: forbidden string on slide: {s!r}')
        if LEFTOVERS.search(slide_txt):
            errors.append(f'{tag}: template leftover text: {LEFTOVERS.search(slide_txt).group(0)!r}')
        for ph in a.anchor:
            if unicodedata.normalize('NFC', ph) in unicodedata.normalize('NFC', slide_txt.replace('\n', ' ')):
                anchor_hits[ph] += 1
        for rp in t.iter(A + 'latin'):
            tf = rp.get('typeface')
            if tf and not tf.startswith('+'):
                fonts[tf] += 1
        # notes
        ntxt = notes_text(src, notes_part(src, part))
        if not ntxt.strip():
            warns.append(f'{tag}: no speaker notes')
        elif a.forbid_notes and not a.no_han_check and HAN.search(ntxt):
            errors.append(f'{tag}: CJK characters in notes')
        info.append(f'{tag}: {"morph" if morph is not None else "NO-MORPH " + tr_name} {dur or "-"}ms, {n_entr} entrances{custom}'
                    f'{", " + extra_fx if extra_fx else ""}, '
                    f'{len(set(names))} !! layers, {shared} shared with previous')
    # motion vocabulary: a deck that only ever morphs and fades is the template look the skill avoids
    n_sl = len(order)
    if n_sl >= 12:
        non_morph_fx = fx_census['emph'] + fx_census['path'] + fx_census['exit'] + fx_census['iterate'] + fx_census['media']
        if tr_census['morph'] / n_sl > 0.85 and not non_morph_fx and len(tr_census) <= 2:
            warns.append(f'motion monotony: {tr_census["morph"]}/{n_sl} slides Morph and no emphasis, path, exit, '
                         'letter or video effect: pick 2-3 signature techniques from references/motion-library.md')
    info.append('motion vocabulary: transitions ' + ', '.join(f'{k}×{v}' for k, v in tr_census.most_common())
                + ('; effects ' + ', '.join(f'{k}×{v}' for k, v in fx_census.most_common()) if fx_census else ''))
    lonely = sorted(n for n, k in seen_names.items() if k == 1)
    if lonely:
        warns.append(f'!! names used on only one slide (no Morph partner, fine for one-offs): {lonely[:25]}')
    # fonts
    inst = installed_fonts()
    if inst is not None:
        missing = [f for f in fonts if f.lower() not in inst]
        if missing:
            warns.append(f'fonts not installed on this machine (renders will use a fallback; ship them in fonts/): {missing}')
    # media
    media = [n for n in src.names() if n.startswith('ppt/media/')]
    hashes = Counter()
    big = []
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for m in media:
        b = src.read(m)
        hashes[hashlib.sha256(b).hexdigest()] += 1
        if Image and m.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                w, h = Image.open(io.BytesIO(b)).size
                if w > 2560:
                    big.append(f'{Path(m).name} {w}x{h}')
            except Exception:
                pass
    dupes = sum(v - 1 for v in hashes.values() if v > 1)
    if dupes:
        warns.append(f'{dupes} byte-identical media copies: run finish_dedupe.py')
    if big:
        warns.append(f'images wider than 2560 px: {big[:8]}')
    mb = src.size() / 1e6
    if mb > a.max_mb:
        errors.append(f'deck is {mb:.1f} MB > {a.max_mb} MB')
    for ph in a.anchor:
        if anchor_hits[ph] != a.anchor_count:
            warns.append(f'anchor phrase {ph!r} on {anchor_hits[ph]} slides (plan: {a.anchor_count})')
    import compat
    mode, morph_slides = a.compat, None
    for mj in (Path(a.deck).parent / 'motion.json', Path(a.deck).parent.parent / 'motion.json'):
        if mj.is_file():
            try:
                import json
                cfg = json.loads(mj.read_text(encoding='utf-8'))
            except ValueError:
                break
            mode = mode or cfg.get('compat')
            tr = cfg.get('transition', {})

            def _is_morph(n):
                t = tr.get(str(n), 'morph')
                return (t if isinstance(t, str) else t.get('type', 'morph')) == 'morph'
            nums = [int(re.sub(r'\D', '', Path(p).name)) for p in order]
            morph_slides = {i for i, n in enumerate(nums) if _is_morph(n)}
            break
    mode = mode or 'morph'
    ce, cw, ci = compat.audit([(f'pos {i:2} ({Path(p).name})', xml(src, p)) for i, p in enumerate(order, 1)], mode, morph_slides)
    errors += ce
    warns += cw
    info += ci
    if a.variety != 'off':
        import variety_audit
        ve, vw, vi = variety_audit.audit([(f'pos {i:2} ({Path(p).name})', xml(src, p)) for i, p in enumerate(order, 1)],
                                         motionlib.describe_transition, strict=a.variety == 'strict')
        errors += ve
        warns += vw
        info += vi
    if a.nomorph_render:
        ce, ci = nomorph_render(src, a.deck, a.nomorph_render, a.renders)
        errors += ce
        info += ci
    from visual_audit import audit_path
    vis = audit_path(a.deck, a.renders, a.facts)
    from craft_audit import audit_craft
    audit_craft(a.deck, a.renders, vis)
    info.extend(vis.infos)
    warns.extend(vis.warns)
    errors.extend(vis.errors)
    print(f'deck: {a.deck}  slides: {len(order)}  size: {mb:.2f} MB  media files: {len(media)}')
    print('fonts used:', dict(fonts))
    for line in info:
        print('  ' + line)
    for w in warns:
        print('WARN ', w)
    for e in errors:
        print('ERROR', e)
    print('RESULT:', 'FAIL' if errors else 'PASS', f'({len(errors)} errors, {len(warns)} warnings)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
