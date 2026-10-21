"""One command per step, so the loop is: edit deck.json -> build -> look -> fix.

  python3 studio.py route WORK [--apply] [--choose FAMILY --why "..."]
      v5.5: analyse the brief (topic, audience, tone), the research and the real assets; score every candidate
      direction; reject mismatched ones with the reason; write design/routing.md/.json (gate 3 needs it).
      --apply copies the chosen family to design/style.json as the starting point of the deck's own genome.
  python3 studio.py new WORK --kind product [--style noir-product] [--title "Tên deck"] [--fonts]
      gates.py init. WITHOUT --style (the v5.5+ way) that is all: no style.json, no starter deck.json and
      no fonts yet; it prints the next steps (fill brief.md, route, genome, then `studio.py fonts WORK`).
      WITH --style (a pack you already know fits): + design/style.json + a 5-slide starter deck.json
      (title, highlight walk, bar grow) in the style's chrome, grounds, roles and components; --fonts then
      fetches and installs the style's fonts into WORK/fonts and writes design/font-check.txt.
  python3 studio.py build WORK [--deck WORK/deck.json] [--group g1] [--no-render] [--strict]
      build_deck -> unpack -> motion -> pack -> render (renders/<group>-N, a new folder every
      round) -> check_deck with the renders (contrast and pixel checks need them).
      v5.4: without --group it builds the WHOLE deck (deck/unpacked, preview-all.pptx, renders/all-N);
      --group gN works in deck/unpacked-gN and never touches deck/unpacked.
  python3 studio.py final WORK      Phase 6: full build, finish_dedupe, clean, pack deck/final.pptx (refuses a
      partial deck), render renders/final-N, check_deck.
      Prints the layout warnings, the audit result and the contact sheets to open.
  python3 studio.py compare WORK RENDER_DIR [--ref catru|SHEET|FOLDER] [--layout stack|side] [--out WORK/design/compare-1.jpg]
      your contact sheet above the reference deck's, at the same width: the critic's view. Default reference by
      deliverable_kind (heritage: ca trù; others: the style gallery). A folder of reference images is tiled on the fly.
  python3 studio.py fonts WORK [--style noir-product]
      fetch_fonts + install + check_fonts --lang vi -> WORK/fonts, design/font-check.txt. Without --style it
      uses the deck's own design/style.json (what genome.py compile writes), else compiles design/genome.json.

Exit code: build returns the check_deck result (1 when the audit finds an ERROR; with --strict
also when build_deck printed layout warnings).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REFERENCES = SKILL / 'assets' / 'reference'


def run(args, capture=True):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=capture, text=True)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def starter(style, title, kind):
    st = json.loads((SKILL / 'assets' / 'styles' / f'{style}.json').read_text(encoding='utf-8'))
    kick = {'heritage': 'DI SẢN', 'product': 'RA MẮT', 'pitch': 'GỌI VỐN', 'business': 'BÁO CÁO',
            'education': 'BÀI HỌC', 'event': 'SỰ KIỆN'}.get(kind, 'CHỦ ĐỀ')
    cards = [
        {'type': 'card', 'name': '!!c1', 'col': [1, 4], 'y': 2.7, 'h': 3.6, 'kicker': 'MỘT', 'title': 'Ý thứ nhất',
         'desc': 'Một câu ngắn nói vì sao ý này quan trọng.'},
        {'type': 'card', 'name': '!!c2', 'col': [5, 4], 'y': 2.7, 'h': 3.6, 'kicker': 'HAI', 'title': 'Ý thứ hai',
         'desc': 'Một câu ngắn nói vì sao ý này quan trọng.'},
        {'type': 'card', 'name': '!!c3', 'col': [9, 4], 'y': 2.7, 'h': 3.6, 'kicker': 'BA', 'title': 'Ý thứ ba',
         'desc': 'Một câu ngắn nói vì sao ý này quan trọng.'},
    ]
    sig = {'type': 'rect', 'name': '!!sig', 'x': 11.2, 'y': 1.2, 'w': 1.2, 'h': 1.2, 'fill': 'accent', 'radius': 0.5,
           'alpha': 0.9}
    data = [{'label': '2022', 'value': 32}, {'label': '2023', 'value': 48}, {'label': '2024', 'value': 71}, {'label': '2025', 'value': 96}]
    return {
        'style': style,
        'title': title,
        'motion': {'default_ms': st.get('motion', {}).get('default_ms', 1300)},
        'slides': [
            {'id': 'title', 'scene': 'S1', 'notes': 'Câu mở đầu: một câu hỏi, không phải lời chào.',
             'shapes': [sig, {'type': 'heading', 'name': '!!h', 'col': [1, 9], 'y': 2.2, 'kicker': kick, 'title': title,
                              'title_role': 'display', 'sub': 'Thay bằng một câu hứa hẹn của bài nói'}]},
            {'id': 'walk1', 'scene': 'S2', 'notes': 'Ba ý chính, đi lần lượt.', 'ms': st.get('motion', {}).get('bloom_ms', 1800),
             'shapes': [{**sig, 'x': 12.0, 'y': 0.95, 'w': 0.32, 'h': 0.32},
                        {'type': 'heading', 'name': '!!h', 'col': [1, 9], 'y': 1.0, 'kicker': 'BA Ý CHÍNH', 'title': 'Một tiêu đề nói kết luận'}]
             + cards},
            {'from': 'prev', 'id': 'walk2', 'notes': 'Ý thứ hai sáng lên.',
             'set': {'!!c1': {'state': 'dim'}, '!!c2': {'state': 'lit', 'y': 2.45}, '!!c3': {'state': 'dim'}}},
            {'id': 'bars0', 'scene': 'S3', 'notes': 'Con số mở ra.', 'source': 'Nguồn: thay bằng nguồn thật (facts.md)',
             'shapes': [{**sig, 'x': 12.0, 'y': 0.95, 'w': 0.32, 'h': 0.32},
                        {'type': 'heading', 'name': '!!h', 'col': [1, 6], 'y': 1.0, 'kicker': 'TĂNG TRƯỞNG', 'title': 'Tăng gấp ba',
                         'body': 'Thay bằng số liệu thật có nguồn trong facts.md.'},
                        {'type': 'bars', 'name': '!!b', 'col': [8, 5], 'y': 1.65, 'h': 4.75, 'data': data, 'grow': 0.0}]},
            {'from': 'prev', 'id': 'bars1', 'ms': 1600, 'notes': 'Cột cuối là năm nay.',
             'set': {'!!b': {'grow': 1.0, 'highlight': 3}}},
        ],
    }


def cmd_route(a):
    """v5.5: analyse subject/audience/tone/assets, score candidates, reject mismatches, record the decision.
    --apply copies the chosen family into design/style.json (tagged "route") as the genome's starting point."""
    sys.path.insert(0, str(HERE))
    import route
    work = Path(a.work).resolve()
    try:
        dec = route.route(work, a.choose, a.why or '')
    except SystemExit as e:
        print(e)
        return 2
    print(route.render_md(dec))
    if not dec['chosen']:
        return 1
    if a.apply:
        fam = dec['chosen']
        if fam.startswith('direction:'):
            spec = json.loads((work / 'design/directions.json').read_text(encoding='utf-8'))
            d = next(x for x in spec['directions'] if f'direction:{x.get("id")}' == fam)
            fam = d.get('family')
            if not fam:
                print('the chosen direction names no "family": write design/style.json for it by hand (references/design-space.md)')
                return 0
        dst = work / 'design' / 'style.json'
        if dst.exists() and not a.force:
            print(f'{dst} exists: kept (use --force to replace it with {fam})')
            return 0
        src = next(p for p in (SKILL / 'assets' / 'styles', SKILL / 'assets' / 'styles-experimental') if (p / f'{fam}.json').is_file())
        st = json.loads((src / f'{fam}.json').read_text(encoding='utf-8'))
        st['route'] = fam
        st['name'] = f'{work.name}-{fam}'
        dst.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'design/style.json <- {fam} (routed). Now make it the subject\'s own: palette from the pictures, '
              'type, grid, layouts and motion grammar (references/design-space.md)')
    return 0


