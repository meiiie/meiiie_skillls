"""v5: motion beyond Morph (transitions, effects, video, links, per-slide styles, poly, gates)."""
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from conftest import NS, SKILL

import gates
import motion
import motionlib
from test_motion import unpacked_deck, slide_xml

WRAP = ('<p:sld xmlns:p="{p}" xmlns:mc="{mc}" xmlns:p14="{p14}" xmlns:p15="{p15}" xmlns:p159="{p159}">'
        .format(p=motionlib.P_NS, mc=motionlib.MC, p14=motionlib.P14, p15=motionlib.P15, p159=motionlib.P159))


@pytest.mark.parametrize('name', sorted(motionlib.TRANSITIONS))
def test_every_transition_is_wellformed_and_reads_back(name):
    if name == 'none':
        return
    x = motionlib.transition_xml({'type': name, 'ms': 900})
    root = etree.fromstring(WRAP + x + '</p:sld>')
    got, ms = motionlib.describe_transition(root)
    assert ms == '900'
    # 'rotate'/'orbit' are written as prism variants and read back as cube; everything else round-trips
    assert got == name or (name in ('rotate', 'orbit') and got == 'cube')


def test_unknown_transition_and_effect_are_refused(build, tmp_path):
    with pytest.raises(SystemExit):
        build({'slides': [{'transition': 'sparkle-unicorn', 'shapes': []}]})
    with pytest.raises(SystemExit):
        build({'slides': [{'shapes': [{'type': 'rect', 'name': 'r', 'x': 1, 'y': 1, 'w': 1, 'h': 1, 'fill': '#FF0000',
                                       'anim': {'fx': 'explode'}}]}]})


def test_timing_census_counts_and_validates():
    effects = [({'fx': 'fly', 'dir': 'l'}, 2), ({'fx': 'pulse', 'loop': True}, 2), ({'fx': 'path', 'path': [[0, 0], [1, 1]]}, 3),
               ({'fx': 'type', 'click': 1}, 4), ({'fx': 'teeter', 'trigger_spid': 3}, 4), ({'fx': 'fadeout', 'click': 2}, 3)]
    xml = motionlib.build_timing(effects, media=[{'spid': 5, 'ms': 4000}], text_ids=[4])
    sld = (WRAP + '<p:cSld><p:spTree>' + ''.join(f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="s{i}"/></p:nvSpPr></p:sp>' for i in (2, 3, 4, 5))
           + '</p:spTree></p:cSld>' + xml + '</p:sld>')
    cen = motionlib.timing_census(etree.fromstring(sld))
    assert cen['errors'] == []
    assert (cen['entr'], cen['emph'], cen['exit'], cen['path'], cen['media'], cen['iterate'], cen['trigger']) == (2, 2, 1, 1, 1, 1, 1)
    assert cen['loop'] >= 2  # the pulse and the video
    bad = sld.replace('spid="3"', 'spid="99"', 1)
    assert any('not on the slide' in e for e in motionlib.timing_census(etree.fromstring(bad))['errors'])


def test_deck_json_transition_anim_link_poly_and_style_switch(build, tmp_path):
    spec = {'style': 'swiss-blue', 'slides': [
        {'id': 'a', 'transition': {'type': 'curtains', 'ms': 1700}, 'shapes': [
            {'type': 'text', 'name': '!!t', 'text': 'Xin chào', 'x': 1, 'y': 1, 'w': 5, 'h': 1, 'role': 'title', 'anim': {'fx': 'type'}},
            {'type': 'rect', 'name': 'go', 'x': 1, 'y': 3, 'w': 1, 'h': 0.5, 'fill': 'accent', 'link': 'b',
             'anim': [{'fx': 'zoom'}, {'fx': 'pulse', 'loop': True}]},
            {'type': 'poly', 'name': '!!tri', 'points': [[6, 3], [8, 3], [7, 5]], 'fill': 'accent2'}]},
        {'id': 'b', 'style': 'blueprint', 'transition': 'fallover', 'shapes': [
            {'type': 'card', 'name': '!!c', 'x': 1, 'y': 1, 'w': 4, 'h': 3, 'title': 'Thẻ', 'desc': 'Mô tả.', 'anim': {'fx': 'rise', 'click': 1}},
            {'type': 'ellipse', 'name': 'dot', 'x': 6, 'y': 6, 'w': 0.2, 'h': 0.2, 'fill': 'lit',
             'anim': {'fx': 'path', 'path': [[0, 0], [3, -2]], 'loop': True, 'trigger': '!!c'}}]},
    ]}
    up = unpacked_deck(build, tmp_path, spec)
    cfg = json.loads((up.parent / 'motion.json').read_text())
    assert cfg['transition']['1']['type'] == 'curtains' and cfg['transition']['2'] == {'type': 'fallover'}
    assert [e['fx'] for e in cfg['effects']['1']] == ['type', 'zoom', 'pulse']
    motion.apply(up, motion.load_config(up, None))
    x1, x2 = slide_xml(up, 1), slide_xml(up, 2)
    assert 'prst="curtains"' in x1 and 'p14:dur="1700"' in x1 and '<p:iterate type="lt"' in x1
    assert 'prst="fallOver"' in x2 and 'interactiveSeq' in x2 and '<p:animMotion' in x2
    assert 'ppaction://hlinksldjump' in x1  # the link
    assert 'custGeom' in x1  # the poly
    # the second slide uses the blueprint ground and palette
    rels2 = (up / 'ppt' / 'slides' / '_rels' / 'slide2.xml.rels').read_text()
    assert 'image' in rels2
    for n in (1, 2):
        cen = motionlib.timing_census(etree.fromstring(slide_xml(up, n).encode()))
        assert cen['errors'] == []


def test_video_shape_gets_autoplay_loop(build, tmp_path):
    mp4 = tmp_path / 'v.mp4'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=320x180:d=1', '-pix_fmt', 'yuv420p', str(mp4)])
    if r.returncode:
        pytest.skip('ffmpeg not available')
    spec = {'slides': [{'shapes': [{'type': 'video', 'name': 'bg', 'path': str(mp4), 'x': 0, 'y': 0, 'w': 13.333, 'h': 7.5}]}]}
    up = unpacked_deck(build, tmp_path, spec)
    motion.apply(up, motion.load_config(up, None))
    x = slide_xml(up, 1)
    assert 'presetClass="mediacall"' in x and '<p:video>' in x and 'repeatCount="indefinite"' in x


def test_gate3_needs_style_choice_and_motion_vocabulary(tmp_path):
    work = tmp_path / 'w'
    gates.main(['init', str(work), '--kind', 'product'])
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            gates.g3(work)
        except SystemExit:
            pass
    out = buf.getvalue()
    assert 'Style choice' in out and 'Motion vocabulary' in out
    ad = work / 'design' / 'art-direction.md'
    ad.write_text(ad.read_text().replace('- chosen: TODO pack(s) and the scenes they cover, and why the subject asks for it',
                                         '- chosen: blueprint for S3, the phin is a machine')
                  .replace('- rejected: TODO a pack you considered and why it is wrong here', '- rejected: paper-editorial, too quiet for a hook')
                  .replace('- TODO e.g. "type (letter by letter)', '- type for the hook, a path for the drop, curtains between chapters; e.g. "type (letter by letter)'))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            gates.g3(work)
        except SystemExit:
            pass
    fails = [l for l in buf.getvalue().splitlines() if 'FAIL' in l]
    assert not any('Style choice' in l or 'Motion vocabulary' in l for l in fails), fails
