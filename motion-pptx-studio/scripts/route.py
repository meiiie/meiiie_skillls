"""Route a deck to fitting art directions BEFORE any design (v5.5): analyse the subject, the audience, the
tone and the real asset material; score every candidate direction for fit; reject the mismatched ones with
a written reason; record the decision. Gate 3 fails without it, and fails a deck whose style was rejected.

  python3 route.py WORK                       analyse + score + write design/routing.json and design/routing.md
  python3 route.py WORK --choose blueprint --why "..."   record a different (non-rejected) choice and why
  python3 route.py WORK --print               show the last decision

What it reads (nothing is guessed from the file name of the style):
  brief.md       topic, audience, deliverable_kind, tone (optional line "- tone: ..."), style wishes,
                 forbidden items; the user's own words
  research/facts.md, assets/CREDITS.md       the subject's own vocabulary (what the facts and the pictures are of)
  assets/**      the material itself: luminance, saturation, warm/cool cast, archival (sepia/mono or a
                 pre-1970 date), cut-outs (transparent PNGs), how many real photos there are
  directions     design/directions.json (the three sketched directions) are scored too when they name a
                 "family" or carry "domains"/"tones" words; their palette is read as material

Candidates are the shipped packs (assets/styles, assets/styles-experimental), each with a "fit" block:
  {"domains": {"aerospace": 0.8, ...}, "tones": [...], "material": {"dark": 1, "cool": 0.5, ...},
   "avoid": [{"domain": "heritage", "reason": "..."}]}
A pack is a starting point, not the answer: the routed family is what the deck's own genome starts from
(references/design-space.md). Scores: domain 45 %, tone 20 %, material 35 %. A candidate is REJECTED when
an "avoid" domain is a leading domain of this deck (the reason is written out), or when its fit is < 0.40.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PACK_DIRS = [SKILL / 'assets' / 'styles', SKILL / 'assets' / 'styles-experimental']
IMG = ('.jpg', '.jpeg', '.png', '.webp')
REJECT_BELOW = 0.40

# subject lexicon (English + Vietnamese, accent-insensitive matching on whole words / stems)
DOMAINS = {
    'aerospace': r'rocket|launch|orbit\w*|booster|spacecraft|space ?x|nasa|falcon|starship|starlink|dragon capsule|raptor|merlin|'
                 r'satellite|aerospace|tên lửa|phóng|quỹ đạo|vũ trụ|tàu vũ trụ|vệ tinh|hàng không',
    'technology': r'technolog\w*|tech|engineering|hardware|reusab\w*|chip|ai\b|robot\w*|software|startup|ipo|'
                  r'công nghệ|kỹ thuật|tái sử dụng|phần mềm|khởi nghiệp',
    'engineering': r'engine\w*|mechanis\w*|propulsion|thrust|structure|landing legs?|grid fins?|động cơ|lực đẩy|cơ chế|kết cấu|chân đáp',
    'science': r'scien\w*|physics|research|experiment|khoa học|vật lý|nghiên cứu|thí nghiệm',
    'business': r'company|revenue|valuation|market|investor|profile|ipo|nasdaq|doanh thu|định giá|thị trường|công ty|nhà đầu tư|cổ phiếu',
    'heritage': r'heritage|di sản|di tích|lịch sử|history|historic\w*|truyền thống|tradition\w*|lễ hội|festival|ritual|nghi lễ|'
                r'đình|đền|chùa|cổ kính|cổ truyền|xưa|thời pháp|colonial|thuộc địa|dân gian|folk',
    'culture': r'cultur\w*|văn hoá|văn hóa|nghệ nhân|artisan|craft\w*|làng|village|ẩm thực|cuisine|music|âm nhạc|ca trù',
    'travel': r'travel|tourism|beach|resort|du lịch|biển|bãi tắm|nghỉ mát|đảo|island|peninsula|bán đảo',
    'finance': r'finance|kpi|quarter\w*|budget|tài chính|quý|ngân sách|lợi nhuận',
    'education': r'lesson|class|student|school|bài giảng|lớp|học sinh|sinh viên|giáo dục',
    'youth': r'youth|kids|children|teen|thiếu nhi|trẻ em|học trò',
    'event': r'event|campaign|concert|keynote|sự kiện|chiến dịch|buổi diễn',
    'software': r'developer|code|api|terminal|hacker|lập trình|mã nguồn',
    'food': r'food|recipe|cook\w*|món|bánh|nấu|ẩm thực',
}
TONES = {
    'technical': r'technical|precise|engineering|kỹ thuật|chính xác',
    'cinematic': r'cinematic|epic|dramatic|điện ảnh|hùng tráng|kịch tính',
    'bold': r'bold|ambitious|daring|táo bạo|tham vọng|mạnh mẽ',
    'calm': r'calm|quiet|clear|rõ ràng|điềm tĩnh|bình thản',
    'warm': r'warm|human|ấm|gần gũi|thân thuộc',
    'nostalgic': r'nostalg\w*|memory|ký ức|hoài niệm|xưa|thuở',
    'solemn': r'solemn|ceremon\w*|sacred|trang nghiêm|linh thiêng|thờ',
    'playful': r'playful|fun|vui|hài hước|tươi',
    'energetic': r'energetic|fast|sôi động|nhanh|hào hứng',
    'luxurious': r'luxur\w*|premium|sang trọng|cao cấp',
}
KIND_PRIOR = {'heritage': {'heritage': 1.0, 'culture': 0.6}, 'product': {'technology': 0.8}, 'pitch': {'business': 0.7, 'technology': 0.4},
              'business': {'business': 1.0, 'finance': 0.6}, 'company-profile': {'business': 0.6}, 'education': {'education': 0.8},
              'event': {'event': 1.0}}
KIND_TONE = {'heritage': ['warm', 'nostalgic', 'solemn'], 'product': ['bold', 'cinematic'], 'pitch': ['bold'], 'business': ['calm'],
             'company-profile': ['bold', 'calm'], 'education': ['calm', 'playful'], 'event': ['energetic']}


def read(p):
    return Path(p).read_text(encoding='utf-8', errors='replace') if Path(p).is_file() else ''


def brief(work):
    out = {}
    for line in read(work / 'brief.md').splitlines():
        m = re.match(r'\s*-\s*([a-z_]+)\s*:\s*(.*)', line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def count_terms(text, table):
    text = text.lower()
    out = {}
    for k, pat in table.items():
        hits = re.findall(r'(?<![\w])(?:' + pat + r')(?![\w])', text)
        if hits:
            out[k] = (len(hits), sorted(set(hits))[:6])
    return out


def subject_profile(work):
    """Domain weights 0..1 with the words that produced them; tone list."""
    b = brief(work)
    kind = (b.get('deliverable_kind') or 'other').split()[0].lower()
    core = ' '.join(b.get(k, '') for k in ('topic', 'audience', 'tone'))
    support = read(work / 'research/facts.md') + '\n' + read(work / 'assets/CREDITS.md')
    c_core, c_sup = count_terms(core, DOMAINS), count_terms(support, DOMAINS)
    raw = {}
    for k in set(c_core) | set(c_sup):
        raw[k] = 3.0 * c_core.get(k, (0,))[0] + min(30, c_sup.get(k, (0,))[0]) / 3.0
    for k, v in KIND_PRIOR.get(kind, {}).items():
        raw[k] = raw.get(k, 0) + 6 * v
    top = max(raw.values(), default=1) or 1
    dom = {k: round(min(1.0, v / top), 3) for k, v in sorted(raw.items(), key=lambda kv: -kv[1])}
    evidence = {k: sorted(set(c_core.get(k, (0, []))[1] + c_sup.get(k, (0, []))[1]))[:6] for k in dom}
    tone_txt = b.get('tone', '') + ' ' + b.get('topic', '') + ' ' + ' '.join(re.findall(r'"([^"]+)"', read(work / 'brief.md')))
    tones = sorted(count_terms(tone_txt, TONES))
    declared = bool(b.get('tone'))
    if not tones:
        tones = KIND_TONE.get(kind, ['calm'])
    return {'kind': kind, 'domains': dom, 'evidence': evidence, 'tones': tones, 'tone_declared': declared}


def _img_traits(p):
    from PIL import Image, ImageOps
    try:
        im = Image.open(p)
        im = ImageOps.exif_transpose(im)
    except Exception:
        return None
    cut = im.mode in ('RGBA', 'LA', 'PA') and im.getchannel('A').getextrema()[0] < 16
    import numpy as np
    a = np.asarray(im.convert('RGB').resize((48, 32)), np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    lum = float((0.2126 * r + 0.7152 * g + 0.0722 * b).mean())
    sat = float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
    warm = float((r > b + 0.05).mean())
    cool = float((b > r + 0.05).mean())
    return {'lum': lum, 'sat': sat, 'warm': warm, 'cool': cool, 'cutout': cut}


def material_profile(work):
    """What the pictures ARE: measured from the files, not their names."""
    files = [p for p in sorted((work / 'assets').rglob('*')) if p.suffix.lower() in IMG and 'grounds' not in p.parts
             and not p.name.startswith(('.', '_'))] if (work / 'assets').is_dir() else []
    credits = read(work / 'assets/CREDITS.md')
    years = [int(y) for y in re.findall(r'(?<![\d/.-])(18[5-9]\d|19[0-6]\d)(?![\d/.-])', credits + ' ' + ' '.join(p.stem for p in files))]
    gen = [p for p in files if 'gen' in p.parts]
    rows = []
    for p in files[:80]:
        t = _img_traits(p)
        if t:
            # archival = an old print: low colour on a lit picture with a warm or neutral cast, or a pre-1970 date in its name
            t['archival'] = bool((t['sat'] < 0.12 and t['lum'] > 0.22 and t['warm'] >= t['cool'])
                                 or re.search(r'(?<!\d)(18[5-9]\d|19[0-6]\d)(?!\d)', p.name))
            rows.append(t)
    n = len(rows) or 1
    share = lambda f: round(sum(1 for r in rows if f(r)) / n, 3) if rows else 0.0
    return {'images': len(rows), 'generated': len(gen), 'photos': max(0, len(rows) - len(gen)),
            'dark': share(lambda r: r['lum'] < 0.33), 'bright': share(lambda r: r['lum'] > 0.62),
            'saturated': share(lambda r: r['sat'] > 0.35), 'muted': share(lambda r: r['sat'] < 0.18),
            'warm': share(lambda r: r['warm'] > 0.5), 'cool': share(lambda r: r['cool'] > 0.35),
            'cutout': share(lambda r: r['cutout']), 'archival': share(lambda r: r['archival']),
            'old_dates': sorted(set(y for y in years if y < 1970))[:8],
            'mean_lum': round(sum(r['lum'] for r in rows) / n, 3) if rows else None}


def packs():
    out = {}
    for d in PACK_DIRS:
        for p in sorted(d.glob('*.json')):
            try:
                s = json.loads(p.read_text(encoding='utf-8'))
            except ValueError:
                continue
            out[s.get('name', p.stem)] = {'label': s.get('label', ''), 'fit': s.get('fit') or {}, 'experimental': d.name.endswith('experimental'),
                                          'palette': s.get('palette', {})}
    return out


def _palette_material(pal):
    from_hex = lambda h: tuple(int(h.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4))
    g = pal.get('ground') or (list(pal.values())[0] if pal else None)
    if not g or not str(g).startswith('#'):
        return {}
    r, gg, b = from_hex(g)
    lum = 0.2126 * r + 0.7152 * gg + 0.0722 * b
    return {'dark': 1.0 if lum < 0.3 else 0.0, 'bright': 1.0 if lum > 0.7 else 0.0, 'warm': 1.0 if r > b + 0.06 else 0.0,
            'cool': 1.0 if b > r + 0.06 else 0.0}


def score(cand, subj, mat):
    fit = cand['fit']
    doms = fit.get('domains', {})
    lead = [k for k, v in subj['domains'].items() if v >= 0.5]
    # domain: how well the candidate's domains cover this deck's leading domains (weighted)
    wsum = sum(subj['domains'].values()) or 1
    d = sum(v * doms.get(k, 0) for k, v in subj['domains'].items()) / wsum
    d = min(1.0, d * 1.6)
    t_want = set(fit.get('tones', []))
    t = len(t_want & set(subj['tones'])) / max(1, min(len(subj['tones']), 3)) if t_want else 0.3
    t = min(1.0, t)
    m_want = fit.get('material', {})
    if m_want and mat['images']:
        m = sum(w * mat.get(k, 0) for k, w in m_want.items()) / (sum(m_want.values()) or 1)
        m = min(1.0, m * 1.5)
    elif m_want:
        m = 0.5 if 'diagram' in m_want or 'drawn' in m_want else 0.35
    else:
        m = 0.4
    total = round(0.45 * d + 0.20 * t + 0.35 * m, 3)
    reasons = []
    for av in fit.get('avoid', []):
        if av.get('domain') in lead:
            reasons.append(f'{av["domain"]} is a leading subject here: {av.get("reason", "mismatch")}')
    if not reasons and total < REJECT_BELOW:
        weak = min((('subject', d), ('tone', t), ('material', m)), key=lambda kv: kv[1])
        reasons.append(f'fit {total:.2f} < {REJECT_BELOW}: weakest on {weak[0]} ({weak[1]:.2f}); '
                       f'its domains {sorted(doms, key=lambda k: -doms[k])[:3]} vs this deck {lead[:3]}')
    return {'fit': total, 'domain': round(d, 3), 'tone': round(t, 3), 'material': round(m, 3), 'rejected': reasons}


def directions_candidates(work, pk):
    p = work / 'design/directions.json'
    if not p.is_file():
        return {}
    try:
        spec = json.loads(read(p))
    except ValueError:
        return {}
    out = {}
    for d in spec.get('directions', []):
        fam = d.get('family')
        base = pk.get(fam, {}).get('fit', {}) if fam else {}
        fit = json.loads(json.dumps(base)) if base else {'domains': {}, 'tones': [], 'material': {}}
        for k in ('domains', 'tones', 'avoid'):
            if d.get(k):
                fit[k] = d[k]
        pal = d.get('palette') or []
        if pal and not d.get('material'):
            fit['material'] = {**fit.get('material', {}), **{k: v for k, v in _palette_material({'ground': pal[0]}).items() if v}}
        out[f'direction:{d.get("id", "?")}'] = {'label': d.get('name', ''), 'fit': fit, 'family': fam}
    return out


def fingerprint(work):
    h = hashlib.sha256()
    h.update(read(work / 'brief.md').encode())
    h.update(read(work / 'assets/CREDITS.md').encode())
    for p in sorted((work / 'assets').rglob('*')) if (work / 'assets').is_dir() else []:
        if p.suffix.lower() in IMG:
            h.update(p.name.encode())
    return h.hexdigest()[:16]


def route(work, choose=None, why=''):
    work = Path(work).resolve()
    subj, mat, pk = subject_profile(work), material_profile(work), packs()
    cands = {**{k: v for k, v in pk.items()}, **directions_candidates(work, pk)}
    scored = []
    for name, c in cands.items():
        if not c['fit']:
            continue
        s = score(c, subj, mat)
        scored.append({'name': name, 'label': c.get('label', '')[:90], 'family': c.get('family'), **s})
    scored.sort(key=lambda r: (bool(r['rejected']), -r['fit']))
    ok = [r for r in scored if not r['rejected']]
    if choose:
        hit = [r for r in scored if r['name'] == choose]
        if not hit:
            raise SystemExit(f'--choose {choose!r}: not a candidate ({", ".join(r["name"] for r in scored)})')
        if hit[0]['rejected']:
            raise SystemExit(f'--choose {choose!r} was rejected: {hit[0]["rejected"][0]}. Choose a fitting direction, or change '
                             'the brief/assets if the analysis is wrong (and say why in brief.md)')
        if len(why.split()) < 8:
            raise SystemExit('--why needs a sentence (8+ words): why this direction over the top-ranked one')
        chosen, how = choose, 'author'
    else:
        chosen, how = (ok[0]['name'] if ok else None), 'auto'
        why = why or (f'highest fit {ok[0]["fit"]:.2f} (subject {ok[0]["domain"]:.2f}, tone {ok[0]["tone"]:.2f}, '
                      f'material {ok[0]["material"]:.2f})' if ok else 'no candidate fits')
    dec = {'version': '5.5', 'fingerprint': fingerprint(work), 'subject': subj, 'material': mat, 'ranked': scored,
           'rejected': {r['name']: r['rejected'] for r in scored if r['rejected']}, 'chosen': chosen, 'how': how, 'why': why,
           'runner_up': [r['name'] for r in ok if r['name'] != chosen][:3]}
    (work / 'design').mkdir(parents=True, exist_ok=True)
    (work / 'design/routing.json').write_text(json.dumps(dec, ensure_ascii=False, indent=1), encoding='utf-8')
    (work / 'design/routing.md').write_text(render_md(dec), encoding='utf-8')
    return dec


def render_md(dec):
    s, m = dec['subject'], dec['material']
    L = ['# Routing (v5.5) — written by route.py; re-run after the brief or the assets change', '',
         f'- kind: {s["kind"]}; leading subjects: ' + ', '.join(f'{k} {v:.2f} ({", ".join(s["evidence"].get(k, [])[:4])})'
                                                            for k, v in list(s['domains'].items())[:5]),
         f'- tone: {", ".join(s["tones"])}' + ('' if s['tone_declared'] else ' (inferred from the kind; add "- tone: ..." to brief.md)'),
         f'- material: {m["images"]} images ({m["photos"]} photos, {m["generated"]} generated); dark {m["dark"]:.0%}, bright {m["bright"]:.0%}, '
         f'saturated {m["saturated"]:.0%}, muted {m["muted"]:.0%}, warm {m["warm"]:.0%}, cool {m["cool"]:.0%}, cut-outs {m["cutout"]:.0%}, '
         f'archival {m["archival"]:.0%}' + (f', dates {m["old_dates"]}' if m['old_dates'] else ''), '',
         '| rank | candidate | fit | subject | tone | material | verdict |', '|---|---|---|---|---|---|---|']
    for i, r in enumerate(dec['ranked'], 1):
        verdict = 'REJECTED: ' + r['rejected'][0] if r['rejected'] else ('**chosen**' if r['name'] == dec['chosen'] else 'fits')
        L.append(f'| {i} | {r["name"]} | {r["fit"]:.2f} | {r["domain"]:.2f} | {r["tone"]:.2f} | {r["material"]:.2f} | {verdict.replace("|", "/")} |')
    L += ['', f'## Decision', f'- chosen: {dec["chosen"]} ({dec["how"]})', f'- why: {dec["why"]}',
          f'- runners-up: {", ".join(dec["runner_up"]) or "none"}',
          '- next: the chosen family is where the genome STARTS (references/design-space.md); the deck still invents its own '
          'palette from its pictures, its layouts and its motion grammar.']
    return '\n'.join(L) + '\n'


def used_families(work):
    """The pack families a deck's styles come from (deck.json style/styles/style_overrides, design/style.json)."""
    work = Path(work)
    fams = set()
    names = set(packs())

    def from_style(v, depth=0):
        if depth > 4 or v is None:
            return
        if isinstance(v, dict):
            from_style(v.get('extends'), depth + 1)
            if v.get('name') in names:
                fams.add(v['name'])
            if v.get('route'):
                fams.add(v['route'])
            return
        v = str(v)
        if v in names:
            fams.add(v)
        elif v.endswith('.json'):
            p = work / v
            if p.is_file():
                try:
                    from_style(json.loads(read(p)), depth + 1)
                except ValueError:
                    pass
    try:
        spec = json.loads(read(work / 'deck.json')) if (work / 'deck.json').is_file() else {}
    except ValueError:
        spec = {}
    inline = {**(spec.get('styles') or {}), **{k: v for k, v in (spec.get('style_overrides') or {}).items() if k not in names}}
    seq = [spec.get('style')] + [s.get('style') for s in spec.get('slides', []) if s.get('style')]
    for v in seq:
        if isinstance(v, str) and v in inline:
            from_style(inline[v])
        else:
            from_style(v)
    if not spec and (work / 'design/style.json').is_file():
        from_style('design/style.json')
    return fams


