"""One transition per slide (Morph by default, or any native transition) plus named animations.

v5: the slide can use any of ~48 native transitions (push, curtains, origami, vortex, zoom ...) and
shapes can carry entrance, emphasis, exit, motion-path, letter-by-letter, trigger and video effects.
The XML comes from motionlib.py; this script decides WHAT goes on each slide.

Naming contract (set the shape name in the selection pane or cNvPr/@name):
  !!name              persistent layer. The same name on neighbouring slides = Morph pairs it.
  @fade<N>-label      fade in, N = order on the slide (1, 2, 3 ...)
  @float<N>-label     float up + fade in
  @wipe<N>[l|r|t|b]-  wipe from the left (or the side given)
  @fly<N>[l|r|t|b]-   fly in from the bottom (or the side given)
  @zoom<N>-label      zoom in from the centre        @split<N>[h|v]-   split out
  @type<N>-label      text appears letter by letter  @word<N>-label    text fades in word by word
  @rise<N>-  @drop<N>-  @wheel<N>-  @appear<N>-
  @blink<N>-label     endless blink                  @pulse<N>- / @spin<N>-  endless pulse / spin
  Anything richer (paths, orbits, delays, clicks, triggers, exits, several effects on one shape,
  effects on !! shapes) goes in motion.json "effects", which build_deck.py writes from "anim" keys.

Usage:
  python motion.py UNPACKED_DIR [--config motion.json] [--dur 12=2000,22=1800]
                   [--keep-timing 50,51] [--default-ms 1300] [--stagger 220] [--dry-run]

motion.json (keys are slide FILE numbers, slideN.xml -> "N"):
  {"default_ms": 1300, "stagger_ms": 220,
   "dur": {"12": 2000}, "option": {"7": "byChar"}, "keep_timing": [50],
   "transition": {"5": {"type": "curtains", "ms": 1600}, "9": "push"},
   "effects": {"3": [{"shape": "!!dot", "fx": "path", "path": [[0, 0], [2.5, -0.8]], "ms": 1800, "delay": 400},
                     {"shape": "Tiêu đề", "fx": "type", "click": 1}]},
   "media": {"4": {"!!bg-video": {"loop": true, "mute": true, "autoplay": true}}}}
Durations, options and transitions: command line > motion.json > style default (Morph 1300 ms).
Embedded videos (p:pic with a:videoFile) always get autoplay + loop + mute unless media says otherwise.

Re-runs are safe: every earlier transition is removed first, so a slide always ends with exactly
one transition. p:timing is rebuilt from names and effects, EXCEPT on slides listed in keep_timing.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compat  # noqa: E402
import motionlib  # noqa: E402

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
P = '{%s}' % NS['p']
A = '{%s}' % NS['a']
MC = '{%s}' % NS['mc']
DEFAULT_MS = 1300
STAGGER_MS = 220
SHAPE_TAGS = {'sp', 'pic', 'grpSp', 'cxnSp', 'graphicFrame'}


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
                'option': {int(k): str(v) for k, v in cfg.get('option', {}).items()},
                'keep_timing': {int(x) for x in cfg.get('keep_timing', [])},
                'stagger': int(cfg.get('stagger_ms', STAGGER_MS)),
                'transition': {int(k): v for k, v in cfg.get('transition', {}).items()},
                'effects': {int(k): v for k, v in cfg.get('effects', {}).items()},
                'media': {int(k): v for k, v in cfg.get('media', {}).items()},
                'compat': compat.check_mode(cfg.get('compat')),
                'safe_transition': cfg.get('safe_transition'),
                'source': str(c),
            }
        if path:
            raise SystemExit('config not found: ' + str(c))
    return {'default_ms': DEFAULT_MS, 'dur': {}, 'option': {}, 'keep_timing': set(), 'stagger': STAGGER_MS,
            'transition': {}, 'effects': {}, 'media': {}, 'compat': 'morph', 'safe_transition': None, 'source': None}


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


def insert_after(root, new_elems):
    """Place elements after cSld/clrMapOvr (schema order: cSld, clrMapOvr, transition, timing, extLst)."""
    anchor = root.find(P + 'clrMapOvr')
    if anchor is None:
        anchor = root.find(P + 'cSld')
    idx = list(root).index(anchor) + 1
    for el in new_elems:
        root.insert(idx, el)
        idx += 1


def top_level(root):
    """{name: (spid, element)} for the slide's top-level shapes (PowerPoint animates only those)."""
    tree = root.find('p:cSld/p:spTree', NS)
    out = {}
    for el in tree:
        if etree.QName(el).localname not in SHAPE_TAGS:
            continue
        c = el.find('.//p:cNvPr', NS)
        if c is not None:
            out.setdefault(c.get('name') or '', (c.get('id'), el))
    return out


