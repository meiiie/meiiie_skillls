"""v5.3: geometry variety, slim gates, signature moments, directions, Codex lint, bug fixes."""
import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

import gates
import studio
import variety_audit


def run(fn, *args):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            r = fn(*args)
            code = 0 if r in (None, True) else (r if isinstance(r, int) else 1)
        except SystemExit as e:
            code = e.code or 0
    return code, buf.getvalue()


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


# ---------- geometry variety (rendered boxes, not layout labels)

def split_slide(png, i, side='right'):
    img_x = 6.5 if side == 'right' else 0.0
    txt_x = 0.8 if side == 'right' else 7.4
    return {'notes': 'n', 'shapes': [
        {'type': 'image', 'name': f'p{i}', 'path': str(png), 'x': img_x, 'y': 0, 'w': 6.833, 'h': 7.5},
        {'type': 'text', 'name': f't{i}', 'text': f'Tiêu đề số {i} khá dài', 'x': txt_x, 'y': 2.5, 'w': 5, 'h': 1, 'size': 36},
        {'type': 'text', 'name': f'b{i}', 'text': 'Một đoạn mô tả có đủ chữ để không bị coi là trống trơn.', 'x': txt_x, 'y': 3.8,
         'w': 5, 'h': 1.2, 'size': 16}]}


def other_slide(png, i):
    return {'notes': 'n', 'shapes': [
        {'type': 'image', 'name': f'p{i}', 'path': str(png), 'x': 3.0, 'y': 0.6, 'w': 7.3, 'h': 4.6},
        {'type': 'text', 'name': f't{i}', 'text': f'Một bố cục khác {i}', 'x': 1.5, 'y': 5.6, 'w': 10, 'h': 1, 'size': 32}]}


def test_text_left_photo_right_on_4_slides_fails(build, png):
    _, roots, _ = build({'slides': [split_slide(png, i) for i in range(4)] + [other_slide(png, 9)]})
    errs, _, info = variety_audit.audit([(f'pos {i}', r) for i, r in enumerate(roots, 1)], lambda r: ('fade', 700))
    assert any('text-left / photo-right split on 4 slides' in e for e in errs), errs
    assert any('text-left/photo-right on 4' in i for i in info)


def test_three_splits_and_mirrors_pass(build, png):
    slides = [split_slide(png, i) for i in range(3)] + [split_slide(png, 5, 'left')] + [other_slide(png, 9)]
    _, roots, _ = build({'slides': slides})
    errs, _, _ = variety_audit.audit([(f'pos {i}', r) for i, r in enumerate(roots, 1)], lambda r: ('fade', 700))
    assert not [e for e in errs if 'geometry' in e], errs


def test_geometry_ignores_layout_labels_and_full_bleed_grounds(build, png):
    # a full-bleed picture is a ground, not a "photo right"
    s = {'notes': 'n', 'shapes': [{'type': 'image', 'name': 'g', 'path': str(png), 'x': 0, 'y': 0, 'w': 13.333, 'h': 7.5},
                                  {'type': 'text', 'name': 't', 'text': 'Chữ bên trái trên nền ảnh', 'x': 0.8, 'y': 3, 'w': 5, 'h': 1, 'size': 36}]}
    _, roots, _ = build({'slides': [s] * 5})
    for r in roots:
        assert variety_audit.geometry(r)[1] is None


def test_geometry_tells_a_native_diagram_from_a_bare_title(build):
    title = {'notes': 'n', 'shapes': [{'type': 'text', 'name': 't', 'text': 'Một tiêu đề', 'x': 1, 'y': 3, 'w': 11.3, 'h': 1, 'size': 40}]}
    diagram = {'notes': 'n', 'shapes': [{'type': 'rect', 'name': 'd', 'x': 3, 'y': 1.5, 'w': 7, 'h': 4, 'fill': '#1464F4'},
                                        {'type': 'text', 'name': 't', 'text': 'Một tiêu đề', 'x': 1, 'y': 3, 'w': 11.3, 'h': 1, 'size': 40}]}
    _, roots, _ = build({'slides': [title, diagram]})
    assert variety_audit.geometry(roots[0])[0] != variety_audit.geometry(roots[1])[0]


# ---------- gates: table parsing, render rounds, research counting

