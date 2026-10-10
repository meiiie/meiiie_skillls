import json
import shutil
import zipfile
from pathlib import Path

from conftest import NS

import motion
import ooxml


def unpacked_deck(build, tmp_path, spec):
    out, _, _ = build(spec)
    up = tmp_path / 'deck' / 'unpacked'
    up.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out) as z:
        z.extractall(up)
    shutil.copy(out.parent / 'motion.json', up.parent / 'motion.json') if (out.parent / 'motion.json').exists() else None
    return up


def slide_xml(up, n):
    return (up / 'ppt' / 'slides' / f'slide{n}.xml').read_text(encoding='utf-8')


def test_morph_option_per_slide(build, tmp_path):
    spec = {'slides': [{'shapes': []}, {'morph': 'byChar', 'ms': 1800, 'shapes': []}]}
    up = unpacked_deck(build, tmp_path, spec)
    cfg = motion.load_config(up, None)
    motion.apply(up, cfg)
    assert 'option="byObject"' in slide_xml(up, 1)
    x2 = slide_xml(up, 2)
    assert 'option="byChar"' in x2 and 'p14:dur="1800"' in x2


def test_entrances_still_built(build, tmp_path):
    spec = {'slides': [{'shapes': [{'type': 'text', 'name': '@fade1-a', 'text': 'A', 'x': 1, 'y': 1, 'w': 2, 'h': 0.5, 'font': 'DejaVu Sans'},
                                   {'type': 'text', 'name': '@float2-b', 'text': 'B', 'x': 1, 'y': 2, 'w': 2, 'h': 0.5, 'font': 'DejaVu Sans'}]}]}
    up = unpacked_deck(build, tmp_path, spec)
    motion.apply(up, motion.load_config(up, None))
    x = slide_xml(up, 1)
    assert x.count('presetClass="entr"') == 2 and x.count('<p:transition') == 2  # Choice + Fallback


def test_idempotent(build, tmp_path):
    spec = {'slides': [{'shapes': []}]}
    up = unpacked_deck(build, tmp_path, spec)
    cfg = motion.load_config(up, None)
    motion.apply(up, cfg)
    once = slide_xml(up, 1)
    motion.apply(up, cfg)
    assert slide_xml(up, 1) == once