def is_text(el):
    return etree.QName(el).localname == 'sp' and el.find('p:txBody', NS) is not None and ''.join(el.find('p:txBody', NS).itertext()).strip() != ''


def plan_slide(root, num, cfg, warnings):
    tops = top_level(root)
    effects, texts = [], set()
    order_items = []
    nested = []
    for c in root.iter(P + 'cNvPr'):
        name = c.get('name') or ''
        e = motionlib.effect_from_name(name, cfg['stagger'])
        if name.startswith('@') and not e:
            warnings.append(f'slide{num}: "{name}" starts with @ but is not a known effect name '
                            f'(@fade|float|wipe|fly|zoom|split|type|word|rise|drop|wheel|appear|blink|pulse|spin<N>-label)')
            continue
        if not e:
            continue
        if name not in tops or tops[name][0] != c.get('id'):
            nested.append(name)
            continue
        order_items.append((e, tops[name]))
    if nested:
        warnings.append(f'slide{num}: animated names inside a group are ignored (PowerPoint animates only top-level shapes): {nested}')
    base = 500 if num == 1 else 350
    for e, (spid, el) in order_items:
        e['delay'] = base + (e.pop('order') - 1) * cfg['stagger']
        effects.append((e, spid))
        if is_text(el):
            texts.add(spid)
    for e in cfg['effects'].get(num, []):
        e = dict(e)
        nm = e.pop('shape', None)
        if nm not in tops:
            warnings.append(f'slide{num}: effect for {nm!r}: no top-level shape with that name (in a group? renamed?)')
            continue
        spid, el = tops[nm]
        if e.get('trigger'):
            if e['trigger'] not in tops:
                warnings.append(f'slide{num}: trigger {e["trigger"]!r} not found')
                continue
            e['trigger_spid'] = tops[e['trigger']][0]
        if 'delay' not in e:
            e['delay'] = base + (int(e.pop('order', 1)) - 1) * cfg['stagger']
        else:
            e.pop('order', None)
        effects.append((e, spid))
        if is_text(el):
            texts.add(spid)
    media = []
    mcfg = cfg['media'].get(num, {})
    for nm, (spid, el) in tops.items():
        if etree.QName(el).localname == 'pic' and el.find('.//a:videoFile', NS) is not None:
            m = {'spid': spid, 'loop': True, 'mute': True, 'autoplay': True, 'ms': 10000}
            m.update(mcfg.get(nm, {}))
            media.append(m)
    return effects, media, texts


