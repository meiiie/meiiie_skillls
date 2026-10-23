#!/usr/bin/env python3
"""v6.18 keyframe + purpose gate. Every component on a slide gets its own classic animation (entrance, path,
emphasis, exit, timed in sequence) that plays in every PowerPoint; Morph is never required.
  python3 anim_check.py DECK.pptx [--deck deck.json]
Fails: a content slide where < 70 % of its foreground components (text, picture, film, group; not the
background/full-slide ground) carry a classic effect; any p159 Morph that has no classic effect fallback on
its slide; with --deck: a slide without a one-line "purpose" (design/story.md through-line)."""
import sys, json, argparse
from pptx import Presentation
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
ap = argparse.ArgumentParser(); ap.add_argument('pptx'); ap.add_argument('--deck'); a = ap.parse_args()
pr = Presentation(a.pptx); W, H = pr.slide_width, pr.slide_height; fails, low = [], []
for k, s in enumerate(pr.slides):
    ids = {str(e.get('spid')) for e in s._element.iter(P + 'spTgt')}
    comp = [sh for sh in s.shapes if not (sh.width and sh.height and sh.width * sh.height >= .9 * W * H and sh.shape_type != 16)
            and not (sh.has_text_frame and not sh.text_frame.text.strip() and sh.shape_type not in (13, 16, 6))]
    if len(comp) < 2: continue
    share = sum(str(sh.shape_id) in ids for sh in comp) / len(comp)
    if share < .7: low.append((k + 1, round(share * 100)))
    xml = s._element.xml
    if 'p159:morph' in xml and not ids: fails.append(f'MORPH   slide {k+1}: Morph with no classic effects - it will not play in PowerPoint 2016/LibreOffice')
if len(low) > max(1, len(pr.slides) // 10):
    fails.append(f'KEYFRAME {len(low)} slides animate < 70 % of their components {low}: give each component its own entrance/path/emphasis, in sequence (native-keyframes)')
if a.deck:
    sl = [x for x in json.load(open(a.deck)).get('slides', []) if not x.get('hidden')]
    miss = [i + 1 for i, x in enumerate(sl) if len(str(x.get('purpose', '')).strip()) < 8]
    if miss: fails.append(f'PURPOSE slides {miss} have no one-line "purpose" in deck.json (through-line): cut them or state what they do')
print('\n'.join('FAIL    ' + f for f in fails) or f'anim_check: ok ({len(low)} slides below 70 %)'); sys.exit(1 if fails else 0)
