"""v5.5: self-routing (subject/tone/asset analysis, written rejections, gate 3), the per-deck genome
(compiled style + art-direction.md, rendered-ground contrast), construction motion (Anatomy/Manim verbs,
one lit part, camera on the rest geometry), stretch/indicate presets and their simulation."""
import contextlib
import io
import json
from pathlib import Path

import pytest
from PIL import Image

from conftest import NS, SKILL, named

P_NS = NS['p']


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


AERO = """# Brief
- topic: Falcon 9 booster landing and reuse: grid fins, landing legs, Merlin engines, the launch and the return
- audience: general public interested in technology
- tone: technical, precise, cinematic
- deliverable_kind: product
"""
HERITAGE = """# Brief
- topic: Đồ Sơn, khu nghỉ mát di sản trăm năm, hải đăng Hòn Dáu, bưu ảnh 1905, lịch sử và văn hóa
- audience: người Hải Phòng, lớp học lịch sử
- tone: warm, nostalgic, calm
- deliverable_kind: heritage
"""


def work_with(tmp_path, name, brief, pics):
    w = tmp_path / name
    (w / 'assets').mkdir(parents=True)
    (w / 'brief.md').write_text(brief, encoding='utf-8')
    for fn, col in pics:
        im = Image.new('RGB', (96, 64), col)
        for x in range(0, 96, 8):
            for y in range(64):
                im.putpixel((x, y), tuple(min(255, c + 25) for c in col))
        im.save(w / 'assets' / fn)
    return w


@pytest.fixture
def aero(tmp_path):
    return work_with(tmp_path, 'aero', AERO, [('01_night_landing.jpg', (8, 10, 22)), ('02_pad.jpg', (20, 30, 60)), ('03_stage.jpg', (90, 100, 120))])


@pytest.fixture
def heri(tmp_path):
    return work_with(tmp_path, 'heri', HERITAGE, [('15_terrace_1905.jpg', (150, 135, 110)), ('16_net_1905.jpg', (120, 110, 95)),
                                                  ('09_lighthouse.jpg', (180, 170, 150))])


# ------------------------------------------------------------------ routing

def test_route_rejects_heritage_collage_for_aerospace_with_a_written_reason(aero):
    import route
    dec = route.route(aero)
    assert dec['chosen'] and dec['chosen'] != 'heritage-collage'
    assert 'heritage-collage' in dec['rejected']
    assert 'aerospace' in dec['rejected']['heritage-collage'][0]
    assert (aero / 'design/routing.md').is_file() and 'heritage-collage' in (aero / 'design/routing.md').read_text(encoding='utf-8')


def test_route_rejects_noir_for_heritage_and_reads_old_prints(heri):
    import route
    dec = route.route(heri)
    assert dec['chosen'] not in dec['rejected'] and 'noir-product' in dec['rejected']
    assert dec['material']['archival'] > 0.5 and 1905 in dec['material']['old_dates']
    assert dec['subject']['domains'].get('heritage') == 1.0


def test_route_choose_refuses_a_rejected_family_and_a_thin_reason(aero):
    import route
    with pytest.raises(SystemExit, match='rejected'):
        route.route(aero, 'heritage-collage', 'because I like it a lot and it is pretty nice')
    with pytest.raises(SystemExit, match='8\\+ words'):
        route.route(aero, 'swiss-blue', 'cleaner')
    dec = route.route(aero, 'swiss-blue', 'a white data sheet suits the timeline better than the black stage here')
    assert dec['chosen'] == 'swiss-blue' and dec['how'] == 'author'


def test_gate3_fails_without_routing_and_when_the_deck_uses_a_rejected_family(aero):
    import route
    need, _ = route.gate_rows(aero)
    assert need and not need[0][0] and 'routing.json' in need[0][1]
    route.route(aero)
    st = json.loads((SKILL / 'assets/styles/heritage-collage.json').read_text(encoding='utf-8'))
    st['route'] = 'heritage-collage'
    (aero / 'design/style.json').write_text(json.dumps(st), encoding='utf-8')
    need, _ = route.gate_rows(aero)
    bad = [r for r in need if not r[0]]
    assert bad and 'avoid the rejected' in bad[0][1] and 'aerospace' in bad[0][2]


def test_studio_route_apply_copies_the_chosen_family_and_new_refuses_a_rejected_style(aero):
    import studio
    code, out = call(studio.main, ['route', str(aero), '--apply'])
    assert code == 0, out
    st = json.loads((aero / 'design/style.json').read_text(encoding='utf-8'))
    dec = json.loads((aero / 'design/routing.json').read_text(encoding='utf-8'))
    assert st['route'] == dec['chosen']
    assert studio.rejected_by_routing(aero, 'heritage-collage')