def test_table_reports_rows_broken_across_lines():
    md = '| # | scene |\n|---|---|\n| 1 | S1 |\n| 2 | S1 tiêu đề\n xuống dòng |\n| 3 | S2 |\n'
    head, rows = gates.table(md, ['#', 'scene'])
    assert len(rows) == 3 and rows.bad and any('broken across lines' in b for b in rows.bad)


def test_gate4_fails_loudly_on_a_malformed_storyboard(tmp_path):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'other'])
    write(work / 'storyboard.md', '| # | scene | keyframe role | layout | layers | visual | on-slide text | source | words |\n'
          '|---|---|---|---|---|---|---|---|---|\n| 1 | S1 | K1 | a | !!x | drawn:x | hai\nba | - | 10 |\n| 2 | S1 | K2 | a | !!x | drawn:x | b | - | 10 |\n')
    code, out = run(gates.g4, work)
    assert any('FAIL' in l and 'malformed' in l for l in out.splitlines()), out


def test_latest_round_is_numeric_and_ignores_files(tmp_path):
    r = tmp_path / 'renders'
    for n in ('final-2', 'final-10', 'final-9'):
        (r / n).mkdir(parents=True)
    (r / 'final-preview-SIMULATION.mp4').write_bytes(b'x')
    assert gates.latest_round(r, 'final').name == 'final-10'


def test_do_not_say_list_is_not_counted_as_facts(tmp_path):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'business'])
    write(work / 'research/facts.md', '# Facts\n- (S1) Filing — https://example.org/20f\n\n## Facts\n'
          '| # | fact | source | tag |\n|---|---|---|---|\n| 1.1 | doanh thu | S1 | [verified] |\n\n'
          '## Do not say\n- "largest EV maker" (S1) https://example.org/a\n- "profitable" (S1)\n- "no losses" https://example.org/b\n')
    code, out = run(gates.g1, work)
    assert '1 sourced fact rows' in out, out


def test_unsourced_fact_row_fails_and_counts_are_advisory(tmp_path):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'business'])
    write(work / 'research/facts.md', '- (S1) Filing — https://example.org/20f\n| # | fact | source | tag |\n|---|---|---|---|\n'
          '| 1.1 | a | S1 | [verified] |\n| 1.2 | b | | [claim] |\n\n## Do not say\n- x\n')
    code, out = run(gates.g1, work)
    fails = [l for l in out.splitlines() if l.strip().startswith('FAIL')]
    assert any('every fact table row has a source' in l for l in fails), out
    assert not any('fact rows (habit' in l for l in fails) and any(l.strip().startswith('WARN') and 'habit' in l for l in out.splitlines())


def test_init_knows_company_profile(tmp_path):
    code, _ = run(gates.main, ['init', str(tmp_path / 'c'), '--kind', 'company-profile'])
    assert code == 0 and (tmp_path / 'c/design/signature-moments.md').is_file() and (tmp_path / 'c/design/directions.md').is_file()


# ---------- assets: uncredited files, AI labels, contact manifest

def test_gate2_needs_credits_for_every_file_and_ai_labels(tmp_path, png):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'other'])
    shutil.copy(png, work / 'assets/a.png')
    (work / 'assets/gen').mkdir(exist_ok=True)
    shutil.copy(png, work / 'assets/gen/tex.jpg')
    write(work / 'assets/CREDITS.md', '| file | why accurate | source page | licence |\n|---|---|---|---|\n'
          '| a.png | photo of the thing, fact 1.1 | https://commons.wikimedia.org/x | CC BY 4.0 |\n')
    code, out = run(gates.g2, work)
    assert any('FAIL' in l and 'has a CREDITS row (1 without)' in l for l in out.splitlines()), out
    write(work / 'assets/CREDITS.md', (work / 'assets/CREDITS.md').read_text() +
          '| gen/tex.jpg | ground texture, no claim | gen/tex.json | AI-generated (no third-party rights claimed; label as AI) |\n')
    code, out = run(gates.g2, work)
    assert any('FAIL' in l and 'sidecar' in l for l in out.splitlines()), out
    write(work / 'assets/gen/tex.json', '{"ai_generated": true}')
    code, out = run(gates.g2, work)
    assert not [l for l in out.splitlines() if l.strip().startswith('FAIL')], out