def rejected_by_routing(work, style):
    p = work / 'design' / 'routing.json'
    if not p.is_file():
        return None
    try:
        return (json.loads(p.read_text(encoding='utf-8')).get('rejected') or {}).get(style)
    except ValueError:
        return None


def cmd_new(a):
    work = Path(a.work).resolve()
    code, out = run([HERE / 'gates.py', 'init', work, '--kind', a.kind])
    print(out.strip().splitlines()[0] if out.strip() else '')
    if code:
        print(out)
        return code
    if not a.style:
        print(f'new project {work}: no style yet (v5.5+ routes it), so no design/style.json and no starter deck.json were made.\n'
              f'Next: fill brief.md (topic, audience, tone, domains), research and assets, then\n'
              f'  python3 {HERE / "studio.py"} route {work} --apply      (routing.md: chosen + rejected with reasons)\n'
              f'  write design/genome.json, python3 {HERE / "genome.py"} compile {work}/design/genome.json\n'
              f'  python3 {HERE / "studio.py"} fonts {work}               (fonts come from the routed style / genome)')
        if a.fonts:
            print('--fonts: skipped, there is no style to take fonts from yet; run `studio.py fonts WORK` after routing/genome')
        return 0
    rej = rejected_by_routing(work, a.style)
    if rej and not a.force:
        print(f'--style {a.style} was rejected by routing: {rej[0]}\n(see design/routing.md; --force to override, and write why)')
        return 2
    (work / 'design').mkdir(parents=True, exist_ok=True)
    shutil.copy(SKILL / 'assets' / 'styles' / f'{a.style}.json', work / 'design' / 'style.json')
    deck = work / 'deck.json'
    if not deck.exists() or a.force:
        spec = starter(a.style, a.title, a.kind)
        spec['style'] = 'design/style.json'
        deck.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    ad = work / 'design' / 'art-direction.md'
    txt = ad.read_text(encoding='utf-8') if ad.exists() else ''
    if 'style:' not in txt:
        ad.write_text(f'- style: {a.style} (design/style.json; edit that copy, not the pack)\n' + txt, encoding='utf-8')
    if a.fonts:
        cmd_fonts(argparse.Namespace(work=str(work), style=a.style))
    print(f'new project {work} with style {a.style}: edit deck.json, then python3 {HERE / "studio.py"} build {work}')
    return 0


