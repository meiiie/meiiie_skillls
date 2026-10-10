"""One command per step, so the loop is: edit deck.json -> build -> look -> fix.

  python studio.py new WORK --kind product --style noir-product [--title "Tên deck"] [--fonts]
      gates.py init + design/style.json + a 5-slide starter deck.json (title, highlight walk, bar grow)
      that already uses the style's chrome, grounds, roles and components. --fonts fetches and
      installs the style's fonts into WORK/fonts and writes design/font-check.txt.
  python studio.py build WORK [--deck WORK/deck.json] [--group g1] [--no-render] [--strict]
      build_deck -> unpack -> motion -> pack -> render (renders/<group>-N, a new folder every
      round) -> check_deck with the renders (contrast and pixel checks need them).
      Prints the layout warnings, the audit result and the contact sheets to open.
  python studio.py compare WORK RENDER_DIR [--ref catru|PATH] [--out WORK/design/compare-1.jpg]
      your contact sheet above the reference deck's, at the same width: the critic's view.
  python studio.py fonts WORK --style noir-product
      fetch_fonts + install + check_fonts --lang vi -> WORK/fonts, design/font-check.txt

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


def cmd_new(a):
    work = Path(a.work).resolve()
    code, out = run([HERE / 'gates.py', 'init', work, '--kind', a.kind])
    print(out.strip().splitlines()[0] if out.strip() else '')
    if code:
        print(out)
        return code
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
    print(f'new project {work} with style {a.style}: edit deck.json, then python {HERE / "studio.py"} build {work}')
    return 0


def cmd_fonts(a):
    work = Path(a.work).resolve()
    code, out = run([HERE / 'fetch_fonts.py', '--style', a.style, '--out', work / 'fonts', '--install', '--check', 'vi'])
    (work / 'design').mkdir(parents=True, exist_ok=True)
    (work / 'design' / 'font-check.txt').write_text(out, encoding='utf-8')
    print(out.strip())
    return code


def next_round(renders, group):
    nums = [int(m.group(1)) for p in renders.glob(f'{group}-*') if (m := re.fullmatch(rf'{re.escape(group)}-(\d+)', p.name))]
    return renders / f'{group}-{max(nums, default=0) + 1}'


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
    up = ddir / 'unpacked'
    if up.exists():
        shutil.rmtree(up)
    for args in (['ooxml.py', 'unpack', built, up], ['motion.py', up]):
        c, o = run([HERE / args[0], *args[1:]])
        if c:
            print(o)
            return c
    preview = ddir / f'preview-{a.group}.pptx'
    c, o = run([HERE / 'ooxml.py', 'pack', up, preview])
    if c:
        print(o)
        return c
    renders = None
    if not a.no_render:
        renders = next_round(work / 'renders', a.group)
        r = subprocess.run(['bash', str(HERE / 'render.sh'), str(preview), str(renders)], capture_output=True, text=True)
        print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else 'render: no output')
    extra = ['--renders', str(renders)] if renders else []
    c, o = run([HERE / 'check_deck.py', preview, *extra])
    keep = [l for l in o.splitlines() if l.startswith(('WARN', 'ERROR', 'RESULT')) or 'system:' in l or 'type scale' in l]
    print('\n'.join(keep) if any(l.startswith('RESULT') for l in keep) else 'check_deck.py did not finish:\n' + o[-3000:])
    if renders:
        sheets = sorted(renders.glob('contact*.jpg'))
        print('LOOK at:', ', '.join(str(s) for s in sheets))
        print(f'then: python {HERE / "studio.py"} compare {work} {renders}')
    return c or (1 if a.strict and warned else 0)


def cmd_compare(a):
    from PIL import Image, ImageDraw
    work = Path(a.work).resolve()
    mine = sorted(Path(a.renders).glob('contact*.jpg'))
    if not mine:
        print('no contact*.jpg in', a.renders)
        return 1
    ref = Path(a.ref) if a.ref and Path(a.ref).exists() else REFERENCES
    refs = sorted(ref.glob('*contact*.jpg')) if ref.is_dir() else [ref]
    if a.ref and not Path(a.ref).exists():
        refs = sorted(REFERENCES.glob(f'{a.ref}*contact*.jpg'))
    if not refs:
        print('no reference contact sheets found in', ref)
        return 1
    width = 1600
    tiles = []
    for label, path in [('YOUR DECK', mine[0]), ('REFERENCE', refs[0])]:
        im = Image.open(path).convert('RGB')
        im = im.resize((width, round(im.height * width / im.width)))
        bar = Image.new('RGB', (width, 44), (24, 24, 24))
        ImageDraw.Draw(bar).text((16, 12), f'{label}  {path.name}', fill=(235, 235, 235))
        tiles += [bar, im]
    out = Path(a.out) if a.out else next_free(work / 'design', 'compare')
    canvas = Image.new('RGB', (width, sum(t.height for t in tiles)), (24, 24, 24))
    y = 0
    for t in tiles:
        canvas.paste(t, (0, y))
        y += t.height
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=88)
    print('compare sheet ->', out)
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
    s.add_argument('--style', required=True, choices=sorted(p.stem for p in (SKILL / 'assets' / 'styles').glob('*.json')))
    s.add_argument('--title', default='Tiêu đề bài nói')
    s.add_argument('--fonts', action='store_true')
    s.add_argument('--force', action='store_true', help='overwrite an existing deck.json')
    s = sub.add_parser('build')
    s.add_argument('work')
    s.add_argument('--deck')
    s.add_argument('--group', default='g1')
    s.add_argument('--no-render', action='store_true')
    s.add_argument('--strict', action='store_true')
    s = sub.add_parser('compare')
    s.add_argument('work')
    s.add_argument('renders')
    s.add_argument('--ref', default=None)
    s.add_argument('--out')
    s = sub.add_parser('fonts')
    s.add_argument('work')
    s.add_argument('--style', required=True)
    a = ap.parse_args(argv)
    return {'new': cmd_new, 'build': cmd_build, 'compare': cmd_compare, 'fonts': cmd_fonts}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