def test_contact_manifest_beats_mtimes(tmp_path, png):
    import contact_sheet
    work = tmp_path / 'w'
    (work / 'assets').mkdir(parents=True)
    shutil.copy(png, work / 'assets/a.png')
    run(contact_sheet.main, [str(work / 'assets'), '--out', str(work / 'assets/contact.jpg')]) if hasattr(contact_sheet, 'main') else None
    assert (work / 'assets/contact.json').is_file()
    import os
    os.utime(work / 'assets/a.png', None)   # touched later, same content: still fresh
    ok, why = gates.contact_fresh(work, gates.asset_files(work))
    assert ok, why
    shutil.copy(png, work / 'assets/b.png')
    ok, why = gates.contact_fresh(work, gates.asset_files(work))
    assert not ok and 'b.png' in why


# ---------- creative floor: directions, signature moments, style shifts

DIRS = '''## Direction A — Xưởng trắng
- ground: white drafting paper, palette #FFFFFF #1464F4 #0B1B33, Swiss grid with Anatomy machines as heroes, type Be Vietnam Pro, slow camera pushes along the line, hero machine
## Direction B — Đêm cao tốc
- ground: noir navy with light trails, palette #050A14 #4D8DFF #F2F4F8, kinetic numbers huge in Space Grotesk, push cuts and fast type, light streaks as the signature
## Direction C — Hồ sơ kiểm toán
- ground: cream paper editorial, palette #F3EEE3 #C8102E #1A1A1A, serif headlines with red pencil marks, quiet wipes like turning pages of an audited annual filing, red marks circle each loss
## Decision
- chosen: A, with B for hook and close
- why: the subject is a factory and the machines read best on white paper while the night look carries the hook
'''


def test_directions_need_three_different_and_a_thumbnail(tmp_path):
    work = tmp_path / 'w'
    (work / 'design').mkdir(parents=True)
    write(work / 'design/directions.md', DIRS)
    errs, _ = gates.directions_report(work)
    assert errs == ['design/directions.jpg missing (3 thumbnails side by side: python3 directions.py WORK)']
    write(work / 'design/directions.md', DIRS.replace('#050A14 #4D8DFF #F2F4F8', '#FFFFFF #1464F4 #0B1B33'))
    errs, _ = gates.directions_report(work)
    assert any('variations' in e for e in errs)


def test_directions_py_writes_sheet_and_md(tmp_path, png):
    import directions
    work = tmp_path / 'w'
    (work / 'design').mkdir(parents=True)
    shutil.copy(png, work / 'p.png')
    spec = {'directions': [
        {'id': 'A', 'name': 'Xưởng trắng', 'composition': 'swiss-grid', 'palette': ['#FFFFFF', '#1464F4', '#0B1B33'], 'image': 'p.png', 'title': 'Một', 'number': '300k'},
        {'id': 'B', 'name': 'Đêm', 'composition': 'full-bleed', 'palette': ['#050A14', '#4D8DFF', '#F2F4F8'], 'image': 'p.png', 'title': 'Hai'},
        {'id': 'C', 'name': 'Kiểm toán', 'composition': 'editorial', 'palette': ['#F3EEE3', '#C8102E', '#1A1A1A'], 'title': 'Ba'}],
        'chosen': 'A', 'why': 'the subject is a factory and machines read best on white paper'}
    write(work / 'design/directions.json', json.dumps(spec))
    run(directions.main, [str(work)])
    assert (work / 'design/directions.jpg').is_file()
    assert '## Direction B' in (work / 'design/directions.md').read_text()


def sig_table(rows):
    return ('| # | moment | tool | mechanism | facts | film | editable | slides |\n|---|---|---|---|---|---|---|---|\n' +
            ''.join(f'| M{i} | {m} | {t} | {mech} | 1.1 | {film} | {ed} | 3 |\n' for i, (m, t, mech, film, ed) in enumerate(rows, 1)))


MECH = 'a coil becomes a body in four shops and the lit part is the station working now'


def sig_work(tmp_path):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'other'])
    write(work / 'research/facts.md', '- (S1) x — https://example.org\n| # | fact | source | tag |\n|---|---|---|---|\n| 1.1 | a | S1 | [verified] |\n')
    return work