def deck_style_source(work):
    """v5.6 (I26): the style to take fonts from when --style is not given: design/style.json, else design/genome.json."""
    st = work / 'design' / 'style.json'
    if st.is_file():
        return str(st)
    gp = work / 'design' / 'genome.json'
    if gp.is_file():
        sys.path.insert(0, str(HERE))
        import genome
        out = work / 'design' / 'style.json'
        out.write_text(json.dumps(genome.compile_genome(json.loads(gp.read_text(encoding='utf-8')), work), ensure_ascii=False, indent=1),
                       encoding='utf-8')
        print(f'compiled design/genome.json -> {out}')
        return str(out)
    return None


def cmd_fonts(a):
    work = Path(a.work).resolve()
    style = a.style or deck_style_source(work)
    if not style:
        print('fonts: no --style, no design/style.json and no design/genome.json: route the deck first (studio.py route WORK --apply)')
        return 2
    code, out = run([HERE / 'fetch_fonts.py', '--style', style, '--out', work / 'fonts', '--install', '--check', 'vi'])
    (work / 'design').mkdir(parents=True, exist_ok=True)
    (work / 'design' / 'font-check.txt').write_text(out, encoding='utf-8')
    print(out.strip())
    return code


def next_round(renders, group):
    nums = [int(m.group(1)) for p in renders.glob(f'{group}-*') if (m := re.fullmatch(rf'{re.escape(group)}-(\d+)', p.name))]
    return renders / f'{group}-{max(nums, default=0) + 1}'


