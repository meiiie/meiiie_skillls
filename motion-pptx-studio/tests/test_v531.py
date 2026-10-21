"""v5.3.1: film/label overlap, film/page colour, Anatomy figure audit, fast shape ids, direction aliases."""
import json
from collections import Counter

import pytest
from lxml import etree

import film_audit
import motionlib
from conftest import NS

P_NS, A_NS = NS['p'], NS['a']
EMU = 914400


def _sp(name, x, y, w, h, text=None, video=False, sid=2):
    off = f'<a:off x="{int(x * EMU)}" y="{int(y * EMU)}"/><a:ext cx="{int(w * EMU)}" cy="{int(h * EMU)}"/>'
    if video:
        return (f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvPicPr/><p:nvPr><a:videoFile r:link="rId9"/></p:nvPr></p:nvPicPr>'
                f'<p:blipFill><a:blip r:embed="rId2"/></p:blipFill><p:spPr><a:xfrm>{off}</a:xfrm></p:spPr></p:pic>')
    body = f'<p:txBody><a:bodyPr/><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody>' if text else ''
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>{off}</a:xfrm></p:spPr>{body}</p:sp>'


def _slide(*parts):
    xml = (f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{NS["r"]}"><p:cSld><p:spTree>'
           '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>' + ''.join(parts) + '</p:spTree></p:cSld></p:sld>')
    return etree.fromstring(xml.encode())


def test_text_under_a_video_is_reported_and_text_above_is_not():
    label = _sp('!!st-weld', 4.5, 2.4, 2.0, 0.6, 'Hàn', sid=3)
    film = _sp('!!film-line', 0.45, 2.3, 12.4, 4.3, video=True, sid=4)
    assert len(film_audit.video_covers_text(_slide(label, film))) == 1          # label drawn first = hidden under the film
    assert film_audit.video_covers_text(_slide(film, label)) == []              # label on top = a deliberate overlay
    outside = _sp('!!st-weld', 4.5, 1.6, 2.0, 0.6, 'Hàn', sid=3)
    assert film_audit.video_covers_text(_slide(outside, film)) == []


def _poster_and_render(tmp_path, card, page):
    from PIL import Image
    poster = Image.new('RGB', (400, 150), card)
    for x in range(120, 280):
        for y in range(40, 110):
            poster.putpixel((x, y), (20, 80, 200))
    pb = tmp_path / 'poster.png'
    poster.save(pb)
    render = Image.new('RGB', (1333, 750), page)
    render.paste(poster.resize((1160, 406)), (87, 260))
    rp = tmp_path / 'slide-10.jpg'
    render.save(rp, quality=95)
    rels = (b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            b'<Relationship Id="rId2" Type="image" Target="../media/image1.png"/></Relationships>')
    files = {'ppt/slides/_rels/slide10.xml.rels': rels, 'ppt/media/image1.png': pb.read_bytes()}
    root = _slide(_sp('!!film-line', 0.87, 2.6, 11.6, 4.06, video=True))
    return files.__getitem__, root, rp


def test_film_card_must_match_the_page_around_it(tmp_path):
    read, root, rp = _poster_and_render(tmp_path, (255, 255, 255), (243, 246, 253))
    errors, _ = film_audit.film_edge_match(read, 'ppt/slides/slide10.xml', root, rp)
    assert errors and 'differs from the page' in errors[0]
    read, root, rp = _poster_and_render(tmp_path, (255, 255, 255), (255, 255, 255))
    assert film_audit.film_edge_match(read, 'ppt/slides/slide10.xml', root, rp) == ([], [])