def apply(unpacked, cfg, dry=False):
    slides = Path(unpacked) / 'ppt' / 'slides'
    if not slides.is_dir():
        raise SystemExit('no slides directory: ' + str(slides))
    report, warnings = [], []
    files = sorted(slides.glob('slide*.xml'), key=file_num)
    mode = cfg.get('compat', 'morph')
    geo = {file_num(f): compat.shapes(etree.parse(str(f)).getroot()) for f in files} if mode != 'morph' else {}
    nums = [file_num(f) for f in files]
    rebuilt = 0
    for f in files:
        num = file_num(f)
        tree = etree.parse(str(f))
        root = tree.getroot()
        morphs = [c.get('name') for c in root.iter(P + 'cNvPr') if (c.get('name') or '').startswith('!!')]
        dups = sorted({n for n in morphs if morphs.count(n) > 1})
        if dups:
            warnings.append(f'slide{num}: duplicate !! names on one slide {dups} (Morph cannot pair them reliably)')
        strip_transitions(root)
        keep = num in cfg['keep_timing']
        old_timing = root.find(P + 'timing')
        if old_timing is not None:
            root.remove(old_timing)
        tspec = cfg['transition'].get(num, 'morph')
        if isinstance(tspec, str):
            tspec = {'type': tspec}
        tspec = dict(tspec)
        slide_cfg = cfg
        if mode != 'morph' and tspec.get('type', 'morph') == 'morph':
            # no-Morph safe mode: rebuild this Morph as a classic transition + effects (compat.py)
            i = nums.index(num)
            prev = geo[nums[i - 1]] if i else {}
            # shapes whose authored effects already enter or travel keep them; emphasis-only shapes still get a path
            taken = {e.get('shape') for e in cfg['effects'].get(num, [])
                     if motionlib.PRESETS.get(e.get('fx', 'fade'), ('entr',))[0] in ('entr', 'path')}
            ms = int(tspec.get('ms', cfg['dur'].get(num, cfg['default_ms'])))
            opt = tspec.get('option', cfg['option'].get(num, 'byObject'))
            try:
                tspec, extra = compat.plan(prev, geo[num], mode, ms, opt, taken, cfg.get('safe_transition'))
            except ValueError as e:
                raise SystemExit(f'slide{num}: {e}')
            if not prev:
                extra = []
            if extra and not keep:
                slide_cfg = dict(cfg, effects=dict(cfg['effects']))
                slide_cfg['effects'][num] = list(cfg['effects'].get(num, [])) + [
                    {k: v for k, v in e.items() if k != '_why'} for e in extra]
                rebuilt += len(extra)
        effects, media, texts = plan_slide(root, num, slide_cfg, warnings)
        if keep:
            timing_el = old_timing
        else:
            xml = motionlib.build_timing(effects, media, texts)
            timing_el = etree.fromstring(xml) if xml else None
        # an explicit "ms" on the slide's transition wins; then dur (deck "ms" / --dur); then default_ms
        tspec.setdefault('ms', cfg['dur'].get(num, cfg['default_ms']))
        if tspec.get('type', 'morph') == 'morph':
            tspec.setdefault('option', cfg['option'].get(num, 'byObject'))
        try:
            trans = etree.fromstring(motionlib.transition_xml(tspec, cfg['default_ms']))
        except ValueError as e:
            raise SystemExit(f'slide{num}: {e}')
        new = [trans]
        if timing_el is not None:
            new.append(timing_el)
        insert_after(root, new)
        if not dry:
            tree.write(str(f), xml_declaration=True, encoding='UTF-8', standalone=True)
        kinds = ','.join(sorted({e.get('fx', '?') for e, _ in effects}))
        tname = tspec.get('type', 'morph')
        extra = f' {tspec["option"]}' if tname == 'morph' and tspec.get('option', 'byObject') != 'byObject' else ''
        report.append(f'slide{num}: {tname} {tspec["ms"]}ms{extra}, {len(effects)} effects [{kinds}]'
                      + (f', {len(media)} video' if media else '') + (' timing KEPT' if keep else '')
                      + f', !! {sorted(set(morphs))}')
    if mode != 'morph':
        report.append(f'compat={mode}: {rebuilt} classic effect(s) synthesized from Morph pairs')
    return report, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description='One transition per slide + named animations (v5).')
    ap.add_argument('unpacked', help='unpacked deck directory (contains ppt/slides)')
    ap.add_argument('--config', help='motion.json (default: UNPACKED/, its parent, or grandparent = WORK/motion.json)')
    ap.add_argument('--dur', default='', help='FILE=ms overrides, e.g. 12=2000,22=1800')
    ap.add_argument('--keep-timing', default='', help='slide FILE numbers whose existing p:timing is preserved')
    ap.add_argument('--default-ms', type=int, help='default transition duration')
    ap.add_argument('--stagger', type=int, help='ms between entrance orders')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--list', action='store_true', help='print the transition and effect names, then exit')
    a = ap.parse_args(argv)
    if a.list:
        print('transitions:', ', '.join(motionlib.transition_names()))
        print('effects:', ', '.join(sorted(motionlib.PRESETS)))
        return
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