def group_positions(spec, group):
    """1-based deck positions that belong to GROUP, or None for the whole deck.

    A slide's "group" key holds until the next slide that sets one; a deck-level
    "groups": {"g1": [first, last], ...} (inclusive positions) wins when present."""
    slides = spec.get('slides', [])
    if not group or group in ('all', 'final'):
        return None
    rng = (spec.get('groups') or {}).get(group)
    if rng:
        lo, hi = int(rng[0]), int(rng[-1])
        return [i for i in range(1, len(slides) + 1) if lo <= i <= hi]
    cur, out, tagged = None, [], False
    for i, s in enumerate(slides, 1):
        if 'group' in s:
            cur, tagged = s['group'], True
        if cur == group:
            out.append(i)
    return out if tagged else None


def cmd_build(a):
    work = Path(a.work).resolve()
    deck = Path(a.deck).resolve() if a.deck else work / 'deck.json'
    ddir = work / 'deck'
    ddir.mkdir(parents=True, exist_ok=True)
    built = ddir / 'build.pptx'
    code, out = run([HERE / 'build_deck.py', deck, '--out', built])
    print(out.strip())
    if code or not built.exists():
        return code or 1
    warned = 'WARN' in out
    spec = json.loads(deck.read_text(encoding='utf-8')) if deck.is_file() else {}
    group = a.group if a.group not in (None, '', 'all', 'final') else None
    # v5.4: deck/unpacked is ALWAYS the full deck (Phase 6 packs it); a group build works in deck/unpacked-<group>
    up = ddir / (f'unpacked-{group}' if group else 'unpacked')
    if up.exists():
        shutil.rmtree(up)
    for args in (['ooxml.py', 'unpack', built, up], ['motion.py', up]):
        c, o = run([HERE / args[0], *args[1:]])
        if c:
            print(o)
            return c
    keep = group_positions(spec, group)
    if keep is not None:   # v5.3: a group build is that group only, page numbers stay the full deck's
        if not keep:
            print(f'group {a.group!r}: no slide has "group": "{a.group}" and deck.json has no "groups" entry for it')
            return 1
        for args in (['ooxml.py', 'sequence', up, *[f'slide{i}.xml' for i in keep]], ['ooxml.py', 'clean', up]):
            c, o = run([HERE / args[0], *map(str, args[1:])])
            if c:
                print(o)
                return c
        print(f'group {a.group}: {len(keep)} of {len(spec.get("slides", []))} slides (positions {keep[0]}-{keep[-1]})')
    (ddir / f'{up.name}.json').write_text(json.dumps({'group': group or 'all', 'slides': len(keep) if keep else len(spec.get('slides', [])),
                                                      'deck_slides': len(spec.get('slides', []))}), encoding='utf-8')
    tag = group or 'all'
    if not group:
        print(f'full deck: {len(spec.get("slides", []))} slides -> {up} (Phase 6 packs this folder)')
    preview = ddir / f'preview-{tag}.pptx'
    c, o = run([HERE / 'ooxml.py', 'pack', up, preview])
    if c:
        print(o)
        return c
    if getattr(a, 'skip_check', False):   # v5.6 (I32): `final` runs ONE check, on the packed final with its renders
        return 0
    renders = None
    if not a.no_render:
        renders = next_round(work / 'renders', tag)
        r = subprocess.run(['bash', str(HERE / 'render.sh'), str(preview), str(renders)], capture_output=True, text=True)
        print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else 'render: no output')
    extra = ['--renders', str(renders)] if renders else []
    mode = (json.loads(deck.read_text(encoding='utf-8')).get('compat') or 'morph') if deck.is_file() else 'morph'
    if mode != 'morph':
        extra += ['--compat', mode]
        if renders:
            extra += ['--nomorph-render', str(renders) + '-nomorph']
    c, o = run([HERE / 'check_deck.py', preview, *extra])
    keep = [l for l in o.splitlines() if l.startswith(('WARN', 'ERROR', 'RESULT')) or 'system:' in l or 'type scale' in l]
    print('\n'.join(keep) if any(l.startswith('RESULT') for l in keep) else 'check_deck.py did not finish:\n' + o[-3000:])
    if renders:
        sheets = sorted(renders.glob('contact*.jpg'))
        print('LOOK at:', ', '.join(str(s) for s in sheets))
        print(f'then: python3 {HERE / "studio.py"} compare {work} {renders}')
    return c or (1 if a.strict and warned else 0)


