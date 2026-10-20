"""Round-trip the deck's motion through LibreOffice Impress and compare what survives.

  python verify_motion.py DECK.pptx [--keep DIR]

Converts the .pptx to .odp with soffice (headless) and counts, per slide, the transition and the
animation nodes LibreOffice imported (anim:par with presentation:preset-class, anim:animateMotion,
anim:iterate, anim:audio/video commands) against what the .pptx authors (motionlib.timing_census).
A slide whose effects drop to zero in the round trip has XML that LibreOffice could not parse:
look at it before trusting PowerPoint with it. LibreOffice does not import every PowerPoint 2013+
transition (Curtains, Fall Over, ... appear as a basic one or none): those are reported as INFO,
since they still play in PowerPoint 365/2019+.
Exit code 1 when a slide that authors effects imports none.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motionlib  # noqa: E402

NS = {'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
      'anim': 'urn:oasis:names:tc:opendocument:xmlns:animation:1.0',
      'presentation': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0',
      'smil': 'urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0',
      'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'}


def authored(pptx):
    z = zipfile.ZipFile(pptx)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    rels = etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    out = []
    for sid in pres.iter('{http://schemas.openxmlformats.org/presentationml/2006/main}sldId'):
        rid = sid.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        root = etree.fromstring(z.read('ppt/' + rmap[rid]))
        cen = motionlib.timing_census(root)
        name, ms = motionlib.describe_transition(root)
        out.append((name, ms, cen))
    return out


def imported(odp):
    z = zipfile.ZipFile(odp)
    root = etree.fromstring(z.read('content.xml'))
    styles = {}
    for st in root.iter('{%s}style' % NS['style']):
        dp = st.find('{%s}drawing-page-properties' % NS['style'])
        if dp is not None:
            styles[st.get('{%s}name' % NS['style'])] = (dp.get('{%s}type' % NS['smil']) or dp.get('{%s}transition-type' % NS['presentation']) or '',
                                                        dp.get('{%s}subtype' % NS['smil']) or '')
    out = []
    for page in root.iter('{%s}page' % NS['draw']):
        tr = styles.get(page.get('{%s}style-name' % NS['draw']), ('', ''))
        classes = {}
        for el in page.iter():
            if not isinstance(el.tag, str):
                continue
            pc = el.get('{%s}preset-class' % NS['presentation'])
            if pc and el.get('{%s}node-type' % NS['presentation']) in ('on-click', 'with-previous', 'after-previous'):
                classes[pc] = classes.get(pc, 0) + 1
        motion_n = len(page.findall('.//{%s}animateMotion' % NS['anim']))
        iterate = len(page.findall('.//{%s}iterate' % NS['anim']))
        out.append((tr, classes, motion_n, iterate))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck')
    ap.add_argument('--keep', help='keep the .odp in this folder')
    a = ap.parse_args(argv)
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    if not soffice:
        print('soffice not found: install LibreOffice to verify motion'); return 2
    tmp = Path(tempfile.mkdtemp(prefix='vm-'))
    subprocess.run([soffice, '--headless', f'-env:UserInstallation=file://{tmp}/profile', '--convert-to', 'odp',
                    '--outdir', str(tmp), a.deck], capture_output=True, timeout=600)
    odp = tmp / (Path(a.deck).stem + '.odp')
    if not odp.exists():
        print('ERROR LibreOffice could not open/convert the deck'); return 1
    if a.keep:
        Path(a.keep).mkdir(parents=True, exist_ok=True)
        shutil.copy(odp, a.keep)
    au, im = authored(a.deck), imported(odp)
    bad = 0
    if len(au) != len(im):
        print(f'ERROR slide count differs: pptx {len(au)} vs odp {len(im)}'); bad += 1
    for i, ((name, ms, cen), (tr, classes, mot, it)) in enumerate(zip(au, im), 1):
        n_auth = cen['entr'] + cen['emph'] + cen['exit'] + cen['path']
        n_imp = sum(classes.get(k, 0) for k in ('entrance', 'emphasis', 'exit', 'motion-path'))
        flag = 'OK  '
        if n_auth and not n_imp:
            flag, bad = 'FAIL', bad + 1
        lo_tr = '/'.join(x for x in tr if x) or 'none'
        print(f'{flag} slide {i:2}: transition {name:<9} -> LO {lo_tr:<26} effects authored {n_auth:2} '
              f'(entr {cen["entr"]}, emph {cen["emph"]}, exit {cen["exit"]}, path {cen["path"]}, letters {cen["iterate"]}, '
              f'media {cen["media"]}) -> imported {n_imp:2} {classes} paths {mot} iterate {it}')
    print('RESULT:', 'FAIL' if bad else 'PASS', '(LibreOffice parsed the animation XML; PowerPoint playback is not proven by this)')
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