def _figure(tmp_path, name, size, face, edge, solids):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (1000, 400), (10, 26, 51))
    d = ImageDraw.Draw(im)
    w, h = size
    box = (500 - w // 2, 200 - h // 2, 500 + w // 2, 200 + h // 2)
    d.rectangle(box, fill=face, outline=edge, width=3)
    for x in range(box[0], box[2], 40):
        d.line([(x, box[1]), (x, box[3])], fill=edge, width=2)
    png = tmp_path / f'{name}.png'
    im.save(png)
    svg = tmp_path / f'{name}.svg'
    svg.write_text('<svg>' + '<g class="iso-solid"/>' * solids + '</svg>')
    return png, svg


def test_figure_audit_flags_a_small_dim_sparse_figure(tmp_path):
    import anatomy_film
    au = anatomy_film.figure_audit(*_figure(tmp_path, 'dim', (420, 160), (22, 40, 74), (60, 90, 140), 60))
    text = ' '.join(au['warnings'])
    assert au['solids'] == 60 and 'solids' in text
    assert au['fill_w'] < 0.7 and 'fills' in text
    assert 'edges' in text and 'faces' in text


def test_figure_audit_passes_a_dense_bright_full_figure(tmp_path):
    import anatomy_film
    au = anatomy_film.figure_audit(*_figure(tmp_path, 'bright', (820, 300), (52, 96, 178), (242, 246, 255), 170))
    assert au['warnings'] == [], au
    assert au['fill_w'] >= 0.7 and au['line_contrast'] >= 4.5


def test_big_groups_keep_unique_shape_ids(build):
    parts = [{'type': 'rect', 'name': f'p{i}', 'x': 0.5 + (i % 40) * 0.3, 'y': 0.5 + (i // 40) * 0.3, 'w': 0.2, 'h': 0.2, 'fill': '#1464F4'}
             for i in range(400)]
    spec = {'slides': [{'shapes': [{'type': 'group', 'name': '!!g', 'shapes': parts},
                                   {'type': 'text', 'name': 't', 'text': 'x', 'x': 1, 'y': 6, 'w': 2, 'h': 0.5}]}] * 2}
    _, sl, _ = build(spec)
    for root in sl:
        ids = Counter(c.get('id') for c in root.iter('{%s}cNvPr' % P_NS))
        assert max(ids.values()) == 1
        assert sum(ids.values()) >= 403
        grp = root.find('.//{%s}grpSp' % P_NS)
        ext = grp.find('{%s}grpSpPr/{%s}xfrm/{%s}ext' % (P_NS, A_NS, A_NS))
        assert int(ext.get('cx')) / EMU == pytest.approx(39 * 0.3 + 0.2, abs=0.02)   # extents recalculated once at the end


@pytest.mark.parametrize('d,sub', [('u', 4), ('d', 1), ('b', 4), ('t', 1)])
def test_effect_directions_accept_transition_style_aliases(d, sub):
    n = iter(range(100, 1000))
    xml = motionlib.effect_par({'fx': 'wipe', 'dir': d}, 5, 0, lambda: next(n))
    assert f'presetSubtype="{sub}"' in xml


def test_the_reference_carries_the_new_rules():
    from pathlib import Path
    ref = Path(film_audit.__file__).resolve().parent.parent / 'references' / 'signature-moments.md'
    text = ref.read_text(encoding='utf-8')
    assert 'Density and contrast' in text and 'Film and page colour' in text and 'Labels never sit under a film' in text


@pytest.mark.skipif(__import__('shutil').which('ffmpeg') is None, reason='ffmpeg')
def test_signature_gate_reads_the_anatomy_figure_audit(tmp_path, png):
    import shutil
    import subprocess
    import gates
    from test_v53 import MECH, sig_table, sig_work, write
    work = sig_work(tmp_path)
    film = work / 'assets/film'
    film.mkdir(parents=True, exist_ok=True)
    for n in ('a', 'b'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=10:duration=4',
                        '-pix_fmt', 'yuv420p', str(film / f'{n}.mp4')], check=True)
        shutil.copy(png, film / f'{n}.poster.png')
    write(film / 'a.shapes.json', '{}')
    write(work / 'design/signature-moments.md', sig_table([('Line', 'anatomy', MECH, 'assets/film/a.mp4', 'assets/film/a.shapes.json'),
                                                           ('Pack', 'manim', MECH, 'assets/film/b.mp4', '!!cap')]))
    _, info = gates.signature_report(work, 'film')
    assert any(i.startswith('WARN') and 'no figure audit' in i for i in info), info
    write(film / 'a/film.json', json.dumps({'audit': {'line_contrast': 2.1, 'warnings': ['69 solids < 120: add parts']}}))
    errs, info = gates.signature_report(work, 'film')
    assert any('edges reach only 2.1:1' in e for e in errs), errs
    assert any(i.startswith('WARN') and '69 solids' in i for i in info), info
    write(film / 'a/film.json', json.dumps({'audit': {'line_contrast': 9.9, 'warnings': []}}))
    errs, info = gates.signature_report(work, 'film')
    assert errs == [] and not any(i.startswith('WARN') for i in info), (errs, info)
