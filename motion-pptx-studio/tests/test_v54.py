"""v5.4: full-deck builds, deck-level gate 5, gate regex fixes, bookends, still pages, inline styles,
magazine/collage components, legibility audit (scrims, caps body), cutout and preview fixes."""
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

from conftest import NS, SKILL, named

SCRIPTS = SKILL / 'scripts'
P_NS, A_NS, R_NS = NS['p'], NS['a'], NS['r']
EMU_W, EMU_H = 12192000, 6858000


def call(fn, *args):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            r = fn(*args)
            code = r if isinstance(r, int) else 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, buf.getvalue()


def photo(path, size=(320, 200), colour=(90, 120, 160)):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', size, colour)
    d = ImageDraw.Draw(im)
    for x in range(0, size[0], 16):
        d.line([(x, 0), (x, size[1])], fill=(230, 200, 120), width=3)
    im.save(path)
    return path


# ------------------------------------------------------------------ bug 1: studio build = whole deck

def grouped_deck(work, png):
    work.mkdir(parents=True, exist_ok=True)
    slides = []
    for i in range(6):
        slides.append({'id': f's{i}', 'group': 'g1' if i < 3 else 'g2', 'scene': f'S{i}', 'bg': '#202020',
                       'shapes': [{'type': 'text', 'name': 't', 'text': f'Trang {i + 1}', 'x': 1, 'y': 1, 'w': 6, 'h': 1, 'size': 30,
                                   'color': '#FFFFFF'}]})
    (work / 'deck.json').write_text(json.dumps({'title': 't', 'slides': slides}), encoding='utf-8')


def count_slides(d):
    return len(list((d / 'ppt' / 'slides').glob('slide*.xml')))


def test_build_without_group_is_the_whole_deck_and_group_builds_leave_it_alone(tmp_path, png):
    import studio
    work = tmp_path / 'w'
    grouped_deck(work, png)
    code, out = call(studio.main, ['build', str(work), '--no-render'])
    assert (work / 'deck' / 'preview-all.pptx').exists(), out
    assert count_slides(work / 'deck' / 'unpacked') == 6
    assert 'full deck: 6 slides' in out
    code, out = call(studio.main, ['build', str(work), '--group', 'g2', '--no-render'])
    assert count_slides(work / 'deck' / 'unpacked-g2') == 3
    assert count_slides(work / 'deck' / 'unpacked') == 6          # Phase 6 still packs the full deck
    assert (work / 'deck' / 'preview-g2.pptx').exists()
    assert json.loads((work / 'deck' / 'unpacked-g2.json').read_text())['group'] == 'g2'


def test_gate5_whole_deck_needs_a_current_full_build(tmp_path, png):
    import gates
    import studio
    work = tmp_path / 'w'
    grouped_deck(work, png)
    assert not call(gates.g5_deck, work)[0] or True
    code, out = call(gates.g5_deck, work)
    assert 'FAIL deck/preview-all.pptx exists' in out
    call(studio.main, ['build', str(work), '--no-render'])
    code, out = call(gates.g5_deck, work)
    assert 'PASS preview-all.pptx has every slide (6 of 6)' in out
    assert 'PASS preview-all.pptx is newer than deck.json' in out


def test_upto_prints_a_summary_and_stop_on_fail_stops(tmp_path):
    import gates
    work = tmp_path / 'w'
    call(gates.main, ['init', str(work), '--kind', 'product'])
    code, out = call(gates.main, ['check', str(work), '--upto', '2'])
    assert '== SUMMARY:' in out and 'first FAIL: gate 0' in out
    code, out = call(gates.main, ['check', str(work), '--upto', '2', '--stop-on-fail'])
    assert 'GATE 1' not in out and code == 1


# ------------------------------------------------------------------ gate regexes (bugs 8, 9, 10)

@pytest.mark.parametrize('text,real', [('domain photo of a train', True), ('aperture f/8, Airbus hangar', True),
                                       ('hand-drawn map', False), ('paper texture, own work', False),
                                       ('AI-generated plate', False), ('made with AI (Codex)', False)])
def test_gate2_real_photo_words_are_whole_words(text, real):
    import gates
    assert (not gates.NOT_REAL.search(text) and not gates.AI_WORD.search(text)) is real


