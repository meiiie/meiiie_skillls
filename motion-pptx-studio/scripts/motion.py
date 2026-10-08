"""Add Morph transitions (p159) and staggered entrance animations.

Objects named '!!x' morph across slides. Objects named '@<fade|float|wipe><order>-x'
get entrances.

Usage:
  python motion.py UNPACKED_DIR [--dur 12=2000,22=1800]

UNPACKED_DIR is the unpacked deck (it contains ppt/slides). --dur values are
milliseconds keyed by slide FILE number (slideN.xml). They override DUR.
Slide files numbered <= OPENING_SLIDE_MAX default to OPENING_DUR_MS; every
other slide defaults to DEFAULT_DUR_MS.
"""
import argparse
import re
from pathlib import Path

from lxml import etree

# Optional built-in durations (slide file number -> ms). Prefer --dur so a
# deck's timings stay out of this file. Keys passed with --dur win.
DUR = {}

OPENING_SLIDE_MAX = 4
OPENING_DUR_MS = 1500
DEFAULT_DUR_MS = 1300

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
}
P = '{%s}' % NS['p']
TRANS = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
    '<p:transition xmlns:p="%s" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}"><p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition xmlns:p="%s" spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
) % (NS['p'], NS['p'])


def parse_dur(text):
    durations = {}
    if not text:
        return durations
    for part in text.split(','):
        if not part.strip():
            continue
        key, value = part.split('=', 1)
        slide = int(key.strip())
        ms = int(value.strip())
        if slide < 1 or ms < 1:
            raise ValueError('duration entries must be positive: ' + part)
        durations[slide] = ms
    return durations


def duration_for(num, durations):
    if num in durations:
        return durations[num]
    return OPENING_DUR_MS if num <= OPENING_SLIDE_MAX else DEFAULT_DUR_MS


def eff(kind, spid, delay, ids, txt):
    n = lambda: str(next(ids))
    tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
    vis = f'<p:set><p:cBhvr><p:cTn id="{n()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>{tgt}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
    grp = ' grpId="0"' if txt else ''
    if kind == 'fade':
        pid, sub, inner = 10, 0, f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{n()}" dur="800"/>{tgt}</p:cBhvr></p:animEffect>'
    elif kind == 'wipe':
        pid, sub, inner = 22, 8, f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{n()}" dur="700"/>{tgt}</p:cBhvr></p:animEffect>'
    else:  # float in (up)
        def anim(attr, a, b):
            return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{n()}" dur="1000" fill="hold"/>{tgt}'
                    f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                    f'<p:tav tm="0"><p:val><p:strVal val="{a}"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="{b}"/></p:val></p:tav></p:tavLst></p:anim>')
        pid, sub = 42, 0
        inner = (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{n()}" dur="1000"/>{tgt}</p:cBhvr></p:animEffect>'
                 + anim('ppt_x', '#ppt_x', '#ppt_x') + anim('ppt_y', '#ppt_y+.06', '#ppt_y'))
    head_id = n()
    return (f'<p:par><p:cTn id="{head_id}" presetID="{pid}" presetClass="entr" presetSubtype="{sub}" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>{vis}{inner}</p:childTnLst></p:cTn></p:par>')


def apply(unpacked, durations):
    slides = Path(unpacked) / 'ppt' / 'slides'
    if not slides.is_dir():
        raise SystemExit('no slides directory: ' + str(slides))
    report = []
    for f in sorted(slides.glob('slide*.xml'), key=lambda p: int(re.findall(r'\d+', p.name)[0])):
        num = int(re.findall(r'\d+', f.name)[0])
        x = f.read_text()
        tree = etree.fromstring(x.encode())
        anims, morphs = [], []
        for c in tree.iter(P + 'cNvPr'):
            name = c.get('name')
            m = re.match(r'@(fade|float|wipe)(\d+)-', name)
            if m:
                sp = c.getparent().getparent()
                anims.append((int(m.group(2)), m.group(1), c.get('id'), sp.tag == P + 'sp' and sp.find('p:txBody', NS) is not None))
            elif name.startswith('!!'):
                morphs.append(name)
        anims.sort(key=lambda a: a[0])
        ids = iter(range(3, 10000))
        pars = []
        base = 350 if num > 1 else 500
        for order, kind, spid, txt in anims:
            pars.append(eff(kind, spid, base + (order - 1) * 220, ids, txt))
        timing = ''
        if pars:
            bld = ''.join(f'<p:bldP spid="{s}" grpId="0"/>' for _, _, s, t in anims if t)
            timing = ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
              '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
              f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
              f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
              + ''.join(pars).replace('nodeType="withEffect"', 'nodeType="afterEffect"', 1) +
              '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
              '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
              '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
              '</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')
        dur = duration_for(num, durations)
        ins = TRANS.replace('{dur}', str(dur)) + timing
        # drop earlier Morph wrappers (mc:AlternateContent) first so re-runs never stack transitions
        x = re.sub(r'<mc:AlternateContent[^>]*>\s*<mc:Choice[^>]*Requires="p159".*?</mc:AlternateContent>', '', x, flags=re.S)
        x = re.sub(r'<p:transition.*?</p:transition>|<p:timing>.*?</p:timing>', '', x, flags=re.S)
        if '</p:clrMapOvr>' in x:
            x = x.replace('</p:clrMapOvr>', '</p:clrMapOvr>' + ins, 1)
        else:
            x = x.replace('</p:cSld>', '</p:cSld>' + ins, 1)
        f.write_text(x)
        report.append(f'slide{num}: morph {dur}ms, {len(anims)} entrances, morph objs {sorted(set(morphs))}')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='Add one Morph transition per slide, with fallback fade and named entrances.')
    parser.add_argument('unpacked', help='unpacked deck directory (contains ppt/slides)')
    parser.add_argument('--dur', default='', help='comma-separated FILE=ms overrides, e.g. 12=2000,22=1800')
    args = parser.parse_args(argv)
    try:
        durations = dict(DUR)
        durations.update(parse_dur(args.dur))
    except ValueError as error:
        raise SystemExit(str(error))
    print('\n'.join(apply(args.unpacked, durations)))


if __name__ == '__main__':
    main()