def test_signature_plan_needs_two_hand_built_and_no_cliche(tmp_path):
    work = sig_work(tmp_path)
    write(work / 'design/signature-moments.md', sig_table([('Line', 'anatomy', MECH, 'f.mp4', 'f.json'),
                                                           ('Flow', 'diagram_video', MECH, 'g.mp4', '!!g')]))
    errs, _ = gates.signature_report(work)
    assert any('1 hand-built' in e for e in errs)
    write(work / 'design/signature-moments.md', sig_table([('Line', 'anatomy', MECH, 'f.mp4', 'f.json'),
                                                           ('Knowledge books', 'manim', MECH, 'g.mp4', '!!g')]))
    errs, _ = gates.signature_report(work)
    assert any('stock metaphor' in e for e in errs)
    write(work / 'design/signature-moments.md', sig_table([('Line', 'anatomy', MECH, 'f.mp4', 'f.json'),
                                                           ('Pack', 'manim', MECH, 'g.mp4', '!!g')]))
    assert gates.signature_report(work)[0] == []


@pytest.mark.skipif(shutil.which('ffmpeg') is None, reason='ffmpeg')
def test_signature_films_must_move_and_be_embedded(tmp_path, build, png):
    work = sig_work(tmp_path)
    film = work / 'assets/film'
    film.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=10:duration=4',
                    '-pix_fmt', 'yuv420p', str(film / 'a.mp4')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', str(png), '-t', '4', '-r', '10', '-vf', 'scale=320:160',
                    '-pix_fmt', 'yuv420p', str(film / 'b.mp4')], check=True)
    for n in ('a', 'b'):
        shutil.copy(png, film / f'{n}.poster.png')
    write(film / 'a.shapes.json', '{}')
    write(work / 'design/signature-moments.md', sig_table([('Line', 'anatomy', MECH, 'assets/film/a.mp4', 'assets/film/a.shapes.json'),
                                                           ('Pack', 'manim', MECH, 'assets/film/b.mp4', '!!cap')]))
    errs, _ = gates.signature_report(work, 'film')
    assert any('still, not a film' in e and 'b.mp4' in e for e in errs), errs
    pptx, _, _ = build({'slides': [{'notes': 'n', 'shapes': [
        {'type': 'video', 'name': '!!film', 'path': str(film / 'a.mp4'), 'poster': str(png), 'x': 1, 'y': 1, 'w': 6, 'h': 3.4},
        {'type': 'rect', 'name': '!!cap', 'x': 8, 'y': 1, 'w': 1, 'h': 1, 'fill': '#1464F4'}]}]})
    errs, info = gates.signature_report(work, 'final', pptx)
    assert any('b.mp4 is not embedded' in e for e in errs) and not any('a.mp4 is not embedded' in e for e in errs), errs


def test_style_shift_required_on_20_plus_slides(tmp_path):
    work = tmp_path / 'w'
    work.mkdir()
    write(work / 'deck.json', json.dumps({'style': 'swiss-blue', 'slides': [{} for _ in range(22)]}))
    ok, txt = gates.style_shift_report(work, [])
    assert ok is False
    spec = {'style': 'swiss-blue', 'slides': [{}] * 10 + [{'style': 'noir-product'}] + [{}] * 11}
    write(work / 'deck.json', json.dumps(spec))
    assert gates.style_shift_report(work, [])[0] is True


def test_numbers_on_slides_need_fact_ids(tmp_path):
    work = sig_work(tmp_path)
    write(work / 'storyboard.md', '| # | scene | keyframe role | layout | layers | visual | on-slide text | source | words |\n'
          '|---|---|---|---|---|---|---|---|---|\n| 1 | S1 | K1 | a | !!x | drawn:x | 300.000 xe mỗi năm | - | 10 |\n'
          '| 2 | S1 | K2 | a | !!x | drawn:x | 300.000 xe mỗi năm | 1.1 | 10 |\n')
    code, out = run(gates.g4, work)
    assert any('FAIL' in l and 'number on the slide cites a fact ID (1 without)' in l for l in out.splitlines()), out


# ---------- studio --group, upto 5