def test_every_pack_has_a_fit_block_with_avoid_reasons():
    import route
    pk = route.packs()
    assert len(pk) >= 10
    for name, c in pk.items():
        assert c['fit'], name
    hc = pk['heritage-collage']['fit']
    assert any(a['domain'] == 'aerospace' and len(a['reason'].split()) >= 8 for a in hc['avoid'])


# ------------------------------------------------------------------ genome

def test_genome_compile_holds_contrast_on_the_rendered_ground_and_a_short_scale(tmp_path):
    import genome
    g = {'route': 'heritage-collage', 'light': 'light', 'palette': {'ground': '#EFE6D2', 'ink': '#6A5A4A', 'accent': '#7FB0B4'},
         'type': {'display': 'Cormorant Garamond', 'text': 'Lora', 'ratio': 1.333, 'body': 16},
         'material': {'kind': 'paper', 'stains': 0.5, 'tone': '#E2D3B4'}}
    st = genome.compile_genome(g, tmp_path)
    p = st['palette']
    assert genome.contrast(p['ink'], p['ground']) >= 7.0
    assert genome.contrast(p['kick'], p['ground']) >= 4.6 and genome.contrast(p['muted'], p['ground']) >= 5.0
    assert genome.contrast(p['muted'], genome.mix('#E2D3B4', '#000000', 0.15)) >= 4.5   # stained edge
    assert len({r['size'] for r in st['type'].values()}) <= 8
    assert st['grounds']['main']['kind'] == 'paper' and 'fit' not in st


def test_genome_writes_art_direction_that_passes_the_palette_source_check(tmp_path):
    import genome
    import visual_audit
    (tmp_path / 'design').mkdir()
    g = {'name': 'x', 'route': 'noir-product', 'palette': {'ground': '#0C0705', 'ink': '#F2F2EE', 'accent': '#FF7A1F'},
         'why': {'palette': 'from the night photo', 'motion': 'built bottom-up'}, 'arc': ['S1 #0C0705', 'S2 #F2F2EE'],
         'motion': {'verbs': ['create', 'grow', 'camera']}, 'signature': 'the stage'}
    st = genome.compile_genome(g, tmp_path)
    md = genome.art_direction_md(g, st, tmp_path)
    hexes, unsourced = visual_audit.palette_report(md)
    assert len(hexes) >= 3 and not unsourced
    assert visual_audit.colour_arc_ok(md)[0]
    assert 'stretch' in md and 'wipe' in md


def test_deck_distance_is_zero_for_the_same_deck_and_positive_for_different_ones(build):
    import genome
    a, _, _ = build({'slides': [{'shapes': [{'type': 'text', 'name': 't', 'text': 'Hello', 'x': 1, 'y': 1, 'w': 5, 'h': 1, 'size': 40}]}]}, 'a')
    b, _, _ = build({'slides': [{'transition': 'push', 'shapes': [
        {'type': 'rect', 'name': 'r', 'x': 6, 'y': 4, 'w': 6, 'h': 3, 'fill': '#FF0000', 'anim': {'fx': 'wipe'}},
        {'type': 'text', 'name': 't', 'text': 'Other', 'x': 7, 'y': 5, 'w': 5, 'h': 1, 'size': 14, 'font': 'Lora'}]}]}, 'b')
    fa, fb = genome.deck_fingerprint(str(a)), genome.deck_fingerprint(str(b))
    assert genome.deck_distance(fa, fa)['overall'] == 0
    assert genome.deck_distance(fa, fb)['overall'] > 0.2


# ------------------------------------------------------------------ construction motion

STAGE = [
    {'id': 'deck', 'kind': 'iso_box', 'layer': 'base', 'box': [-3, -3, -0.5, 6, 6, 0.5], 'fill': '#333333'},
    {'id': 'body', 'kind': 'iso_cyl', 'layer': 'structure', 'on': 'deck', 'box': [-1, -1, 0, 2, 2, 6], 'fill': '#DDDDDD'},
    {'id': 'cap', 'kind': 'rect', 'layer': 'control', 'on': 'body', 'at': [-0.5, -8, 1, 1], 'fill': '#777777', 'lit': True,
     'states': {'up': {'at': [-0.5, -9, 1, 1]}}},
    {'id': 'ring', 'kind': 'ellipse', 'layer': 'mechanism', 'on': 'body', 'at': [-1.5, -5, 3, 1], 'line': '#FFFFFF'},
    {'id': 'wire', 'kind': 'line', 'layer': 'mechanism', 'on': 'body', 'points': [[1, -2], [4, -2]], 'line': '#FFFFFF'},
    {'id': 'lab', 'kind': 'text', 'layer': 'label', 'on': 'cap', 'text': 'CAP', 'at': [2, -8, 1.2, 0.3]},
]


