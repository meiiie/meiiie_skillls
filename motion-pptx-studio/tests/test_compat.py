"""v5.1: no-Morph safe mode (compat morph|safe|dual), Morph->classic rebuild, no-Morph gate."""
import subprocess
import sys

import pytest
from lxml import etree

from conftest import SKILL

import compat
import motion
import motionlib

SCRIPTS = SKILL / 'scripts'


def deck(mode, **extra):
    d = {'style': 'swiss-blue', 'title': 'T', 'slides': [
        {'id': 'a', 'shapes': [
            {'type': 'rect', 'name': '!!dot', 'x': 1, 'y': 1, 'w': 1, 'h': 1, 'fill': '#1F4FE0'},
            {'type': 'text', 'name': '!!t', 'text': 'Một', 'x': 1, 'y': 4, 'w': 6, 'h': 1}]},
        {'id': 'b', 'morph': 'byChar', 'shapes': [
            {'type': 'rect', 'name': '!!dot', 'x': 8, 'y': 3, 'w': 1, 'h': 1, 'fill': '#1F4FE0'},
            {'type': 'text', 'name': '!!t', 'text': 'Hai', 'x': 1, 'y': 4, 'w': 6, 'h': 1},
            {'type': 'rect', 'name': '!!new', 'x': 4, 'y': 1, 'w': 1, 'h': 1, 'fill': '#000000'}]}]}
    if mode:
        d['compat'] = mode
    d.update(extra)
    return d


def run_pipeline(build, tmp_path, spec):
    out, _, _ = build(spec)
    up = tmp_path / 'up'
    subprocess.run([sys.executable, str(SCRIPTS / 'ooxml.py'), 'unpack', str(out), str(up)], check=True, capture_output=True)
    cfg = motion.load_config(up, None)
    report, _ = motion.apply(up, cfg)
    roots = [etree.parse(str(up / 'ppt' / 'slides' / f'slide{i}.xml')).getroot() for i in (1, 2)]
    return roots, report, up


def presets(root):
    return [c.get('presetClass') + ':' + c.get('presetID') for c in root.iter('{%s}cTn' % motionlib.P_NS) if c.get('presetClass')]


def test_mode_validation():
    assert compat.check_mode(None) == 'morph'
    with pytest.raises(ValueError):
        compat.check_mode('fast')


def test_plan_safe_rebuilds_moves_text_and_new_shapes():
    prev = {'!!a': {'id': '2', 'box': (1, 1, 1, 1), 'text': '', 'kind': 'sp'},
            '!!t': {'id': '3', 'box': (1, 4, 6, 1), 'text': 'x', 'kind': 'sp'},
            '!!g': {'id': '5', 'box': (1, 1, 1, 1), 'text': '', 'kind': 'sp'}}
    cur = {'!!a': {'id': '2', 'box': (8, 3, 1, 1), 'text': '', 'kind': 'sp'},
           '!!t': {'id': '3', 'box': (1, 4, 6, 1), 'text': 'y', 'kind': 'sp'},
           '!!g': {'id': '5', 'box': (0.75, 0.75, 1.5, 1.5), 'text': '', 'kind': 'sp'},
           '!!n': {'id': '4', 'box': (2, 2, 1, 1), 'text': '', 'kind': 'sp'}}
    t, fx = compat.plan(prev, cur, 'safe', 1300, 'byChar')
    assert t == {'type': 'fade', 'ms': 800}
    got = {(e['shape'], e['fx']) for e in fx}
    assert {('!!a', 'appear'), ('!!a', 'path'), ('!!t', 'type'), ('!!g', 'zoom'), ('!!n', 'fade')} <= got
    path = next(e for e in fx if e['fx'] == 'path')
    assert path['path'][0] == [-7.0, -2.0] and path['from_offset']
    t, fx = compat.plan(prev, cur, 'dual', 1300)
    assert t['type'] == 'morph' and t['fallback'] == {'type': 'push', 'dir': 'r'}
    assert [e['shape'] for e in fx] == ['!!n']          # dual never animates paired shapes
    assert compat.plan(prev, cur, 'safe', taken={'!!a', '!!t', '!!g', '!!n'})[1] == []
    with pytest.raises(ValueError):
        compat.plan(prev, cur, 'safe', safe_transition='vortex')


