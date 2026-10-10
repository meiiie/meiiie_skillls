import json

import numpy as np
import pytest
from PIL import Image

import make_assets as M

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="400" viewBox="0 0 200 400">'
       '<g id="head"><rect x="80" y="10" width="40" height="80" fill="#000"/></g>'
       '<g id="neck"><rect x="90" y="90" width="20" height="200" fill="#000"/></g>'
       '<g id="body"><path d="M40,290 L160,290 L140,390 L60,390 Z" fill="#000"/></g></svg>')


@pytest.mark.parametrize('kind', ['lacquer', 'noir', 'paper', 'clean', 'halftone', 'flat'])
def test_ground_kinds_are_textured_not_flat(kind):
    im = M.ground(kind, '#140B08', '#3A2016', size=(480, 270), grain=0.03, seed=2, grid=0.5, dots=0.05)
    a = np.asarray(im, np.float32)
    assert im.size == (480, 270) and im.mode == 'RGB'
    assert a.std() > 1.0  # a material, not a flat fill
    assert abs(a.mean() - np.array(M.hexrgb('#140B08')).mean()) < 60


def test_ground_from_style_pack():
    im = M.style_ground('lacquer-heritage', 'alt', size=(320, 180))
    r, g, b = np.asarray(im, np.float32).reshape(-1, 3).mean(0)
    assert r > g and r > b  # the red lacquer reads red


def test_ground_is_deterministic():
    a = np.asarray(M.ground('paper', '#F3EEE4', size=(200, 120), seed=4))
    b = np.asarray(M.ground('paper', '#F3EEE4', size=(200, 120), seed=4))
    assert (a == b).all()


def test_foil_keeps_shape(tmp_path):
    src = tmp_path / 'o.svg'
    src.write_text(SVG)
    im = M.foil(src, 'gold', size=200)
    a = np.asarray(im)
    assert im.mode == 'RGBA' and im.size == (200, 400)
    assert a[50, 100, 3] > 200 and a[5, 5, 3] < 10  # inside the head vs empty corner
    r, g, b = a[50, 100, :3].astype(int)
    assert r > b + 40  # gold, not grey


@pytest.mark.parametrize('finish', ['silver', 'copper', 'bronze', 'ink', 'chalk', 'neon', 'metal'])
def test_other_finishes(tmp_path, finish):
    src = tmp_path / 'o.svg'
    src.write_text(SVG)
    im = M.foil(src, finish, size=100, color='#6EE7F9')
    assert im.mode == 'RGBA' and np.asarray(im)[:, :, 3].max() > 100


def test_layers_split_on_one_canvas(tmp_path):
    src = tmp_path / 'o.svg'
    src.write_text(SVG)
    made = M.layers(src, tmp_path / 'parts', finish='gold', size=200)
    assert [m['id'] for m in made] == ['head', 'neck', 'body']
    sizes = {Image.open(tmp_path / 'parts' / m['file']).size for m in made}
    assert sizes == {(200, 400)}
    head = np.asarray(Image.open(tmp_path / 'parts' / 'head.png'))
    assert head[350, 100, 3] < 10  # the body region is empty in the head layer
    assert json.loads((tmp_path / 'parts' / 'layers.json').read_text())[0]['id'] == 'head'


def test_photo_duotone_pair(tmp_path, png):
    out = tmp_path / 'hero.jpg'
    M.main(['photo', str(png), '--out', str(out), '--mode', 'duotone', '--colors', '#140B08,#E2BE7C',
            '--aspect', '1:1', '--pair'])
    im = Image.open(out)
    assert im.size[0] == im.size[1]
    assert (tmp_path / 'hero_mono.jpg').exists() and (tmp_path / 'hero_color.jpg').exists()
    assert Image.open(tmp_path / 'hero_color.jpg').size == im.size


def test_glow_and_pattern(tmp_path):
    g = M.glow('#FFB020', size=200)
    a = np.asarray(g)
    assert a[100, 100, 3] > a[10, 10, 3]
    p = M.pattern('woven', 400, 60, '#D9B26A')
    assert p.mode == 'RGBA' and np.asarray(p)[:, :, 3].mean() > 20
    pg = M.pattern('dots', 200, 60, finish='gold')
    assert pg.size == (200, 60)


def test_cli_ground(tmp_path):
    out = tmp_path / 'g.jpg'
    assert M.main(['ground', '--style', 'noir-product', '--name', 'main', '--size', '320x180', '--out', str(out)]) == 0
    assert Image.open(out).size == (320, 180)