def cmd_final(a):
    """Phase 6 in one step: full build -> finish_dedupe -> clean -> pack deck/final.pptx -> render renders/final-N -> check."""
    work = Path(a.work).resolve()
    a.group = None
    a.no_render = True
    a.skip_check = True
    c = cmd_build(a)
    if c and a.strict:
        return c
    up, final = work / 'deck' / 'unpacked', work / 'deck' / 'final.pptx'
    deck = Path(a.deck).resolve() if a.deck else work / 'deck.json'
    want = len(json.loads(deck.read_text(encoding='utf-8')).get('slides', [])) if deck.is_file() else 0
    have = len(list((up / 'ppt' / 'slides').glob('slide*.xml')))
    if want and have != want:
        print(f'ERROR deck/unpacked holds {have} slides, deck.json has {want}: not packing a partial deck')
        return 1
    for args in (['finish_dedupe.py', up], ['ooxml.py', 'clean', up], ['ooxml.py', 'pack', up, final]):
        c, o = run([HERE / args[0], *map(str, args[1:])])
        print(o.strip().splitlines()[-1] if o.strip() else args[0])
        if c:
            print(o)
            return c
    renders = next_round(work / 'renders', 'final')
    r = subprocess.run(['bash', str(HERE / 'render.sh'), str(final), str(renders)], capture_output=True, text=True)
    print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else 'render: no output')
    extra = ['--renders', str(renders)]
    mode = (json.loads(deck.read_text(encoding='utf-8')).get('compat') or 'morph') if deck.is_file() else 'morph'
    if mode != 'morph':
        extra += ['--compat', mode]
    c, o = run([HERE / 'check_deck.py', final, *extra])
    (work / 'deck' / 'final-check.txt').write_text(o, encoding='utf-8')
    print('check_deck (the one final check: deck/final.pptx with ' + str(renders.name) + '):')
    print('\n'.join(l for l in o.splitlines() if l.startswith(('WARN', 'ERROR', 'RESULT'))))
    print(f'final: {final} ({have} slides), renders {renders}. NEXT: deliver.py WORK --deck {final} ... then gates.py check WORK --gate 6')
    return c


REF_BY_KIND = {'heritage': 'catru'}   # v5.4: the ca trù sheet is the default only for heritage decks


def deck_kind(work):
    import re as _re
    b = (work / 'brief.md').read_text(encoding='utf-8') if (work / 'brief.md').is_file() else ''
    m = _re.search(r'^\s*-\s*deliverable_kind\s*:\s*([\w-]+)', b, _re.M)
    return m.group(1).lower() if m else 'other'


def reference_sheets(work, ref, tmpdir):
    """(paths, label). ref: None (by deck kind), a name in assets/reference, a contact sheet, or a folder of images
    (tiled on the fly, so a folder of a designer's reference slides works too)."""
    if ref is None:
        kind = deck_kind(work)
        name = REF_BY_KIND.get(kind)
        if name:
            return sorted(REFERENCES.glob(f'{name}*contact*.jpg')), f'REFERENCE ({name}, default for {kind})'
        return [REFERENCES / 'styles-gallery.jpg'], f'STYLE GALLERY (no reference deck for kind {kind!r}: pass --ref PATH)'
    p = Path(ref)
    if p.is_file():
        return [p], f'REFERENCE {p.name}'
    if p.is_dir():
        sheets = sorted(p.glob('*contact*.jpg'))
        if sheets:
            return sheets, f'REFERENCE {p.name}'
        import contact_sheet
        files = contact_sheet.collect([p])
        if not files:
            return [], ''
        out = Path(tmpdir) / 'ref-contact.jpg'
        contact_sheet.sheet(files, out, 4, 480, 'none', {})
        return [out], f'REFERENCE {p.name} ({len(files)} images)'
    return sorted(REFERENCES.glob(f'{ref}*contact*.jpg')), f'REFERENCE ({ref})'