def test_build_order_is_base_structure_mechanism_with_labels_after_their_part():
    import construct
    order = [i for st in construct.build_order(STAGE) for i in st]
    assert order.index('deck') < order.index('body') < order.index('cap')
    assert order.index('lab') == order.index('cap') + 1


def test_verbs_follow_the_part_kind():
    import construct
    by = {p['id']: p for p in STAGE}
    assert construct.choose_verb(by['wire'], by['body'], None) == ('create', 'l')
    assert construct.choose_verb(by['lab'], by['cap'], None)[0] == 'write'
    assert construct.choose_verb(by['ring'], by['body'], None)[0] == 'sweep'
    v, d = construct.choose_verb(by['cap'], by['body'], None)
    assert v == 'grow' and d == 'b'                                      # rises off what it sits on
    assert construct.anims_for('write', None, 0, 600)[0]['by'] == 'letter'


def test_construct_builds_native_effects_and_one_lit_part(build):
    import construct
    import motionlib
    sh = {'type': 'construct', 'name': 'm', 'parts': STAGE, 'x': 1, 'y': 0.5, 'w': 6, 'h': 6.5, 'reveal': True, 'indicate': ['cap']}
    prims = {s['name']: s for s in construct.comp_construct(None, sh)}
    fx = {n: [a['fx'] for a in s.get('anim', [])] for n, s in prims.items()}
    assert fx['!!m.deck.top'] == ['stretch'] and fx['!!m.body.body'] == ['stretch']      # solids grow from their contact edge
    assert fx['!!m.wire'] == ['wipe'] and fx['!!m.ring'] == ['wheel'] and fx['!!m.lab'] == ['type']
    assert fx['!!m.cap'] == ['stretch', 'indicate']
    d = [prims[n]['anim'][0]['delay'] for n in ('!!m.deck.top', '!!m.body.body', '!!m.cap', '!!m.lab')]
    assert d == sorted(d) and d[0] < d[-1]                                               # LaggedStart in build order
    xml = motionlib.build_timing([(prims['!!m.body.body']['anim'][0], 5), (prims['!!m.ring']['anim'][0], 6)])
    assert 'presetID="17"' in xml and 'ppt_w' in xml and 'presetID="21"' in xml
    _, slides, _ = build({'compat': 'morph', 'slides': [{'shapes': [sh]}]})
    assert named(slides[0], '!!m.body.body') is not None and named(slides[0], '!!m.deck.top') is not None
    two = [dict(p, lit=True) if p['id'] == 'wire' else p for p in STAGE]
    with pytest.raises(SystemExit, match='one lit part'):
        construct.comp_construct(None, dict(sh, parts=two))
    grouped = [dict(p, group='g') if p['id'] in ('wire', 'cap') else p for p in two]
    assert construct.comp_construct(None, dict(sh, parts=grouped))


def test_states_and_camera_share_the_rest_fit(build):
    from conftest import box
    base = {'type': 'construct', 'name': 'm', 'parts': STAGE, 'x': 1, 'y': 0.5, 'w': 6, 'h': 6.5}
    _, slides, _ = build({'compat': 'morph', 'slides': [{'shapes': [dict(base, state='rest')]}, {'shapes': [dict(base, state='up')]},
                                                       {'shapes': [dict(base, state='up', camera={'focus': 'cap', 'zoom': 2.0})]}]})
    b0, b1, b2 = (box(named(s, '!!m.body.body')) for s in slides)
    c0, c1 = box(named(slides[0], '!!m.cap')), box(named(slides[1], '!!m.cap'))
    assert b0 == b1 and c0[1] > c1[1]                    # a state change moves only the part that changed
    assert b2[2] == pytest.approx(b1[2] * 2, rel=0.02)   # the camera scales everything by its zoom


# ------------------------------------------------------------------ presets + simulation

def test_motionlib_stretch_and_indicate_presets():
    import motionlib
    assert motionlib.PRESETS['stretch'] == ('entr', 17) and motionlib.PRESETS['indicate'] == ('emph', 6)
    assert set(motionlib.STRETCH) >= {'t', 'b', 'l', 'r', 'h', 'v'}


def test_preview_sweep_mask_and_stretch_paste():
    import preview_motion as pm
    m = pm.sweep_mask((100, 100), 0.25)
    import numpy as np
    a = np.asarray(m, dtype=float)
    assert 0.15 < a.mean() < 0.4                         # a quarter of the wheel
    canvas = Image.new('RGBA', (200, 200), (0, 0, 0, 255))
    sprite = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
    pm.paste(canvas, sprite, 50, 50, stretch=('b', 0.5))
    px = np.asarray(canvas.convert('L'), dtype=float)
    assert px[140, 100] > 200 and px[60, 100] < 50       # grown from the bottom edge, half way
    assert pm.STRETCH_SUB[4] == 'b'
