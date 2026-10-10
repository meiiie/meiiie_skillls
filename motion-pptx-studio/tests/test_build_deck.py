import json
import zipfile

import pytest

from conftest import NS, box, named, names, text

A = '{%s}' % NS['a']
P = '{%s}' % NS['p']


def test_v3_spec_still_builds(build, png):
    spec = {
        'palette': {'bg': '#0E0A07', 'ink': '#F1E4C8', 'gold': '#C79A3B'},
        'fonts': {'display': 'DejaVu Serif', 'body': 'DejaVu Sans'},
        'slides': [
            {'id': 's1', 'bg': 'bg', 'notes': 'Lời', 'shapes': [
                {'type': 'line', 'name': '!!str2', 'x1': 6.67, 'y1': 0.6, 'x2': 6.67, 'y2': 6.9, 'color': 'gold', 'width': 1.25},
                {'type': 'text', 'name': '@fade1-anchor', 'text': 'Nghe.', 'x': 7.1, 'y': 5.9, 'w': 5.4, 'h': 0.6,
                 'font': 'body', 'size': 20, 'color': 'ink'}]},
            {'id': 's2', 'from': 'prev', 'set': {'!!str2': {'x1': 6.2, 'x2': 6.2}}, 'drop': ['@fade1-anchor'],
             'add': [{'type': 'image', 'name': '!!photo', 'path': str(png), 'x': 8.4, 'y': 2.2, 'w': 4.2, 'h': 3.1}]},
        ]}
    out, sl, _ = build(spec)
    assert len(sl) == 2
    assert named(sl[0], '!!str2') is not None
    assert named(sl[1], '!!photo') is not None
    assert named(sl[1], '@fade1-anchor') is None


def test_style_pack_roles_and_palette(build):
    spec = {'style': 'noir-product', 'slides': [
        {'shapes': [{'type': 'text', 'name': '!!t', 'role': 'title', 'text': 'Xin chào', 'x': 1, 'y': 1, 'w': 8, 'h': 1.2}]}]}
    out, sl, _ = build(spec)
    t = named(sl[0], '!!t')
    rpr = t.find('.//' + A + 'rPr')
    from build_deck import load_style
    st = load_style('noir-product')
    role = st['type']['title']
    assert int(rpr.get('sz')) == int(role['size'] * 100)
    latin = rpr.find(A + 'latin').get('typeface')
    assert latin == st['fonts'][role['font']]