def test_gate3_motif_section_is_not_the_signature_heading_and_negation_is_dropped():
    import gates
    ad = ('## Signature (one motif that returns)\n- one\n\n## Motifs and textures\n- paper grain\n- red thread\n- seal stamp\n'
          '## Motion vocabulary\n- never fly, no spin; zoom on numbers\n- drift the photo\n')
    assert len(gates.items(gates.section(ad, r'motifs?|textures?', start=True))) == 3
    txt = gates.strip_negated(' '.join(gates.items(gates.section(ad, r'motion vocabulary')))).lower()
    assert 'zoom' in txt and 'drift' in txt and 'fly' not in txt and 'spin' not in txt


def test_gate2_names_credit_rows_outside_the_table():
    import gates
    cr = '| file | licence | why |\n|---|---|---|\n| a.jpg | CC0 | x |\n\n- notes\n| b.jpg | CC0 | after the list |\n'
    head, rows = gates.table(cr, ['file', 'licence'])
    assert [gates.col(r, 'file') for r in rows] == ['a.jpg']
    assert gates.rows_outside_table(cr, head, ['b.jpg']) == ['line 6: b.jpg']


# ------------------------------------------------------------------ bookend, still, moving depth (bugs 3, 18)

def test_bookend_slide_may_return_to_the_opening_photo(build, tmp_path):
    import visual_audit
    p = photo(tmp_path / 'open.png', (800, 450))
    others = [photo(tmp_path / f'o{i}.png', (800, 450), (40 * i, 90, 30)) for i in range(1, 4)]

    def sl(img, scene, **k):
        return {'scene': scene, **k, 'shapes': [{'type': 'image', 'name': 'ph', 'path': str(img), 'x': 0, 'y': 0, 'w': 13.333, 'h': 7.5},
                                               {'type': 'text', 'name': 't', 'text': scene, 'x': 1, 'y': 6, 'w': 4, 'h': 0.6}]}
    spec = {'slides': [sl(p, 'S1'), sl(others[0], 'S2'), sl(others[1], 'S3'), sl(others[2], 'S4'), sl(p, 'S5', bookend=True)]}
    out, roots, _ = build(spec)
    assert roots[-1].find(f'{{{P_NS}}}cSld').get('name') == 'S5 [bookend]'
    slides = visual_audit.load_pptx_slides(out)
    assert slides[-1]['bookend'] and slides[-1]['marker'] == 'S5'
    visual_audit._apply_subject(slides)
    a = visual_audit.Audit()
    visual_audit._reuse_and_runs(slides, a)
    assert any('declared bookend' in i for i in a.infos)


def _sld(*parts, name=''):
    xml = (f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}"><p:cSld name="{name}"><p:spTree>'
           '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>' + ''.join(parts) + '</p:spTree></p:cSld>'
           '{timing}</p:sld>')
    return xml


def _xf(x, y, w, h):
    return f'<a:xfrm><a:off x="{int(x * EMU_W)}" y="{int(y * EMU_H)}"/><a:ext cx="{int(w * EMU_W)}" cy="{int(h * EMU_H)}"/></a:xfrm>'


def _shape(sid, x, y, w, h, fill='', text=''):
    body = f'<p:txBody><a:bodyPr/><a:p><a:r><a:rPr sz="1800"/><a:t>{text}</a:t></a:r></a:p></p:txBody>' if text else ''
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="s{sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{_xf(x, y, w, h)}{fill}</p:spPr>{body}</p:sp>')


def _pic(sid, x, y, w, h, extra=''):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="p{sid}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="rId2">{extra}</a:blip></p:blipFill><p:spPr>{_xf(x, y, w, h)}</p:spPr></p:pic>')


