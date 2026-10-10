import json
import sys
import zipfile
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / 'scripts'))

from lxml import etree  # noqa: E402

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
EMU = 914400


@pytest.fixture
def png(tmp_path):
    """A small RGB test image (wide) on disk."""
    from PIL import Image
    p = tmp_path / 'photo.png'
    im = Image.new('RGB', (400, 200), (120, 80, 40))
    for x in range(0, 400, 20):
        for y in range(200):
            im.putpixel((x, y), (250, 240, 220))
    im.save(p)
    return p


@pytest.fixture
def build(tmp_path):
    """build(spec_dict) -> (pptx_path, slides_xml list, stdout text)."""
    import build_deck

    def _build(spec, name='deck'):
        sp = tmp_path / f'{name}.json'
        sp.write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
        out = tmp_path / f'{name}.pptx'
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            build_deck.main([str(sp), '--out', str(out)])
        return out, slides_xml(out), buf.getvalue()
    return _build


def slides_xml(pptx):
    z = zipfile.ZipFile(pptx)
    names = sorted((n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')),
                   key=lambda n: int(''.join(c for c in n.rsplit('/', 1)[1] if c.isdigit())))
    return [etree.fromstring(z.read(n)) for n in names]


def named(root, name):
    for c in root.iter('{%s}cNvPr' % NS['p']):
        if c.get('name') == name:
            return c.getparent().getparent()
    return None


def names(root):
    return [c.get('name') for c in root.iter('{%s}cNvPr' % NS['p'])]


def box(el):
    xfrm = el.find('.//{%s}xfrm' % NS['a'])
    if xfrm is None:
        xfrm = el.find('.//{%s}xfrm' % NS['p'])
    off = xfrm.find('{%s}off' % NS['a'])
    ext = xfrm.find('{%s}ext' % NS['a'])
    return tuple(round(int(v) / EMU, 3) for v in (off.get('x'), off.get('y'), ext.get('cx'), ext.get('cy')))


def text(el):
    return ''.join(t.text or '' for t in el.iter('{%s}t' % NS['a']))