def test_from_offset_path_starts_away_from_shape():
    ids = motionlib.Ids(3)
    x = motionlib.effect_par({'fx': 'path', 'path': [[-2, 0], [0, 0]], 'from_offset': True}, '4', 0, ids)
    assert 'path="M -0.15 0 L 0 0 E"' in x
    x = motionlib.effect_par({'fx': 'path', 'path': [[-2, 0]]}, '4', 0, motionlib.Ids(3))
    assert 'path="M 0 0 L -0.15 0 E"' in x


def test_morph_fallback_transition():
    x = motionlib.transition_xml({'type': 'morph', 'fallback': {'type': 'wipe', 'dir': 'l'}, 'advance_ms': 3000})
    fb = x[x.index('<mc:Fallback>'):]
    assert '<p:wipe dir="l"/>' in fb and 'advTm="3000"' in fb and 'p159' not in fb
    with pytest.raises(ValueError):
        motionlib.transition_xml({'type': 'morph', 'fallback': 'vortex'})


def test_safe_pipeline_has_no_morph_and_passes_audit(build, tmp_path):
    roots, report, _ = run_pipeline(build, tmp_path, deck('safe'))
    assert not any(compat.has_morph(r) for r in roots)
    assert motionlib.describe_transition(roots[1])[0] == 'fade'
    p = presets(roots[1])
    assert 'path:0' in p and 'entr:1' in p                 # appear + motion path for the moved dot
    assert any(x.startswith('entr:10') for x in p)          # fade for !!new, type for !!t
    assert 'compat=safe' in report[-1]
    errors, _, infos = compat.audit([('s1', roots[0]), ('s2', roots[1])], 'safe')
    assert errors == [] and '0 shared-shape' in infos[-1]


def test_dual_pipeline_keeps_morph_with_classic_fallback(build, tmp_path):
    roots, _, _ = run_pipeline(build, tmp_path, deck('dual'))
    assert compat.has_morph(roots[1])
    fb = roots[1].find('.//{%s}Fallback/{%s}transition' % (motionlib.MC, motionlib.P_NS))
    assert etree.QName(fb[0]).localname == 'push'
    assert 'path:0' not in presets(roots[1])
    n = compat.strip_morph(roots[1])
    assert n == 1 and not compat.has_morph(roots[1])
    assert etree.QName(roots[1].find('{%s}transition' % motionlib.P_NS)[0]).localname == 'push'


def test_audit_flags_morph_left_and_lost_moves(build, tmp_path):
    roots, _, _ = run_pipeline(build, tmp_path, deck(None))
    errors, _, _ = compat.audit([('s1', roots[0]), ('s2', roots[1])], 'safe')
    assert any('still carries a Morph' in e for e in errors)
    assert any('!!dot' in e and 'jumps' in e for e in errors)
    errors, _, infos = compat.audit([('s1', roots[0]), ('s2', roots[1])], 'dual')
    assert errors == [] and any('!!dot' in i for i in infos)
    # a deliberate push is allowed to jump
    errors, _, _ = compat.audit([('s1', roots[0]), ('s2', roots[1])], 'safe', morph_slides=set())
    assert not any('jumps' in e for e in errors)


def test_check_deck_compat_gate(build, tmp_path):
    out, _, _ = build(deck(None), name='plain')
    r = subprocess.run([sys.executable, str(SCRIPTS / 'check_deck.py'), str(out), '--compat', 'safe'], capture_output=True, text=True)
    assert 'no-Morph' in r.stdout and 'still carries a Morph' not in r.stdout   # build_deck alone writes no transition


def test_unknown_compat_refused(build):
    with pytest.raises(SystemExit):
        build(deck('fast'))


def test_compare_renders(tmp_path):
    from PIL import Image
    a, b = tmp_path / 'a', tmp_path / 'b'
    a.mkdir()
    b.mkdir()
    im = Image.new('L', (40, 20), 0)
    for x in range(0, 40, 4):
        for y in range(20):
            im.putpixel((x, y), 255)
    im.save(a / 'slide-01.jpg')
    im.save(b / 'slide-01.jpg')
    assert compat.compare_renders(a, b)[0] == []
    Image.new('L', (40, 20), 255).save(b / 'slide-01.jpg')
    errs = compat.compare_renders(a, b)[0]
    assert any('differs' in e for e in errs) and any('blank' in e for e in errs)
