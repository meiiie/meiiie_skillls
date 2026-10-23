#!/usr/bin/env python3
"""v6.21 unity + layout rhythm gate (principles/unity.md, layout-rhythm.md).
  python3 style_check.py renders/rN --pptx DECK.pptx --deck deck.json
Needs design/style.json {"palette": ["#hex", ... 4-7], "treatment": "one line: grade, grain, crop, edge"} written
BEFORE building. Fails:
- STYLE   no design/style.json, or a palette outside 4-7 colours;
- PALETTE a slide without a real photo (renders, diagrams, type) whose non-neutral pixels are < 75 % within
          distance 70 of the palette (a render or chart in another world);
- TREAT   > 15 % of slides whose mean saturation/lightness sit > 3 MAD from the deck (an ungraded photo, a stray look);
- LAYOUT  deck.json slides need "layout"; one layout on > 3 slides; a run of 4 slides without a full-bleed,
          detail-crop or type-on-photo slide."""
import sys, glob, json, argparse, io
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent)); from art_check import real_photo
ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--pptx'); ap.add_argument('--deck'); a = ap.parse_args()
fails = []; deck = Path(a.deck) if a.deck else None
def _root(d):   # v6.22: style.json is found from the project root (design/ or samples/ holder), not only beside deck.json
    for p in [d.parent, *list(d.parents)[1:4]]:
        if (p / 'design').is_dir() or (p / 'samples').is_dir(): return p
    return d.parent
_r = _root(deck.resolve()) if deck else None
sj = sorted((p for p in (_r.glob('**/style.json') if _r else []) if '.agents' not in str(p)),
            key=lambda p: (p.parent.name != 'design', 'samples' in p.parts and 'samples' not in deck.resolve().parts, len(p.parts)))
pal = []
if not sj: fails.append('STYLE   no design/style.json (palette + treatment locked before building)')
else:
    st = json.load(open(sj[0])); pal = [tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) for h in st.get('palette', [])]
    if not 4 <= len(pal) <= 7: fails.append(f'STYLE   palette has {len(pal)} colours (need 4-7)')
renders = sorted(glob.glob(f'{a.dir}/slide-*.jpg') + glob.glob(f'{a.dir}/slide-*.png'))
photo = set()
if a.pptx:
    from pptx import Presentation
    R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
    for k, s in enumerate(Presentation(a.pptx).slides):
        for bl in s._element.xpath('.//a:blip'):
            try:
                if real_photo(Image.open(io.BytesIO(s.part.related_part(bl.get(R)).blob))): photo.add(k); break
            except Exception: pass
stats, offp = [], []
P = np.array(pal, float) if pal else None
for k, f in enumerate(renders):
    im = Image.open(f).convert('RGB').resize((160, 90)); x = np.asarray(im, float).reshape(-1, 3)
    mx, mn = x.max(1), x.min(1); sat = (mx - mn) / (mx + 1e-6); stats.append((sat.mean(), x.mean() / 255))
    if P is not None and k not in photo:
        c = x[(mx - mn) > 30]   # neutrals (paper, black, grey) are free
        if len(c) > 200 and (np.sqrt(((c[:, None] - P[None]) ** 2).sum(2)).min(1) < 70).mean() < .75: offp.append(k + 1)
if offp: fails.append(f'PALETTE slides {offp}: renders/diagrams/type off the locked palette - redraw them in style.json colours')
S = np.array(stats); out = []
if len(S) > 5:
    for j in range(2):
        med = np.median(S[:, j]); mad = np.median(np.abs(S[:, j] - med)) + 1e-3
        out += list(np.where(np.abs(S[:, j] - med) > 3 * mad * 1.4826)[0] + 1)
    out = sorted(set(out))
    if len(out) > .15 * len(S): fails.append(f'TREAT   {len(out)} slides off the deck treatment {out}: grade photos/renders with the one treatment')
if deck:
    sl = [x for x in json.load(open(deck)).get('slides', []) if not x.get('hidden')]
    L = [str(x.get('layout', '')).lower() for x in sl]
    if not all(L): fails.append(f'LAYOUT  slides {[i + 1 for i, l in enumerate(L) if not l]} have no "layout" (layout-rhythm)')
    from collections import Counter
    many = {l: c for l, c in Counter(L).items() if l and c > 3 and l not in ('sources', 'title')}
    if many: fails.append(f'LAYOUT  layouts used > 3 times {many}: vary (layout-rhythm)')
    strong = {'full-bleed', 'detail-crop', 'type-on-photo', 'film'}
    for i in (range(len(L) - 3) if all(L) else []):
        if not strong & set(L[i:i + 4]): fails.append(f'RHYTHM  slides {i + 1}-{i + 4} have no full-bleed / detail-crop / type-on-photo / film'); break
    # v6.22 CHART rhythm: a chapter whose slides state >= 3 quantities needs >= 1 real chart (layout "chart",
    # a "bars" component, or a chart/plot image) - big numerals alone do not show a comparison.
    import re as _re
    num = _re.compile(r'\d[\d.,]*\s?(%|tỷ|triệu|nghìn|km|kg|tấn|ha|°|usd|\$|vnđ|đồng|lần|năm)', _re.I)
    chs = {}
    for x in sl: chs.setdefault(str(x.get('chapter', '')), []).append(x)
    for c, xs in chs.items():
        if not c or _re.match(r'(?i)^(nguồn|sources?|credits?|tài liệu|tham khảo)', c): continue
        t = json.dumps(xs, ensure_ascii=False)
        has = any(str(x.get('layout', '')).lower() == 'chart' for x in xs) or _re.search(r'"type":\s*"bars"|chart|plot|graph', t, _re.I)
        if len(num.findall(t)) >= 3 and not has:
            fails.append(f'CHART   chapter {c!r} states {len(num.findall(t))} quantities but has no real chart (layout "chart" / bars / plotted image)')
print('\n'.join('FAIL    ' + f for f in fails) or 'style_check: ok'); sys.exit(1 if fails else 0)