def _path_timing(spid, loop=False):
    rep = ' repeatCount="indefinite"' if loop else ''
    return (f'<p:timing><p:tnLst><p:par><p:cTn id="1"><p:childTnLst><p:par><p:cTn id="2" presetClass="path" presetID="0"{rep}>'
            f'<p:childTnLst><p:animMotion path="M 0 0 L 0.1 0"><p:cBhvr><p:cTn id="3"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            '</p:cBhvr></p:animMotion></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')


def test_moving_depth_needs_a_picture_plate_and_a_real_moving_layer():
    import variety_audit
    solid = '<a:solidFill><a:srgbClr val="202020"/></a:solidFill>'
    flat = _sld(_shape(2, 0, 0, 1, 0.7, solid), _shape(3, 0.5, 0.5, 0.01, 0.01, solid), _shape(4, 0.1, 0.8, 0.5, 0.1, text='Tiêu đề'))
    root = etree.fromstring(flat.replace('{timing}', _path_timing(3)).encode())
    assert variety_audit.moving_depth(root, variety_audit.effect_techniques(root))[0] is False   # flat rect + a drifting dot
    real = _sld(_pic(2, 0, 0, 1, 1), _shape(3, 0.3, 0.3, 0.2, 0.2, solid), _shape(4, 0.1, 0.8, 0.5, 0.1, text='Tiêu đề'))
    root = etree.fromstring(real.replace('{timing}', _path_timing(3)).encode())
    assert variety_audit.moving_depth(root, variety_audit.effect_techniques(root))[0] is True


def test_still_pages_are_excluded_from_the_depth_share():
    import variety_audit
    pages = []
    for i in range(10):
        x = _sld(_shape(2, 0.1, 0.1, 0.5, 0.2, text=f'Trang {i}'), name=f'S{i} [still]' if i < 2 else f'S{i}')
        pages.append((f'pos {i + 1}', etree.fromstring(x.replace('{timing}', '').encode())))
    errors, warns, info = variety_audit.audit(pages, lambda r: ('fade',))
    assert any('(2 still)' in i for i in info)
    assert any('on 0/8 slides' in w and '2 still page(s) excluded' in w for w in warns)


# ------------------------------------------------------------------ styles (bugs 14, 16)

def test_inline_style_extends_a_pack_and_style_overrides_may_define_one(build):
    spec = {'style': 'mine', 'styles': {'mine': {'extends': 'paper-editorial', 'palette': {'accent': '#123456'}}},
            'slides': [{'shapes': [{'type': 'rect', 'name': 'r', 'x': 1, 'y': 1, 'w': 2, 'h': 1, 'fill': 'accent'}]},
                       {'style': 'zine', 'shapes': [{'type': 'rect', 'name': 'r', 'x': 1, 'y': 1, 'w': 2, 'h': 1, 'fill': 'accent'}]}],
            'style_overrides': {'zine': {'extends': 'neo-brutal', 'palette': {'accent': '#ABCDEF'}}}}
    out, roots, _ = build(spec)
    fills = [named(r, 'r').find('.//{%s}srgbClr' % A_NS).get('val') for r in roots]
    assert fills == ['123456', 'ABCDEF']


def test_every_pack_leaves_room_on_the_ten_size_scale():
    import build_deck
    for p in sorted((SKILL / 'assets' / 'styles').glob('*.json')):
        t = build_deck.merge(build_deck.DEFAULT_TYPE, json.loads(p.read_text())['type'])
        sizes = {v['size'] for v in t.values() if v.get('size')}
        assert len(sizes) <= 8, (p.name, sorted(sizes))


def test_heritage_collage_pack_is_complete():
    d = json.loads((SKILL / 'assets' / 'styles' / 'heritage-collage.json').read_text())
    assert {'script', 'callout'} <= set(d['type']) and d['fonts']['script']
    assert d['type']['display']['caps'] and not d['type']['body'].get('caps')
    assert d['grounds']['main']['kind'] == 'paper' and d['grounds']['main']['stains'] > 0
    assert d['grounds']['terracotta']['kind'] == 'gradient'


# ------------------------------------------------------------------ components (weakness 20)

def collage(build, shapes):
    return build({'style': 'heritage-collage', 'slides': [{'shapes': shapes}]})


def test_callout_dot_sits_on_the_part_and_the_leader_ends_on_the_chip(build):
    out, roots, log = collage(build, [{'type': 'callout', 'name': 'c', 'at': [3.0, 3.0], 'x': 6.0, 'y': 1.5, 'label': 'Mũi tàu',
                                       'desc': 'nắp che cổng ghép'}])
    r = roots[0]
    for part in ('c.dot', 'c.ring', 'c.lead', 'c.labk', 'c.lab', 'c.desc'):
        assert named(r, part) is not None, part
    off = named(r, 'c.dot').find('.//{%s}off' % A_NS)
    ext = named(r, 'c.dot').find('.//{%s}ext' % A_NS)
    cx = (int(off.get('x')) + int(ext.get('cx')) / 2) / 914400
    assert abs(cx - 3.0) < 0.02
    chip = named(r, 'c.labk').find('.//{%s}off' % A_NS)
    lead = named(r, 'c.lead')
    lo, le = lead.find('.//{%s}off' % A_NS), lead.find('.//{%s}ext' % A_NS)
    assert abs((int(lo.get('x')) + int(le.get('cx'))) - int(chip.get('x'))) < 914400 * 0.02


def test_swatch_samples_distinct_colours_and_prints_codes(build, tmp_path):
    from PIL import Image
    im = Image.new('RGB', (300, 100), (200, 40, 30))
    im.paste((30, 60, 160), (100, 0, 200, 100))
    im.paste((240, 220, 180), (200, 0, 300, 100))
    p = tmp_path / 'tri.png'
    im.save(p)
    import build_deck
    cols = build_deck.sample_palette(p, 3)
    assert len(cols) == 3 and len(set(cols)) == 3
    out, roots, _ = collage(build, [{'type': 'swatch', 'name': 'sw', 'image': str(p), 'n': 3, 'x': 1, 'y': 1, 'w': 4.5, 'h': 0.8}])
    texts = [''.join(t.text or '' for t in named(roots[0], f'sw.h{i}').iter('{%s}t' % A_NS)) for i in range(3)]
    assert all(t.startswith('#') for t in texts)


def test_swatch_from_a_cutout_ignores_the_transparent_page(tmp_path):
    from PIL import Image
    import build_deck
    im = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    im.paste((10, 200, 30, 255), (40, 40, 60, 60))
    p = tmp_path / 'cut.png'
    im.save(p)
    assert build_deck.sample_palette(p, 2)[0] == '#0AC81E'


def test_photogrid_packs_spans_and_puts_labels_on_chips(build, tmp_path):
    imgs = [str(photo(tmp_path / f'g{i}.png')) for i in range(5)]
    out, roots, _ = collage(build, [{'type': 'photogrid', 'name': 'g', 'x': 1, 'y': 1, 'w': 8, 'h': 4.5, 'cols': 3,
                                     'images': [{'path': imgs[0], 'span': [2, 2], 'label': 'Lớn'}] + imgs[1:]}])
    r = roots[0]
    big = named(r, 'g.p0').find('.//{%s}ext' % A_NS)
    small = named(r, 'g.p1').find('.//{%s}ext' % A_NS)
    assert int(big.get('cx')) > 1.9 * int(small.get('cx'))
    assert named(r, 'g.t0k') is not None and named(r, 'g.f4') is not None
    import legibility_audit
    assert legibility_audit.scrim_missing(r) == []


def test_nodemap_draws_links_nodes_and_chip_labels(build):
    out, roots, _ = collage(build, [{'type': 'nodemap', 'name': 'm', 'x': 1, 'y': 1, 'w': 8, 'h': 5,
                                     'nodes': [{'id': 'a', 'x': 0.1, 'y': 0.2, 'label': 'Hội quán A'}, {'id': 'b', 'x': 0.8, 'y': 0.7, 'label': 'B', 'desc': 'mô tả'}],
                                     'links': [['a', 'b']]}])
    r = roots[0]
    assert named(r, 'm.e0') is not None and named(r, 'm.n1') is not None and named(r, 'm.t0k') is not None and named(r, 'm.d1') is not None


def test_script_role_rotates_and_may_cross_the_title_without_a_warning(build):
    out, roots, log = collage(build, [{'type': 'text', 'name': 'title', 'role': 'display', 'text': 'Kiến trúc', 'x': 1, 'y': 1, 'w': 9, 'h': 2},
                                      {'type': 'text', 'name': 'script', 'role': 'script', 'text': 'nghệ thuật trang trí', 'x': 2, 'y': 2.2, 'w': 6, 'h': 1}])
    assert 'overlap' not in log
    xfrm = named(roots[0], 'script').find('.//{%s}xfrm' % A_NS)
    assert xfrm.get('rot') == str(-4 * 60000) or int(xfrm.get('rot')) == 21360000


def test_paper_stains_and_gradient_grounds():
    import make_assets
    import numpy as np
    a = np.asarray(make_assets.ground('paper', base='#ECDFC1', tone='#D9C08C', stains=0.8, size=(320, 180), seed=2), np.float32)
    b = np.asarray(make_assets.ground('paper', base='#ECDFC1', tone='#D9C08C', stains=0.0, size=(320, 180), seed=2), np.float32)
    assert a.std() > b.std()
    g = np.asarray(make_assets.ground('gradient', base='#5E2210', tone='#D98A3D', angle=0, size=(320, 180)), np.float32)
    assert g[:, -10:].mean() > g[:, :10].mean() + 40


# ------------------------------------------------------------------ legibility audit

def test_caps_body_paragraph_is_flagged_but_a_caps_headline_is_not():
    import legibility_audit
    long = 'HỘI QUÁN ÔN LĂNG LÀ MỘT TRONG NHỮNG HỘI QUÁN CỔ NHẤT CỦA NGƯỜI HOA Ở CHỢ LỚN VÀ VẪN CÒN GIỮ NGUYÊN'
    body = (f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="body"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{_xf(0.1, 0.5, 0.5, 0.3)}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:p><a:r><a:rPr sz="1400"/><a:t>{long}</a:t></a:r></a:p></p:txBody></p:sp>')
    head = (f'<p:sp><p:nvSpPr><p:cNvPr id="3" name="head"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{_xf(0.1, 0.1, 0.8, 0.2)}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:p><a:r><a:rPr sz="6000" cap="all"/><a:t>{long.lower()}</a:t></a:r></a:p></p:txBody></p:sp>')
    root = etree.fromstring(_sld(body, head).replace('{timing}', '').encode())
    hits = legibility_audit.caps_body(root)
    assert [h[0] for h in hits] == ['body']


def test_text_on_a_photo_needs_a_band_a_gradient_or_a_toned_picture():
    import legibility_audit
    txt = _shape(5, 0.1, 0.7, 0.5, 0.1, text='Chữ trên ảnh')
    bare = etree.fromstring(_sld(_pic(2, 0, 0, 1, 1), txt).replace('{timing}', '').encode())
    assert legibility_audit.scrim_missing(bare) == ['s5']
    band = _shape(3, 0.05, 0.65, 0.6, 0.2, '<a:solidFill><a:srgbClr val="000000"><a:alpha val="70000"/></a:srgbClr></a:solidFill>')
    assert legibility_audit.scrim_missing(etree.fromstring(_sld(_pic(2, 0, 0, 1, 1), band, txt).replace('{timing}', '').encode())) == []
    grad = _shape(3, 0, 0.5, 1, 0.5, '<a:gradFill><a:gsLst><a:gs pos="0"><a:srgbClr val="000000"/></a:gs></a:gsLst></a:gradFill>')
    assert legibility_audit.scrim_missing(etree.fromstring(_sld(_pic(2, 0, 0, 1, 1), grad, txt).replace('{timing}', '').encode())) == []
    toned = _pic(2, 0, 0, 1, 1, '<a:lum bright="-30000"/>')
    assert legibility_audit.scrim_missing(etree.fromstring(_sld(toned, txt).replace('{timing}', '').encode())) == []
    faint = _shape(3, 0.05, 0.65, 0.6, 0.2, '<a:solidFill><a:srgbClr val="000000"><a:alpha val="15000"/></a:srgbClr></a:solidFill>')
    assert legibility_audit.scrim_missing(etree.fromstring(_sld(_pic(2, 0, 0, 1, 1), faint, txt).replace('{timing}', '').encode())) == ['s5']
    assert legibility_audit.scrim_missing(bare, cutout=lambda rid: True) == []     # a transparent cut-out is page, not photo


def test_check_deck_reports_caps_body_as_an_error(build):
    import check_deck
    out, _, _ = build({'slides': [{'shapes': [{'type': 'text', 'name': 'b', 'caps': True, 'size': 14, 'x': 1, 'y': 1, 'w': 8, 'h': 2,
                                               'text': 'đây là một đoạn văn dài viết hoa toàn bộ mà lẽ ra phải viết thường cho dễ đọc hơn nhiều'}]}]})
    code, txt = call(check_deck.main, [str(out), '--variety', 'off'])
    assert 'caps body' in txt and code != 0


# ------------------------------------------------------------------ small fixes (bugs 4-7, 11-13, 17)

def test_poly_open_and_closed_spellings():
    import build_deck
    assert build_deck.poly_closed({}) is True
    assert build_deck.poly_closed({'open': True}) is False
    assert build_deck.poly_closed({'closed': False}) is False


def test_motion_list_needs_no_folder():
    r = subprocess.run([sys.executable, str(SCRIPTS / 'motion.py'), '--list'], capture_output=True, text=True)
    assert r.returncode == 0 and 'transitions:' in r.stdout


def test_max_seconds_fits_every_slide_by_shrinking_holds_first():
    import preview_motion
    holds, trans = [6000] * 10, [0] + [800] * 9
    fitted, tk = preview_motion.fit_budget(holds, trans, 40000)
    assert tk == 1.0 and abs(sum(fitted) + sum(trans) - 40000) < 50 and min(fitted) >= preview_motion.MIN_HOLD_MS
    fitted, tk = preview_motion.fit_budget(holds, trans, 12000)
    assert all(f == preview_motion.MIN_HOLD_MS for f in fitted) and tk < 1
    assert preview_motion.fit_budget(holds, trans, 0) == (holds, 1.0)


def test_cutout_and_contact_sheet_respect_exif_rotation(tmp_path):
    from PIL import Image
    import contact_sheet
    import cutout
    im = Image.new('RGB', (300, 100), (250, 250, 250))
    im.paste((200, 20, 20), (0, 0, 60, 100))
    ex = Image.Exif()
    ex[0x0112] = 6
    p = tmp_path / 'rot.jpg'
    im.save(p, exif=ex)
    assert cutout.open_upright(p).size == (100, 300)
    out = tmp_path / 'sheet.jpg'
    contact_sheet.sheet([p], out, 1, 300, 'none', {})
    import numpy as np
    arr = np.asarray(Image.open(out).convert('L')) > 200          # the white part of the photo
    cols, rows = arr.any(axis=0).sum(), arr.any(axis=1).sum()
    assert rows > 1.5 * cols, (rows, cols)                       # an upright portrait tile, not the raw landscape


def test_cutout_keeps_dark_parts_of_the_object(tmp_path):
    from PIL import Image, ImageDraw
    import cutout
    im = Image.new('RGB', (400, 300), (0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((180, 80, 320, 220), fill=(235, 235, 235))
    d.rectangle((40, 110, 185, 190), fill=(14, 18, 34))          # a dark solar panel, nearly the colour of space
    for x in range(40, 185, 12):
        d.line([(x, 110), (x, 190)], fill=(70, 80, 110), width=2)
    src, dst = tmp_path / 'sat.png', tmp_path / 'cut.png'
    im.save(src)
    cutout.main([str(src), str(dst), '--pad', '0'])
    al = Image.open(dst).getchannel('A')
    bx = Image.open(dst).size
    assert al.getpixel((bx[0] // 5, bx[1] // 2)) > 200            # the panel survives
    assert al.getpixel((2, 2)) == 0


def test_defringe_removes_the_dark_ring_of_a_white_object(tmp_path):
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    import cutout
    im = Image.new('RGB', (200, 200), (0, 0, 0))
    ImageDraw.Draw(im).ellipse((40, 40, 160, 160), fill=(240, 240, 240))
    im = im.filter(ImageFilter.GaussianBlur(2))
    src, a, b = tmp_path / 'w.png', tmp_path / 'a.png', tmp_path / 'b.png'
    im.save(src)
    cutout.main([str(src), str(a), '--defringe', '0', '--pad', '0'])
    cutout.main([str(src), str(b), '--pad', '0'])

    def ring_dark(p):
        arr = np.asarray(Image.open(p).convert('RGBA'), np.float32)
        on = arr[..., 3] > 128
        lum = arr[..., :3].mean(axis=2)
        return (on & (lum < 120)).sum()
    assert ring_dark(b) < ring_dark(a) * 0.5


def test_compare_default_reference_follows_the_deck_kind(tmp_path):
    import studio
    import gates
    work = tmp_path / 'w'
    call(gates.main, ['init', str(work), '--kind', 'product'])
    refs, label = studio.reference_sheets(work, None, tmp_path)
    assert refs[0].name == 'styles-gallery.jpg' and 'product' in label
    folder = tmp_path / 'refs'
    folder.mkdir()
    for i in range(3):
        photo(folder / f'r{i}.jpg')
    refs, label = studio.reference_sheets(work, str(folder), tmp_path)
    assert refs[0].exists() and '3 images' in label
    (work / 'brief.md').write_text((work / 'brief.md').read_text().replace('deliverable_kind: product', 'deliverable_kind: heritage'))
    refs, label = studio.reference_sheets(work, None, tmp_path)
    assert all('catru' in r.name for r in refs)


def test_film_module_reports_figure_errors_not_setup(tmp_path):
    src = (SCRIPTS / 'anatomy' / 'film.mjs').read_text()
    assert 'FIGURE ERROR' in src and 'anchorsAt' in src and '[object Object]' in src
    r = subprocess.run(['node', '--check', str(SCRIPTS / 'anatomy' / 'film.mjs')], capture_output=True, text=True) \
        if subprocess.run(['which', 'node'], capture_output=True).returncode == 0 else None
    if r is not None:
        assert r.returncode == 0, r.stderr