def gate_rows(work):
    """(need rows, want rows) for gate 3: [(ok, text, hint)]."""
    work = Path(work)
    p = work / 'design/routing.json'
    need, want = [], []
    if not p.is_file():
        need.append((False, 'design/routing.json: the deck was routed (subject, audience, tone and assets analysed; candidates scored)',
                     'python3 route.py WORK'))
        return need, want
    try:
        dec = json.loads(read(p))
    except ValueError:
        need.append((False, 'design/routing.json parses', 'python3 route.py WORK'))
        return need, want
    need.append((bool(dec.get('chosen')), f'routing: a direction was chosen ({dec.get("chosen")}, {dec.get("how")})',
                 'no candidate fits: add a "- tone:" line and real assets, or write a direction in design/directions.json'))
    fresh = dec.get('fingerprint') == fingerprint(work)
    want.append((fresh, 'routing is current (brief and assets unchanged since route.py ran)', 'python3 route.py WORK'))
    rej = dec.get('rejected', {})
    need.append((bool(rej), f'routing: {len(rej)} mismatched direction(s) rejected with a written reason',
                 'the router found nothing to reject: the subject analysis is too thin (fill topic/audience/tone in brief.md)'))
    fams = used_families(work)
    bad = sorted(f for f in fams if f in rej)
    need.append((not bad, f'the deck\'s styles {sorted(fams) or ["(own genome)"]} avoid the rejected directions',
                 '; '.join(f'{b}: {rej[b][0]}' for b in bad)[:300]))
    ch = dec.get('chosen') or ''
    fam_of_choice = ch.split(':', 1)[0] if not ch.startswith('direction:') else None
    if fams and fam_of_choice and fam_of_choice not in fams:
        others = [f for f in fams if f not in rej]
        want.append((False, f'the deck uses {sorted(fams)}, the router chose {ch}',
                     f're-run route.py WORK --choose {others[0] if others else "<family>"} --why "..." to record the reason'))
    top = next((r for r in dec.get('ranked', []) if r['name'] == ch), None)
    if top:
        want.append((top['fit'] >= 0.6, f'routing: the chosen direction fits {top["fit"]:.2f} (0.60+)', 'see design/routing.md: weakest axis'))
    return need, want


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work')
    ap.add_argument('--choose')
    ap.add_argument('--why', default='')
    ap.add_argument('--print', action='store_true')
    a = ap.parse_args(argv)
    work = Path(a.work)
    if a.print:
        print(read(work / 'design/routing.md'))
        return 0
    dec = route(work, a.choose, a.why)
    print(render_md(dec))
    return 0 if dec['chosen'] else 1


if __name__ == '__main__':
    sys.exit(main())
