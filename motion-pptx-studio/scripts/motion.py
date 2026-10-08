"""Add one Morph transition per slide plus named entrance / blink animations.

Naming contract (set the shape name in the selection pane or cNvPr/@name):
  !!name              persistent layer. The same name on neighbouring slides = Morph pairs it.
  @fade<N>-label      fade in, N = order on the slide (1, 2, 3 ...)
  @float<N>-label     float up + fade in
  @wipe<N>-label      wipe from the left (good for rules / lines / underlines)
  @blink<N>-label     endless blink (cursor, signal light) starting in order N
  A shape can be both persistent and animated only through a group: put the @shape
  inside a group named !!x, or keep them separate shapes.

Usage:
  python motion.py UNPACKED_DIR [--config motion.json] [--dur 12=2000,22=1800]
                   [--keep-timing 50,51] [--default-ms 1300] [--stagger 220] [--dry-run]

UNPACKED_DIR is the unpacked deck (contains ppt/slides). Durations and kept timings
are keyed by slide FILE number (slideN.xml), never by deck position, so they survive
re-ordering. If --config is not given, motion.json is looked up in UNPACKED_DIR and
its parent folder. Command-line values win over the config file.

motion.json example:
  {"default_ms": 1300, "dur": {"12": 2000, "22": 2000}, "keep_timing": [50]}

Re-runs are safe: every earlier transition (Morph wrapper or plain) is removed first,
so a slide always ends with exactly one transition. p:timing is rebuilt from names,
EXCEPT on slides listed in keep_timing, whose hand-made timing is preserved.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from lxml import etree

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
P = '{%s}' % NS['p']
MC = '{%s}' % NS['mc']
DEFAULT_MS = 1300
STAGGER_MS = 220
TRANS = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
    '<p:transition xmlns:p="%s" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}"><p159:morph option="byObject"/></p:transition></mc:Choice>'
    '<mc:Fallback><p:transition xmlns:p="%s" spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
) % (NS['p'], NS['p'])
ANIM_RE = re.compile(r'@(fade|float|wipe|blink)(\d+)-')


def file_num(path):
    return int(re.findall(r'\d+', Path(path).name)[0])


def parse_dur(text):
    out = {}
    for part in (text or '').split(','):
        if not part.strip():
            continue
        key, value = part.split('=', 1)
        slide, ms = int(key), int(value)
        if slide < 1 or ms < 1:
            raise ValueError('duration entries must be positive: ' + part)
        out[slide] = ms
    return out


def parse_list(text):
    return {int(x) for x in (text or '').split(',') if x.strip()}


def load_config(unpacked, path):
    up = Path(unpacked).resolve()
    cands = [Path(path)] if path else [up / 'motion.json', up.parent / 'motion.json', up.parent.parent / 'motion.json']
    for c in cands:
        if c.is_file():
            cfg = json.loads(c.read_text(encoding='utf-8'))
            return {
                'default_ms': int(cfg.get('default_ms', DEFAULT_MS)),
                'dur': {int(k): int(v) for k, v in cfg.get('dur', {}).items()},
                'keep_timing': {int(x) for x in cfg.get('keep_timing', [])},
                'stagger': int(cfg.get('stagger_ms', STAGGER_MS)),
                'source': str(c),
            }
        if path:
            raise SystemExit('config not found: ' + str(c))
    return {'default_ms': DEFAULT_MS, 'dur': {}, 'keep_timing': set(), 'stagger': STAGGER_MS, 'source': None}


def eff(kind, spid, delay, ids, txt):
    n = lambda: str(next(ids))
    tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
    if kind == 'blink':
        # Emphasis "Blink" (preset 35), repeats forever.
        return (f'<p:par><p:cTn id="{n()}" presetID="35" presetClass="emph" presetSubtype="0" repeatCount="indefinite" fill="hold" nodeType="withEffect">'
                f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
                f'<p:anim calcmode="discrete" valueType="str"><p:cBhvr override="childStyle"><p:cTn id="{n()}" dur="1000" fill="hold"/>{tgt}'
                '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                '<p:tavLst><p:tav tm="0"><p:val><p:strVal val="hidden"/></p:val></p:tav><p:tav tm="50000"><p:val><p:strVal val="visible"/></p:val></p:tav></p:tavLst></p:anim>'
                '</p:childTnLst></p:cTn></p:par>')
    vis = (f'<p:set><p:cBhvr><p:cTn id="{n()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>{tgt}'
           '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')
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
    head = n()
    return (f'<p:par><p:cTn id="{head}" presetID="{pid}" presetClass="entr" presetSubtype="{sub}" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>{vis}{inner}</p:childTnLst></p:cTn></p:par>')


def strip_transitions(root):
    """Remove every p:transition and every mc:AlternateContent that wraps one."""
    removed = 0
    for ac in list(root.findall(MC + 'AlternateContent')):
        if ac.find('.//' + P + 'transition') is not None:
            root.remove(ac)
            removed += 1
    for tr in list(root.findall(P + 'transition')):
        root.remove(tr)
        removed += 1
    return removed


def build_timing(anims, num, stagger):
    ids = iter(range(3, 100000))
    base = 500 if num == 1 else 350
    pars = [eff(kind, spid, base + (order - 1) * stagger, ids, txt) for order, kind, spid, txt in anims]
    entr = [a for a in anims if a[1] != 'blink']
    bld = ''.join(f'<p:bldP spid="{s}" grpId="0"/>' for _, k, s, t in entr if t)
    return (f'<p:timing xmlns:p="{NS["p"]}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + ''.join(pars).replace('nodeType="withEffect"', 'nodeType="afterEffect"', 1) +
            '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            '</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')


def insert_after(root, new_elems):
    """Place elements after cSld/clrMapOvr (schema order: cSld, clrMapOvr, transition, timing, extLst)."""
    anchor = root.find(P + 'clrMapOvr')
    if anchor is None:
        anchor = root.find(P + 'cSld')
    idx = list(root).index(anchor) + 1
    for el in new_elems:
        root.insert(idx, el)
        idx += 1


def apply(unpacked, cfg, dry=False):
    slides = Path(unpacked) / 'ppt' / 'slides'
    if not slides.is_dir():
        raise SystemExit('no slides directory: ' + str(slides))
    report, warnings = [], []
    for f in sorted(slides.glob('slide*.xml'), key=file_num):
        num = file_num(f)
        tree = etree.parse(str(f))
        root = tree.getroot()
        anims, morphs = [], []
        for c in root.iter(P + 'cNvPr'):
            name = c.get('name') or ''
            m = ANIM_RE.match(name)
            if m:
                sp = c.getparent().getparent()
                has_text = sp.tag == P + 'sp' and sp.find('p:txBody', NS) is not None and ''.join(sp.itertext()).strip() != ''
                anims.append((int(m.group(2)), m.group(1), c.get('id'), has_text))
            elif name.startswith('@'):
                warnings.append(f'slide{num}: "{name}" starts with @ but does not match @fade|float|wipe|blink<N>-label')
            elif name.startswith('!!'):
                morphs.append(name)
        dups = sorted({n for n in morphs if morphs.count(n) > 1})
        if dups:
            warnings.append(f'slide{num}: duplicate !! names on one slide {dups} (Morph cannot pair them reliably)')
        anims.sort(key=lambda a: a[0])
        strip_transitions(root)
        keep = num in cfg['keep_timing']
        old_timing = root.find(P + 'timing')
        if keep:
            if old_timing is not None:
                root.remove(old_timing)  # re-inserted after the new transition
            timing_el = old_timing
        else:
            if old_timing is not None:
                root.remove(old_timing)
            timing_el = etree.fromstring(build_timing(anims, num, cfg['stagger'])) if anims else None
        dur = cfg['dur'].get(num, cfg['default_ms'])
        new = [etree.fromstring(TRANS.replace('{dur}', str(dur)))]
        if timing_el is not None:
            new.append(timing_el)
        insert_after(root, new)
        if not dry:
            tree.write(str(f), xml_declaration=True, encoding='UTF-8', standalone=True)
        kinds = ','.join(f'{k}{o}' for o, k, _, _ in anims)
        report.append(f'slide{num}: morph {dur}ms, anims [{kinds}]' + (' timing KEPT' if keep else '') + f', !! {sorted(set(morphs))}')
    return report, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description='One Morph transition per slide + named entrances/blink.')
    ap.add_argument('unpacked', help='unpacked deck directory (contains ppt/slides)')
    ap.add_argument('--config', help='motion.json (default: UNPACKED/, its parent, or grandparent = WORK/motion.json)')
    ap.add_argument('--dur', default='', help='FILE=ms overrides, e.g. 12=2000,22=1800')
    ap.add_argument('--keep-timing', default='', help='slide FILE numbers whose existing p:timing is preserved')
    ap.add_argument('--default-ms', type=int, help='default Morph duration')
    ap.add_argument('--stagger', type=int, help='ms between entrance orders')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(argv)
    try:
        cfg = load_config(a.unpacked, a.config)
        cfg['dur'].update(parse_dur(a.dur))
        cfg['keep_timing'] |= parse_list(a.keep_timing)
    except (ValueError, json.JSONDecodeError) as e:
        raise SystemExit(str(e))
    if a.default_ms:
        cfg['default_ms'] = a.default_ms
    if a.stagger:
        cfg['stagger'] = a.stagger
    report, warnings = apply(a.unpacked, cfg, a.dry_run)
    print('config:', cfg['source'] or '(none, defaults)')
    print('\n'.join(report))
    for w in warnings:
        print('WARNING', w, file=sys.stderr)


if __name__ == '__main__':
    main()