def test_group_positions():
    spec = {'slides': [{'group': 'g1'}, {}, {'group': 'g2'}, {}, {}]}
    assert studio.group_positions(spec, 'g2') == [3, 4, 5]
    assert studio.group_positions({'slides': [{}] * 6, 'groups': {'g1': [2, 4]}}, 'g1') == [2, 3, 4]
    assert studio.group_positions({'slides': [{}] * 3}, 'g1') is None   # untagged deck: whole deck, as before


def test_studio_build_group_builds_only_that_group(tmp_path):
    work = tmp_path / 'w'
    run(studio.main, ['new', str(work), '--kind', 'product', '--style', 'noir-product', '--title', 'Thử'])
    spec = json.loads((work / 'deck.json').read_text())
    spec['slides'][0]['group'] = 'g1'
    spec['slides'][2]['group'] = 'g2'
    (work / 'deck.json').write_text(json.dumps(spec, ensure_ascii=False))
    code, out = run(studio.main, ['build', str(work), '--group', 'g2', '--no-render'])
    import zipfile
    z = zipfile.ZipFile(work / 'deck/preview-g2.pptx')
    n = len([x for x in z.namelist() if x.startswith('ppt/slides/slide') and x.endswith('.xml')])
    assert n == len(spec['slides']) - 2, out


def test_upto_runs_gate5_for_rendered_groups(tmp_path):
    work = tmp_path / 'w'
    run(gates.main, ['init', str(work), '--kind', 'other'])
    (work / 'renders/g1-1').mkdir(parents=True)
    (work / 'renders/g2-3').mkdir(parents=True)
    assert gates.groups_with_renders(work) == ['g1', 'g2']
    code, out = run(gates.main, ['check', str(work), '--upto', '5'])
    assert '== GATE 5 group g1' in out and '== GATE 5 group g2' in out


# ---------- Codex prompt lint, Anatomy fragment, MPO

def test_codex_lint():
    import gen_assets_codex as g
    assert g.lint('brushed aluminium sheet under cool white light, faint blue reflections, no logos, no text') == []
    assert g.lint('a stack of books and a lightbulb glowing on a desk at night, cinematic')
    assert g.lint('the real VinFast factory floor with workers, photo', brands=['VinFast'])
    assert any('brand' in p for p in g.lint('an electric SUV by VinFast on a wet road at dusk', kind='plate', brands=['VinFast']))
    assert any('too short' in p for p in g.lint('steel texture'))


def test_anatomy_fragment_is_inches_in_region():
    import anatomy_film
    doc = {'width': 100, 'height': 50, 'shapes': [
        {'kind': 'path', 'pts': [[0, 0], [100, 0], [100, 50]], 'closed': True, 'fill': 'rgb(20, 100, 244)', 'fillOpacity': 1},
        {'kind': 'circle', 'cx': 50, 'cy': 25, 'r': 5, 'fill': '#FFFFFF', 'stroke': '#000', 'strokeWidth': 1},
        {'kind': 'path', 'pts': [[0, 0], [1, 1]], 'fill': 'none', 'stroke': 'rgba(0,0,0,0)', 'strokeWidth': 1}]}
    frag, (ox, oy, s) = anatomy_film.to_fragment(doc, (1, 1, 10, 5), '!!fig')
    assert frag['type'] == 'group' and len(frag['shapes']) == 2
    poly = frag['shapes'][0]
    assert poly['fill'] == '#1464F4' and poly['points'][0] == [1.0, 1.0] and poly['points'][1] == [11.0, 1.0]
    assert frag['shapes'][1]['type'] == 'ellipse' and frag['shapes'][1]['line_width'] >= 0.35


def test_mpo_and_exif_are_made_ppt_safe(tmp_path, build):
    from PIL import Image
    im = Image.new('RGB', (300, 100), (200, 30, 30))
    ex = im.getexif()
    ex[0x0112] = 6   # rotate 90 CW on display
    p = tmp_path / 'rot.jpg'
    im.save(p, exif=ex)
    import build_deck
    safe = build_deck.ppt_safe(p)
    assert safe != p and Image.open(safe).size == (100, 300)
    import fetch_commons
    out, note = fetch_commons.normalise_image(p.read_bytes(), tmp_path / 'kept.jpg')
    assert Image.open(out).size == (100, 300) and 'EXIF' in note