def test_explicit_keys_override_role(build):
    spec = {'style': 'noir-product', 'slides': [
        {'shapes': [{'type': 'text', 'name': '!!t', 'role': 'title', 'size': 30, 'text': 'A', 'x': 1, 'y': 1, 'w': 4, 'h': 1}]}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!t').find('.//' + A + 'rPr').get('sz') == '3000'


def test_chrome_on_every_slide_with_page_numbers(build):
    spec = {'palette': {'bg': '#101010', 'ink': '#FFFFFF'},
            'chrome': {'over': [
                {'type': 'rect', 'name': '!!frame', 'x': 0.3, 'y': 0.3, 'w': 12.73, 'h': 6.9, 'line_color': 'ink', 'line_width': 0.75},
                {'type': 'text', 'name': '!!pageno', 'text': '{n}', 'x': 12.1, 'y': 6.8, 'w': 0.6, 'h': 0.3, 'size': 10, 'color': 'ink'}]},
            'slides': [{'shapes': []}, {'shapes': []}, {'chrome': False, 'shapes': []}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!frame') is not None and text(named(sl[0], '!!pageno')) == '01'
    assert text(named(sl[1], '!!pageno')) == '02'
    assert named(sl[2], '!!frame') is None
    # chrome "over" sits on top of slide shapes
    assert names(sl[0])[-1] == '!!pageno'


def test_chrome_subset_and_override(build):
    spec = {'palette': {'ink': '#FFFFFF'},
            'chrome': {'over': [
                {'type': 'rect', 'name': '!!frame', 'x': 0.3, 'y': 0.3, 'w': 12.73, 'h': 6.9, 'line_color': 'ink'},
                {'type': 'text', 'name': '!!pageno', 'text': '{n}/{total}', 'x': 12, 'y': 6.8, 'w': 1, 'h': 0.3, 'size': 10}]},
            'slides': [{'chrome': ['!!pageno'], 'shapes': []},
                       {'chrome_set': {'!!frame': {'x': 1.0}}, 'shapes': []}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!frame') is None
    assert text(named(sl[0], '!!pageno')) == '01/02'
    assert box(named(sl[1], '!!frame'))[0] == pytest.approx(1.0, abs=0.01)


def test_grid_columns(build):
    spec = {'grid': {'cols': 12, 'left': 1.0, 'right': 1.0, 'gutter': 0.25},
            'slides': [{'shapes': [{'type': 'rect', 'name': '!!r', 'col': [1, 6], 'y': 1, 'h': 1, 'fill': '#FF0000'},
                                   {'type': 'rect', 'name': '!!s', 'col': [7, 6], 'y': 1, 'h': 1, 'fill': '#FF0000'}]}]}
    _, sl, _ = build(spec)
    colw = (13.333 - 2 - 11 * 0.25) / 12
    x, y, w, h = box(named(sl[0], '!!r'))
    assert x == pytest.approx(1.0, abs=0.01)
    assert w == pytest.approx(6 * colw + 5 * 0.25, abs=0.01)
    x2 = box(named(sl[0], '!!s'))[0]
    assert x2 == pytest.approx(1.0 + 6 * (colw + 0.25), abs=0.01)


def test_image_background(build, png):
    spec = {'grounds': {'main': str(png)}, 'slides': [{'bg': 'main', 'shapes': []}, {'bg': '#112233', 'shapes': []}]}
    out, sl, _ = build(spec)
    bg = sl[0].find('.//' + P + 'bg')
    assert bg is not None and bg.find('.//' + A + 'blip') is not None
    bg2 = sl[1].find('.//' + P + 'bg')
    assert bg2.find('.//' + A + 'srgbClr').get('val') == '112233'


def test_deck_default_bg_applies(build):
    spec = {'bg': '#0A0B0C', 'slides': [{'shapes': []}]}
    _, sl, _ = build(spec)
    assert sl[0].find('.//' + P + 'bg').find('.//' + A + 'srgbClr').get('val') == '0A0B0C'


def test_shadow_on_rect_and_image(build, png):
    spec = {'slides': [{'shapes': [
        {'type': 'rect', 'name': '!!card', 'x': 1, 'y': 1, 'w': 3, 'h': 2, 'fill': '#FFFFFF',
         'shadow': {'blur': 18, 'dist': 6, 'dir': 90, 'color': '#000000', 'alpha': 0.35}},
        {'type': 'image', 'name': '!!pic', 'path': str(png), 'x': 5, 'y': 1, 'w': 4, 'h': 2, 'shadow': True}]}]}
    _, sl, _ = build(spec)
    sh = named(sl[0], '!!card').find('.//' + A + 'outerShdw')
    assert sh is not None and sh.get('blurRad') == str(18 * 12700) and sh.get('dir') == str(90 * 60000)
    assert sh.find(A + 'srgbClr/' + A + 'alpha').get('val') == '35000'
    assert named(sl[0], '!!pic').find('.//' + A + 'outerShdw') is not None


def test_image_effects(build, png):
    spec = {'slides': [{'shapes': [
        {'type': 'image', 'name': '!!a', 'path': str(png), 'x': 1, 'y': 1, 'w': 4, 'h': 2, 'grayscale': True,
         'radius': 0.08, 'line_color': '#D9B26A', 'line_width': 1.5},
        {'type': 'image', 'name': '!!b', 'path': str(png), 'x': 6, 'y': 1, 'w': 4, 'h': 2, 'duotone': ['#140B08', '#EBCB86'],
         'brightness': -0.2, 'contrast': 0.1}]}]}
    _, sl, _ = build(spec)
    a = named(sl[0], '!!a')
    assert a.find('.//' + A + 'grayscl') is not None
    assert a.find('.//' + A + 'prstGeom').get('prst') == 'roundRect'
    assert a.find('.//' + A + 'ln') is not None
    b = named(sl[0], '!!b')
    duo = b.find('.//' + A + 'duotone')
    assert [c.get('val') for c in duo] == ['140B08', 'EBCB86']
    lum = b.find('.//' + A + 'lum')
    assert lum.get('bright') == '-20000' and lum.get('contrast') == '10000'


def test_group_shape(build):
    spec = {'slides': [{'shapes': [{'type': 'group', 'name': '!!card1', 'shapes': [
        {'type': 'rect', 'name': 'card1 bg', 'x': 1, 'y': 1, 'w': 3, 'h': 4, 'fill': '#222222'},
        {'type': 'text', 'name': 'card1 title', 'text': 'Một', 'x': 1.2, 'y': 1.2, 'w': 2.6, 'h': 0.6, 'size': 20}]}]}]}
    _, sl, _ = build(spec)
    g = named(sl[0], '!!card1')
    assert g.tag == P + 'grpSp'
    assert box(g) == pytest.approx((1, 1, 3, 4), abs=0.01)
    assert named(g, 'card1 title') is not None


def test_hidden_shape_is_skipped_and_can_return(build):
    spec = {'slides': [
        {'shapes': [{'type': 'rect', 'name': '!!r', 'x': 1, 'y': 1, 'w': 1, 'h': 1, 'fill': '#FFFFFF', 'hidden': True}]},
        {'from': 'prev', 'set': {'!!r': {'hidden': False}}}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!r') is None and named(sl[1], '!!r') is not None


def test_heading_component_expands_and_stacks(build):
    spec = {'style': 'paper-editorial', 'slides': [{'shapes': [
        {'type': 'heading', 'name': '!!h', 'x': 1.2, 'y': 1.0, 'w': 7,
         'kicker': 'CHƯƠNG 1', 'title': 'Ngược dòng thời gian', 'sub': 'Tìm hiểu nguồn gốc', 'body': 'Một đoạn mô tả ngắn.'}]}]}
    _, sl, out = build(spec)
    k, t, s, b = (named(sl[0], '!!h.' + p) for p in ('kick', 'title', 'sub', 'body'))
    assert all(e is not None for e in (k, t, s, b))
    ys = [box(e)[1] for e in (k, t, s, b)]
    assert ys == sorted(ys) and len(set(ys)) == 4
    assert text(t) == 'Ngược dòng thời gian'


def test_component_keyframe_set(build):
    spec = {'style': 'paper-editorial', 'slides': [
        {'shapes': [{'type': 'heading', 'name': '!!h', 'x': 1, 'y': 1, 'w': 7, 'title': 'Một'}]},
        {'from': 'prev', 'set': {'!!h': {'title': 'Hai', 'x': 6}}}]}
    _, sl, _ = build(spec)
    assert text(named(sl[1], '!!h.title')) == 'Hai'
    assert box(named(sl[1], '!!h.title'))[0] > box(named(sl[0], '!!h.title'))[0]


def test_card_states(build):
    spec = {'style': 'noir-product', 'slides': [{'shapes': [
        {'type': 'card', 'name': '!!c1', 'x': 1, 'y': 2, 'w': 3.2, 'h': 4, 'title': 'Nhanh', 'kicker': 'TỐC ĐỘ', 'desc': 'Mô tả', 'state': 'lit'},
        {'type': 'card', 'name': '!!c2', 'x': 5, 'y': 2, 'w': 3.2, 'h': 4, 'title': 'Gọn', 'state': 'dim'}]}]}
    _, sl, _ = build(spec)
    c1, c2 = named(sl[0], '!!c1'), named(sl[0], '!!c2')
    assert c1.tag == P + 'grpSp' and c2.tag == P + 'grpSp'
    assert 'Nhanh' in text(c1) and 'TỐC ĐỘ'.upper() in text(c1).upper()
    # a dim card is visibly quieter than a lit one: its title colour is mixed toward the card
    # surface as a SOLID colour (LibreOffice misplaces Vietnamese marks on transparent text)
    lit = named(c1, '!!c1 title').find('.//' + A + 'srgbClr').get('val')
    dim = named(c2, '!!c2 title').find('.//' + A + 'srgbClr').get('val')
    assert lit != dim and named(c2, '!!c2 title').find('.//' + A + 'alpha') is None
    lum = lambda h: sum(int(h[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
    assert lum(dim) < lum(lit)  # on a dark style the quiet title is darker


def test_stat_component(build):
    spec = {'style': 'boardroom-data', 'slides': [{'shapes': [
        {'type': 'stat', 'name': '!!k', 'x': 1, 'y': 2, 'w': 4, 'value': '48', 'unit': '%', 'label': 'khách hàng quay lại'}]}]}
    _, sl, _ = build(spec)
    v = named(sl[0], '!!k.value')
    assert text(v) == '48' and named(sl[0], '!!k.unit') is not None and named(sl[0], '!!k.label') is not None


def test_screen_component(build, png):
    spec = {'style': 'noir-product', 'slides': [{'shapes': [
        {'type': 'screen', 'name': '!!scr', 'device': 'browser', 'image': str(png), 'x': 6, 'y': 1.5, 'w': 6, 'h': 4, 'url': 'app.example'}]}]}
    _, sl, _ = build(spec)
    g = named(sl[0], '!!scr')
    assert g.tag == P + 'grpSp'
    assert g.find('.//' + P + 'pic') is not None
    assert g.find('.//' + A + 'outerShdw') is not None


def test_timeline_active_node_is_larger(build):
    nodes = [{'t': '0:00', 'label': 'Mở đầu'}, {'t': '0:30', 'label': 'Giữa'}, {'t': '1:29', 'label': 'Kết'}]
    spec = {'style': 'lacquer-heritage', 'slides': [
        {'shapes': [{'type': 'timeline', 'name': '!!tl', 'x': 1, 'y': 4.3, 'w': 11, 'nodes': nodes, 'active': 0}]},
        {'from': 'prev', 'set': {'!!tl': {'active': 2}}}]}
    _, sl, _ = build(spec)
    d0a, d2a = box(named(sl[0], '!!tl.dot0')), box(named(sl[0], '!!tl.dot2'))
    d0b, d2b = box(named(sl[1], '!!tl.dot0')), box(named(sl[1], '!!tl.dot2'))
    assert d0a[2] > d2a[2] and d2b[2] > d0b[2]
    assert named(sl[1], '!!tl.prog') is not None
    assert box(named(sl[1], '!!tl.prog'))[2] > box(named(sl[0], '!!tl.prog'))[2]


def test_bars_grow_and_highlight(build):
    data = [{'label': '2023', 'value': 40}, {'label': '2024', 'value': 80}]
    spec = {'style': 'boardroom-data', 'slides': [
        {'shapes': [{'type': 'bars', 'name': '!!b', 'x': 1, 'y': 2, 'w': 6, 'h': 4, 'data': data, 'grow': 0.0}]},
        {'from': 'prev', 'set': {'!!b': {'grow': 1.0, 'highlight': 1}}}]}
    _, sl, _ = build(spec)
    h0 = box(named(sl[0], '!!b.bar1'))[3]
    h1 = box(named(sl[1], '!!b.bar1'))[3]
    assert h0 < 0.05 and h1 > 2.5
    # bars grow upward: the bottom edge stays on the baseline
    y0, hh0 = box(named(sl[0], '!!b.bar1'))[1], h0
    y1, hh1 = box(named(sl[1], '!!b.bar1'))[1], h1
    assert y0 + hh0 == pytest.approx(y1 + hh1, abs=0.02)
    # bar 0 is half of bar 1 when fully grown
    assert box(named(sl[1], '!!b.bar0'))[3] == pytest.approx(h1 / 2, abs=0.05)


def test_list_reveal(build):
    items = ['Một', 'Hai', 'Ba']
    spec = {'style': 'paper-editorial', 'slides': [
        {'shapes': [{'type': 'list', 'name': '!!l', 'x': 1, 'y': 2, 'w': 6, 'items': items, 'reveal': 1}]},
        {'from': 'prev', 'set': {'!!l': {'reveal': 3, 'focus': 2}}}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!l.i0') is not None and named(sl[0], '!!l.i1') is None
    assert named(sl[1], '!!l.i2') is not None


def test_quote_component(build):
    spec = {'style': 'paper-editorial', 'slides': [{'shapes': [
        {'type': 'quote', 'name': '!!q', 'x': 1.5, 'y': 1.5, 'w': 9, 'text': 'Nghe thì lạ, hiểu rồi thương.', 'by': 'Đáy'}]}]}
    _, sl, _ = build(spec)
    assert 'Nghe thì lạ' in text(named(sl[0], '!!q.text')) and named(sl[0], '!!q.by') is not None


def test_motion_json_written_from_deck(build, tmp_path):
    spec = {'motion': {'default_ms': 1200, 'stagger_ms': 200},
            'slides': [{'shapes': []}, {'ms': 2000, 'morph': 'byChar', 'shapes': []}, {'keep_timing': True, 'shapes': []}]}
    out, _, _ = build(spec)
    mj = json.loads((out.parent / 'motion.json').read_text())
    assert mj['default_ms'] == 1200 and mj['dur'] == {'2': 2000}
    assert mj['option'] == {'2': 'byChar'} and mj['keep_timing'] == [3]


def test_scene_id_written_to_slide_name(build):
    spec = {'slides': [{'scene': 'S3', 'shapes': []}]}
    _, sl, _ = build(spec)
    assert sl[0].find(P + 'cSld').get('name') == 'S3'


def test_overflow_warning(build):
    spec = {'slides': [{'shapes': [
        {'type': 'text', 'name': '!!t', 'text': 'Một tiêu đề rất dài sẽ không vừa trong hộp nhỏ này đâu nhé bạn',
         'font': 'DejaVu Sans', 'size': 40, 'x': 1, 'y': 1, 'w': 3, 'h': 0.8}]}]}
    _, _, out = build(spec)
    assert 'WARN' in out and '!!t' in out and 'lines need' in out


def test_safe_area_warning(build):
    spec = {'slides': [{'shapes': [
        {'type': 'text', 'name': '!!t', 'text': 'Sát mép', 'font': 'DejaVu Sans', 'size': 20, 'x': 0.05, 'y': 1, 'w': 3, 'h': 0.6}]}]}
    _, _, out = build(spec)
    assert 'safe area' in out


def test_unknown_style_errors(build):
    with pytest.raises(SystemExit):
        build({'style': 'nope-not-a-style', 'slides': [{'shapes': []}]})


def test_preset_geometry(build):
    spec = {'slides': [{'shapes': [{'type': 'rect', 'geom': 'CHEVRON', 'name': '!!c', 'x': 1, 'y': 1, 'w': 1, 'h': 1, 'fill': '#FF0000'}]}]}
    _, sl, _ = build(spec)
    assert named(sl[0], '!!c').find('.//' + A + 'prstGeom').get('prst') == 'chevron'


def test_text_running_over_a_card_is_flagged(build):
    spec = {'style': 'noir-product', 'slides': [{'shapes': [
        {'type': 'heading', 'name': '!!h', 'x': 1, 'y': 1.2, 'w': 7.5, 'title': 'Một tiêu đề khá dài sẽ xuống dòng và chạm vào thẻ bên dưới'},
        {'type': 'card', 'name': '!!c', 'x': 1, 'y': 2.2, 'w': 3, 'h': 3, 'title': 'Thẻ'}]}]}
    _, _, out = build(spec)
    assert 'runs over !!c' in out


def test_stat_unit_beside_value_is_not_a_collision(build):
    spec = {'style': 'noir-product', 'slides': [{'shapes': [
        {'type': 'stat', 'name': '!!k', 'x': 1, 'y': 1.5, 'w': 5, 'value': '5', 'unit': 'giờ / tuần', 'label': 'mỗi tuần'}]}]}
    _, _, out = build(spec)
    assert 'overlap' not in out and 'runs over' not in out
