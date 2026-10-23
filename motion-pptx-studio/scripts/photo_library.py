#!/usr/bin/env python3
"""v6.16 chapter photo library: assemble BEFORE writing slides; slides are written from it.

  library/library.json = {"chapters": {"CH": [{"file": "library/CH/x.jpg", "url": "...", "licence": "CC BY 4.0",
        "author": "...", "subject": "what it physically shows", "job": "hero|detail|wide|sequence|texture|candidate"}]}}
  python3 photo_library.py board library/library.json      -> library/board-CH.jpg per chapter (caption = job · licence)
  python3 photo_library.py check library/library.json [--deck deck.json --pptx deck.pptx]
Check: per chapter >= 8 candidates, all real photographs (art_check.real_photo), licence + url on each,
picks with >= 3 different jobs incl. a hero; with --pptx: >= 2 library picks used per chapter, a photo on
<= 2 slides, a non-photo picture (drawing/diagram) on <= 2 slides (one drawing repeated 10x = a template)."""
import sys, json, argparse, io, hashlib
import numpy as np, re
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent)); from art_check import real_photo

def load(p):
    return json.load(open(p))['chapters']

def board(a):
    root = Path(a.lib).parent
    for ch, items in load(a.lib).items():
        T = 360; n = len(items); cols = 5; rows = (n + cols - 1) // cols
        b = Image.new('RGB', (cols * T, rows * (T * 9 // 16 + 28) + 30), 'white'); d = ImageDraw.Draw(b)
        d.text((6, 8), f'{ch}: {n} candidates', fill='black')
        for i, it in enumerate(items):
            x, y = i % cols * T, 30 + i // cols * (T * 9 // 16 + 28)
            try:
                im = Image.open(root.parent / it['file'] if not Path(it['file']).exists() else it['file']).convert('RGB')
                im.thumbnail((T - 6, T * 9 // 16)); b.paste(im, (x + 3, y))
            except Exception:
                d.text((x + 8, y + 40), 'missing ' + it.get('file', ''), fill='red')
            d.text((x + 4, y + T * 9 // 16 + 4), f"{i+1} {it.get('job','candidate')} · {it.get('licence','?')[:18]}", fill='black')
        out = Path(a.lib).with_name(f'board-{ch}.jpg'); b.save(out, quality=82); print('board', out)

def _hash(f):
    g = np.asarray(Image.open(f).convert('L').resize((17, 16)), float); return (g[:, 1:] > g[:, :-1]).flatten()

def _hist(f):
    h = np.asarray(Image.open(f).convert('RGB').resize((64, 36)).quantize(64, method=Image.Quantize.FASTOCTREE).convert('RGB').resize((8, 8)), float).flatten()
    return h / (np.linalg.norm(h) + 1e-9)

def variety(ch, items):
    """v6.17: a library of 8 server rooms is one subject. Need >= 4 distinct 'subject' strings (first 3 words) and
    <= 1/3 of candidate pairs looking alike (dhash dist < .30 or colour-layout cosine > .97)."""
    STOP = {'file', 'with', 'from', 'jpg', 'jpeg', 'png', 'the', 'and', 'photo', 'view', 'image', 'front', 'back', 'close'}
    toks = []
    for it in items:
        t = re.sub(r'\.(jpe?g|png|tiff?)$', '', str(it.get('subject') or it.get('file', '')).lower().replace('file:', ''))
        toks.append({w[:5] for w in re.findall(r'[^\W\d_]{4,}', t) if w not in STOP} | {'#' + t[:40]})
    par = list(range(len(toks)))
    def f(i):
        while par[i] != i: i = par[i]
        return i
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            if any(w[0] != '#' and len(w) == 5 and w in ' '.join(toks[j]) for w in toks[i]): par[f(i)] = f(j)
    subj = {f(i) for i in range(len(toks))}
    out = []
    if len(subj) < 4: out.append(f'VARIETY chapter {ch!r}: {len(subj)} distinct subjects (need >= 4: place, object, people, detail...)')
    H = []
    for it in items:
        try: H.append((_hash(it['file']), _hist(it['file'])))
        except Exception: pass
    pairs = [(i, j) for i in range(len(H)) for j in range(i + 1, len(H))]
    alike = sum(1 for i, j in pairs if (H[i][0] != H[j][0]).mean() < .30 or float(H[i][1] @ H[j][1]) > .97)
    if pairs and alike > len(pairs) / 3:
        out.append(f'VARIETY chapter {ch!r}: {alike}/{len(pairs)} candidate pairs look alike (max 1/3): replace near-duplicates with other subjects')
    return out

def check(a):
    fails, lib = [], load(a.lib); picks = {}
    for ch, items in lib.items():
        if len(items) < 8: fails.append(f'LIB     chapter {ch!r}: {len(items)} candidates (need >= 8)')
        jobs = {it.get('job') for it in items if it.get('job', 'candidate') != 'candidate'}
        if 'hero' not in jobs or len(jobs) < 3: fails.append(f'LIB     chapter {ch!r}: picks have jobs {sorted(jobs)} (need a hero + 3 different jobs)')
        for it in items:
            if not it.get('licence') or not it.get('url'): fails.append(f"LIB     {it.get('file')}: licence/url missing")
            try:
                if not real_photo(Image.open(it['file'])): fails.append(f"LIB     {it['file']}: not a real photograph (render/illustration)")
            except Exception: fails.append(f"LIB     {it.get('file')}: cannot open")
            if it.get('job', 'candidate') != 'candidate': picks[Path(it['file']).stem.lower()] = ch
        for w in variety(ch, items): print('WARN    ' + w)   # v6.18: warn; the critic judges variety
    if a.pptx:
        from pptx import Presentation
        used, nonphoto, per_ch = {}, {}, {}
        for k, s in enumerate(Presentation(a.pptx).slides):
            R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'; blobs = {}
            for bl in s._element.xpath('.//a:blip'):
                try: bb = s.part.related_part(bl.get(R)).blob; blobs[hashlib.md5(bb).hexdigest()] = (bb, bool(bl.xpath('ancestor::p:bg')))
                except Exception: pass
            for h, (blob, bg) in blobs.items():
                try: im = Image.open(io.BytesIO(blob))
                except Exception: continue
                if real_photo(im): used.setdefault(h, set()).add(k + 1)
                elif not bg and im.size[0] * im.size[1] < 1.5e6: nonphoto.setdefault(h, set()).add(k + 1)   # grounds/materials exempt
        if a.deck:
            sl = [x for x in json.load(open(a.deck)).get('slides', []) if not x.get('hidden')]
            for k, x in enumerate(sl):
                t = json.dumps(x).lower()
                for st, ch in picks.items():
                    if st in t: per_ch.setdefault(ch, set()).add(k + 1)
        n = len(Presentation(a.pptx).slides); ph = {k for v in used.values() for k in v}
        if len(ph) < n / 2: fails.append(f'IMAGE   only {len(ph)}/{n} slides carry a real photo: image-led means most slides start from a library pick')
        for d, kind in ((used, 'photo'), (nonphoto, 'drawing')):
            for h, sl in d.items():
                if len(sl) > 2: fails.append(f'REUSE   one {kind} on {len(sl)} slides {sorted(sl)} (max 2): pick another from the library')
        for ch in (lib if a.deck else []):
            if len(per_ch.get(ch, ())) < 2: fails.append(f'LIB     chapter {ch!r}: {len(per_ch.get(ch, ()))} slides use its library picks (need >= 2): write slides FROM the library')
    print('\n'.join('FAIL    ' + f for f in fails) or 'photo_library: ok'); sys.exit(1 if fails else 0)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sp = ap.add_subparsers(dest='cmd', required=True)
b = sp.add_parser('board'); b.add_argument('lib'); b.set_defaults(f=board)
c = sp.add_parser('check'); c.add_argument('lib'); c.add_argument('--deck'); c.add_argument('--pptx'); c.set_defaults(f=check)
a = ap.parse_args(); a.f(a)