def cmd_compare(a):
    import tempfile
    from PIL import Image, ImageDraw
    work = Path(a.work).resolve()
    mine = sorted(Path(a.renders).glob('contact*.jpg'))
    if not mine:
        print('no contact*.jpg in', a.renders)
        return 1
    tmp = tempfile.mkdtemp(prefix='cmp-')
    sys.path.insert(0, str(HERE))
    refs, ref_label = reference_sheets(work, a.ref, tmp)
    if not refs:
        print('no reference contact sheets or images found for', a.ref)
        return 1
    side = getattr(a, 'layout', 'stack') == 'side'
    width = 1200 if side else 1600
    cols = []
    for label, path in [('YOUR DECK', mine[0]), (ref_label, refs[0])]:
        im = Image.open(path).convert('RGB')
        im = im.resize((width, round(im.height * width / im.width)))
        bar = Image.new('RGB', (width, 44), (24, 24, 24))
        ImageDraw.Draw(bar).text((16, 12), f'{label}  {path.name}', fill=(235, 235, 235))
        cols.append([bar, im])
    out = Path(a.out) if a.out else next_free(work / 'design', 'compare')
    if side:   # v5.4: the two sheets next to each other, top-aligned
        hh = max(sum(t.height for t in c) for c in cols)
        canvas = Image.new('RGB', (2 * width + 24, hh), (24, 24, 24))
        for k, c in enumerate(cols):
            y = 0
            for t in c:
                canvas.paste(t, (k * (width + 24), y))
                y += t.height
    else:
        tiles = cols[0] + cols[1]
        canvas = Image.new('RGB', (width, sum(t.height for t in tiles)), (24, 24, 24))
        y = 0
        for t in tiles:
            canvas.paste(t, (0, y))
            y += t.height
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=88)
    print('compare sheet ->', out, f'(against: {ref_label})')
    print('Ask: does it read as one designed system (ground, chrome, type scale)? is the signature present?'
          ' is every slide as rich at 1x and still rewarding up close? is anything flat, generic or crowded?')
    return 0


def next_free(folder, stem):
    n = 1
    while (folder / f'{stem}-{n}.jpg').exists():
        n += 1
    return folder / f'{stem}-{n}.jpg'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('new')
    s.add_argument('work')
    s.add_argument('--kind', default='other')
    s.add_argument('--style', default=None, choices=sorted(p.stem for p in (SKILL / 'assets' / 'styles').glob('*.json')),
                   help='optional (v5.5): leave it out and run "studio.py route WORK --apply" once the brief and assets exist')
    s.add_argument('--title', default='Tiêu đề bài nói')
    s.add_argument('--fonts', action='store_true', help='with --style only: fetch the style\'s fonts (else run `studio.py fonts WORK` after routing)')
    s.add_argument('--force', action='store_true', help='overwrite an existing deck.json')
    s = sub.add_parser('route')
    s.add_argument('work')
    s.add_argument('--choose')
    s.add_argument('--why')
    s.add_argument('--apply', action='store_true')
    s.add_argument('--force', action='store_true')
    s = sub.add_parser('build')
    s.add_argument('work')
    s.add_argument('--deck')
    s.add_argument('--group', default=None, help='build only this group (g1, g2 ...); default: the whole deck')
    s.add_argument('--no-render', action='store_true')
    s.add_argument('--strict', action='store_true')
    s = sub.add_parser('final')
    s.add_argument('work')
    s.add_argument('--deck')
    s.add_argument('--strict', action='store_true')
    s = sub.add_parser('compare')
    s.add_argument('work')
    s.add_argument('renders')
    s.add_argument('--ref', default=None)
    s.add_argument('--out')
    s.add_argument('--layout', choices=('stack', 'side'), default='stack', help='stack (default) or side by side')
    s = sub.add_parser('fonts')
    s.add_argument('work')
    s.add_argument('--style', default=None, help='a pack name or style.json; default: design/style.json, else design/genome.json')
    a = ap.parse_args(argv)
    return {'new': cmd_new, 'route': cmd_route, 'build': cmd_build, 'final': cmd_final, 'compare': cmd_compare, 'fonts': cmd_fonts}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
