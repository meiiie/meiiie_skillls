"""Audit calibration: the accepted reference deck passes, the failure modes still fail."""
import contextlib
import io
import os
from pathlib import Path

import pytest
from PIL import Image

import check_deck
import motion
import ooxml


def finish(build, tmp_path, spec, name='deck'):
    """build -> unpack -> motion -> pack, like studio.py build."""
    out, _, _ = build(spec, name)
    up = tmp_path / f'{name}_unpacked'
    ooxml.main(['unpack', str(out), str(up)]) if hasattr(ooxml, 'main') else None
    if not up.exists():
        import zipfile
        zipfile.ZipFile(out).extractall(up)
    motion.apply(up, motion.load_config(up, str(out.parent / 'motion.json') if (out.parent / 'motion.json').exists() else None))
    final = tmp_path / f'{name}_final.pptx'
    import zipfile
    with zipfile.ZipFile(final, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(up.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(up).as_posix())
    return final


def fake_renders(tmp_path, n, same_pairs=()):
    """slide-NN.png renders: every slide differs except the listed (a, b) pairs, which are identical."""
    d = tmp_path / 'renders'
    d.mkdir(exist_ok=True)
    colours = {}
    for i in range(1, n + 1):
        colours[i] = (i * 23 % 255, i * 57 % 255, i * 91 % 255)
    for a, b in same_pairs:
        colours[b] = colours[a]
    for i in range(1, n + 1):
        Image.new('RGB', (200, 112), colours[i]).save(d / f'slide-{i:02d}.png')
    return d


def run_check(path, *extra):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            check_deck.main([str(path), *extra])
        except SystemExit as e:
            code = e.code or 0
    return code, buf.getvalue()


def photo_slide(png, title, scene, x=6.5):
    return {'scene': scene, 'notes': 'Lời.', 'shapes': [
        {'type': 'image', 'name': '!!photo', 'path': str(png), 'x': x, 'y': 0, 'w': 6.833, 'h': 7.5},
        {'type': 'text', 'name': '!!title', 'text': title, 'x': 1.0, 'y': 2.5, 'w': 5, 'h': 1, 'size': 36, 'font': 'DejaVu Serif'},
        {'type': 'text', 'name': '!!body', 'text': 'Một đoạn mô tả có đủ chữ để không bị coi là trống trơn.', 'x': 1.0,
         'y': 4, 'w': 5, 'h': 1, 'size': 16, 'font': 'DejaVu Sans'}]}


@pytest.fixture
def photos(tmp_path):
    out = []
    for k in range(6):
        p = tmp_path / f'p{k}.png'
        im = Image.new('RGB', (600, 600), (40 + k * 30, 80, 120))
        for x in range(0, 600, 15 + k):
            for y in range(600):
                im.putpixel((x, y), (250, 240 - k * 20, 200))
        im.save(p)
        out.append(p)
    return out


def test_slogan_deck_with_stuck_photos_fails(build, tmp_path, photos):
    """The Genshin failure: one photo held still while only the words change, scene after scene."""
    slides = []
    for sc, ph in (('S1', photos[0]), ('S2', photos[1])):
        for k in range(4):
            slides.append(photo_slide(ph, f'Khẩu hiệu {k}', sc))
    deck = finish(build, tmp_path, {'slides': slides})
    renders = fake_renders(tmp_path, 8, [(1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (7, 8)])
    code, out = run_check(deck, '--renders', str(renders))
    assert code == 1 and 'keyframe delta' in out


def test_one_hold_beat_is_allowed(build, tmp_path, photos):
    """A deliberate hold (the reference's question beat) is one stuck pair in a long, moving deck."""
    slides = []
    for i in range(12):
        ph = photos[i % 6]
        slides.append(photo_slide(ph, f'Cảnh {i}', f'S{i // 2 + 1}', x=6.5 if i % 2 == 0 else 5.0))
    # slides 3 and 4 share a photo; make the pair a hold (same position, only words change)
    slides[3] = photo_slide(photos[2], 'Bạn có đoán ra chưa?', 'S2', x=6.5)
    slides[2] = photo_slide(photos[2], 'Nhạc cụ nào đang thiếu?', 'S2', x=6.5)
    deck = finish(build, tmp_path, {'slides': slides})
    renders = fake_renders(tmp_path, 12, [(3, 4)])
    code, out = run_check(deck, '--renders', str(renders))
    assert 'hold beat' in out
    assert 'keyframe delta' not in out.split('RESULT')[0].split('ERROR')[-1] or code == 0


def test_two_holds_in_one_scene_fail(build, tmp_path, photos):
    slides = [photo_slide(photos[k % 6], f'Cảnh {k}', f'S{k + 1}', x=6.5 if k % 2 else 5.0) for k in range(12)]
    for k, t in zip((4, 5, 6), ('A', 'B', 'C')):
        slides[k] = photo_slide(photos[4], t, 'S5', x=6.5)
    deck = finish(build, tmp_path, {'slides': slides})
    renders = fake_renders(tmp_path, 12, [(5, 6), (6, 7)])
    code, out = run_check(deck, '--renders', str(renders))
    assert code == 1 and 'keyframe delta' in out


def test_deck_without_a_persistent_layer_fails(build, tmp_path):
    slides = [{'notes': 'n', 'shapes': [{'type': 'text', 'name': f'!!t{i}', 'text': 'Một tiêu đề có vài chữ cho đủ số lượng', 'x': 1, 'y': 1,
                                          'w': 8, 'h': 1, 'size': 30, 'font': 'DejaVu Serif'},
                                         {'type': 'text', 'name': f'b{i}', 'text': 'Thân bài với nhiều chữ hơn để vượt ngưỡng tối thiểu.',
                                          'x': 1, 'y': 3, 'w': 8, 'h': 1, 'size': 16, 'font': 'DejaVu Sans'}]} for i in range(9)]
    deck = finish(build, tmp_path, {'slides': slides})
    code, out = run_check(deck)
    assert code == 1 and 'persistent' in out


def test_styled_deck_has_a_system(build, tmp_path):
    slides = [{'notes': 'n', 'shapes': [
        {'type': 'heading', 'name': '!!h', 'x': 1, 'y': 1.2, 'w': 8, 'kicker': f'PHẦN {i}', 'title': 'Một tiêu đề vừa phải',
         'body': 'Một câu thân bài đủ dài để đọc được và có nghĩa với người nghe.'}]} for i in range(9)]
    deck = finish(build, tmp_path, {'style': 'paper-editorial', 'title': 'Báo cáo', 'slides': slides})
    code, out = run_check(deck)
    assert 'persistent' not in out.split('RESULT')[0].replace('INFO', '') or 'system:' in out
    assert 'system:' in out


def test_fact_ids_on_slides_are_not_required(build, tmp_path):
    (tmp_path / 'facts.md').write_text('| 1.1 | UNESCO 2009 | https://ich.unesco.org | [verified] |\n')
    slides = [{'notes': 'Nguồn 1.1', 'shapes': [{'type': 'heading', 'name': '!!h', 'x': 1, 'y': 1.2, 'w': 8, 'title': 'Năm 2009',
                                                 'body': 'Ca trù được ghi danh vào danh sách cần bảo vệ khẩn cấp.'}]} for _ in range(9)]
    deck = finish(build, tmp_path, {'style': 'lacquer-heritage', 'slides': slides})
    code, out = run_check(deck, '--facts', str(tmp_path / 'facts.md'))
    assert 'carry a fact ID' not in ''.join(l for l in out.splitlines() if l.startswith('ERROR'))


def test_overflow_is_reported(build, tmp_path):
    slides = [{'notes': 'n', 'shapes': [{'type': 'text', 'name': '!!t', 'x': 1, 'y': 1, 'w': 2.5, 'h': 0.6, 'size': 40,
                                         'font': 'DejaVu Sans', 'text': 'Một tiêu đề quá dài cho chiếc hộp nhỏ xíu này'}]}] * 2
    deck = finish(build, tmp_path, {'slides': slides})
    code, out = run_check(deck)
    assert 'overflow' in out


REF = os.environ.get('MOTION_REF_DECK')


@pytest.mark.skipif(not REF or not Path(REF).is_file(), reason='set MOTION_REF_DECK to NEKO_CORE_CaTru_motion.pptx')
def test_reference_deck_passes():
    code, out = run_check(REF, '--anchor', 'Nghe thì lạ, hiểu rồi thương', '--anchor-count', '4')
    assert code == 0, out[-3000:]
    assert 'hold beat' in out


# ---- v5.2 variety audit -------------------------------------------------------------------------

def _mono_slides(n=15):
    return [{'notes': 'n', 'transition': {'type': 'fade'}, 'shapes': [
        {'type': 'text', 'name': '!!t', 'text': f'Tiêu đề số {i}', 'x': 1, 'y': 1, 'w': 8, 'h': 1, 'size': 30,
         'font': 'DejaVu Serif', 'anim': {'fx': 'fade', 'ms': 500}},
        {'type': 'text', 'name': f'b{i}', 'text': 'Thân bài với nhiều chữ hơn để vượt ngưỡng tối thiểu.',
         'x': 1, 'y': 3, 'w': 8, 'h': 1, 'size': 16, 'font': 'DejaVu Sans', 'anim': {'fx': 'fade', 'ms': 500, 'delay': 300}}]}
        for i in range(n)]


def test_monotone_deck_warns_on_variety(build, tmp_path):
    deck = finish(build, tmp_path, {'slides': _mono_slides()})
    code, out = run_check(deck)
    assert 'variety:' in out and 'transition types' in out
    assert 'of all effects' in out          # fade 100%
    assert 'composition: the same layout signature' in out


def test_monotone_deck_fails_under_strict_variety(build, tmp_path):
    deck = finish(build, tmp_path, {'slides': _mono_slides()})
    code, out = run_check(deck, '--variety', 'strict')
    assert code == 1


def test_variety_off_is_silent(build, tmp_path):
    deck = finish(build, tmp_path, {'slides': _mono_slides()})
    code, out = run_check(deck, '--variety', 'off')
    assert 'variety:' not in out


def test_variety_audit_counts_techniques():
    import variety_audit
    from lxml import etree
    P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    empty = etree.fromstring(f'<p:sld xmlns:p="{P}"><p:cSld><p:spTree/></p:cSld></p:sld>')
    e, w, i = variety_audit.audit([('s1', empty)], lambda r: ('fade', None))
    assert not e and not w and i[0].startswith('variety: 0 effect techniques')


def test_rotated_text_uses_rotated_box_for_safe_area(build, tmp_path):
    import build_deck
    spec = {'slides': [{'notes': 'n', 'shapes': [
        {'type': 'text', 'name': 'vert', 'text': '29.400 km', 'rot': 270, 'x': -1.6, 'y': 3.0, 'w': 5.6, 'h': 1.3,
         'size': 60, 'font': 'DejaVu Serif'}]}]}
    out, _, text = build(spec, 'rot')
    assert 'vert: outside the safe area' not in text
    spec['slides'][0]['shapes'][0]['rot'] = 0
    out, _, text = build(spec, 'rot0')
    assert 'vert: outside the safe area' in text
