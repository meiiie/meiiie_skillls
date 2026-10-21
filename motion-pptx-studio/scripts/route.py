"""Route a deck to fitting art directions BEFORE any design (v5.5; semantic subject analysis v5.6): analyse the subject, the audience, the
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

# ---------------------------------------------------------------- subject analysis (v5.6)
# Routing judges what the talk is ABOUT, not which words occur somewhere. Each domain has STRONG terms (they
# define a subject: "lạm phát", "booster", "di sản") and WEAK terms (ambiguous or incidental: "AI", "tech",
# "market", "NASA"). Where a word occurs matters more than how often: the topic's head phrase (before the first
# dash/colon/bracket) and the rest of the topic carry the subject; the audience says who listens (not what it is
# about); the user's own words support; research/facts.md is support, density-normalised and capped; CREDITS
# (what a photo shows and who took it) never counts as subject. A domain with no evidence in the topic, the
# user's words or a declaration is only "mentioned" and cannot lead (capped at 0.35). The author (or the agent,
# which can read the brief semantically) may DECLARE domains: "- domains: economy, finance" in brief.md or
# design/subject.json {"domains": {"economy": 1, ...}, "tones": [...], "why": "..."}; declarations win and the
# lexicon is reported next to them as a cross-check.
DOMAINS = {
    'economy': (r'econom\w*|macro\w*|gdp|inflation|disinflation|interest rates?|central banks?|monetary|fiscal|recession|tariffs?|'
                r'global trade|world trade|trade (?:war|deficit|surplus|flows?|policy)|public debt|sovereign debt|imf|world bank|oecd|wto|'
                r'unemployment|exchange rates?|kinh tế|vĩ mô|tăng trưởng|lạm phát|lãi suất|ngân hàng trung ương|tiền tệ|tài khóa|tài khoá|'
                r'suy thoái|thuế quan|thương mại|nợ công|thất nghiệp|tỷ giá|xuất khẩu|nhập khẩu|cán cân|fed|ecb',
                r'growth|trade|debt|prices?|đầu tư|investment|banks?|ngân hàng|giá cả|thị trường|ports?|cảng|container|teu|logistics|hàng hóa|sản lượng'),
    'finance': (r'finance|financial|bonds?|equit(?:y|ies)|stock markets?|yields?|tài chính|trái phiếu|chứng khoán|lợi suất|cổ phiếu',
                r'kpi|quarter\w*|budget|quý|ngân sách|lợi nhuận|profit\w*|revenue'),
    'business': (r'compan(?:y|ies)|corporate|startups?|investors?|valuation|nasdaq|ipo|doanh nghiệp|doanh thu|định giá|công ty|'
                 r'nhà đầu tư|khởi nghiệp|business review|brand',
                 r'markets?|profile|revenue|customers?|khách hàng|sales'),
    'energy': (r'crude|opec|oil prices?|energy (?:prices?|shock|crisis|transition)|lng|năng lượng|dầu thô|giá dầu|khí đốt|điện gió|điện mặt trời',
               r'energy|oil|gas|dầu|điện'),
    'technology': (r'technolog\w*|software|hardware|semiconductors?|artificial intelligence|machine learning|công nghệ|bán dẫn|'
                   r'trí tuệ nhân tạo|phần mềm|reusab\w*|tái sử dụng',
                   r'ai|tech|chips?|robot\w*|digital|số hoá|số hóa|data cent(?:er|re)s?|wafers?'),
    'aerospace': (r'rockets?|boosters?|spacecraft|space ?x|falcon 9|falcon|starship|launch vehicles?|orbit\w*|aerospace|tên lửa|'
                  r'tàu vũ trụ|quỹ đạo|tầng đẩy|hàng không vũ trụ|grid fins?|landing legs?',
                  r'nasa|launch(?:es)?|satellites?|vệ tinh|phóng|space|vũ trụ|merlin|dragon|starlink'),
    'engineering': (r'engineering|mechanis\w*|propulsion|thrust|kỹ thuật|cơ chế|lực đẩy|kết cấu|chân đáp|động cơ',
                    r'engines?|structure|machine'),
    'science': (r'physics|chemistry|biology|experiment\w*|khoa học|vật lý|hoá học|hóa học|sinh học|thí nghiệm', r'research|nghiên cứu|scien\w*'),
    'health': (r'health|medic\w*|hospital|vaccin\w*|disease|y tế|bệnh viện|sức khỏe|sức khoẻ|bệnh', r'doctor|bác sĩ|care'),
    'climate': (r'climate|emissions?|carbon|biodiversity|khí hậu|phát thải|môi trường', r'green|xanh|weather|thời tiết'),
    'heritage': (r'heritage|di sản|di tích|lễ hội|rituals?|nghi lễ|đình|đền|chùa|cổ kính|cổ truyền|thời pháp|colonial|thuộc địa|'
                 r'dân gian|folk|truyền thống|traditions?|traditional',
                 r'xưa|festival|trăm năm|hundred years|hải đăng|lighthouse|monument'),
    'history': (r'history|lịch sử|historic\w*|centur(?:y|ies)|thế kỷ|dynast(?:y|ies)|triều|thời kỳ', r'1[5-9]\d\d(?:\s*[–-]\s*1[5-9]\d\d)?'),
    'culture': (r'cultur\w*|văn hoá|văn hóa|nghệ nhân|artisans?|crafts?|làng nghề|ẩm thực|cuisine|âm nhạc|ca trù', r'music|làng|village|art'),
    'travel': (r'travel|tourism|resorts?|du lịch|nghỉ mát|bãi tắm|bán đảo|peninsula', r'beach|biển|đảo|islands?|hotel'),
    'education': (r'lessons?|curriculum|bài giảng|giáo dục|bài học|lớp học', r'class|students?|school|lớp|học sinh|sinh viên'),
    'youth': (r'youth|kids|children|teens?|thiếu nhi|trẻ em|học trò', r'young|trẻ'),
    'event': (r'event|campaign|concert|sự kiện|chiến dịch|buổi diễn|launch event', r'keynote|show'),
    'software': (r'developers?|source code|apis?|terminal|hacker\w*|lập trình|mã nguồn|open source', r'code|app'),
    'food': (r'food|recipes?|cooking|cuisine|món ăn|bánh|nấu ăn|ẩm thực', r'món|nấu|cook\w*'),
}
# what each subject needs from a design: rejection reasons are composed from THIS deck's evidence plus these
DOMAIN_NEEDS = {
    'economy': 'figures that read exact at a glance, daylight legibility for dense numbers and a source on every one',
    'finance': 'exact figures, comparisons and sources a decision-maker can trust',
    'business': 'clear evidence and numbers that read as accountable',
    'energy': 'scale, prices and flows shown plainly',
    'technology': 'precision, real hardware and a present-tense register',
    'aerospace': 'precision and scale: real hardware shot cold and high-contrast',
    'engineering': 'parts, mechanisms and dimensions that can be read',
    'science': 'evidence, diagrams and restraint',
    'health': 'care, clarity and calm',
    'climate': 'evidence and scale without alarmism',
    'heritage': 'the warmth and age of real places, objects and people',
    'history': 'the texture of the period and its documents',
    'culture': 'people, places and craft seen as they are',
    'travel': 'the place itself: light, colour and air',
    'education': 'patient, readable explanation',
    'youth': 'energy and play at the audience\'s level',
    'event': 'energy and one strong idea per moment',
    'software': 'the product\'s own screens and logic',
    'food': 'appetite: warmth, colour and texture',
}
# tone: words -> positions on four axes (energy, warmth, formality, drama). A family's tones and the deck's
# tones are compared by direction, so "serious, analytical" sits near "calm, precise" without sharing a word.
TONE_VEC = {
    'technical': (0.0, -0.4, 0.6, 0.0), 'precise': (-0.1, -0.3, 0.7, -0.2), 'cinematic': (0.4, 0.0, 0.2, 0.9),
    'bold': (0.7, 0.1, 0.0, 0.6), 'calm': (-0.7, 0.1, 0.3, -0.5), 'warm': (-0.2, 0.9, 0.0, 0.1),
    'nostalgic': (-0.4, 0.7, 0.1, 0.3), 'solemn': (-0.6, 0.2, 0.8, 0.4), 'playful': (0.6, 0.6, -0.8, 0.2),
    'energetic': (0.9, 0.3, -0.4, 0.4), 'luxurious': (-0.2, 0.3, 0.6, 0.7), 'serious': (-0.3, -0.1, 0.8, 0.0),
    'analytical': (-0.3, -0.4, 0.7, -0.4), 'editorial': (-0.2, 0.1, 0.6, 0.1), 'clear': (-0.3, 0.0, 0.4, -0.6),
    'authoritative': (0.0, -0.1, 0.9, 0.2), 'urgent': (0.6, -0.2, 0.3, 0.6), 'intimate': (-0.5, 0.8, -0.1, 0.0),
    'inspiring': (0.5, 0.4, 0.1, 0.6), 'minimal': (-0.4, -0.2, 0.4, -0.8), 'raw': (0.4, -0.2, -0.4, 0.5),
    'elegant': (-0.3, 0.2, 0.6, 0.4), 'friendly': (0.2, 0.8, -0.5, 0.0),
}
TONES = {
    'technical': r'technical|engineering|kỹ thuật', 'precise': r'precise|exact|accurate|chính xác', 'cinematic': r'cinematic|epic|điện ảnh|hùng tráng',
    'bold': r'bold|ambitious|daring|táo bạo|tham vọng|mạnh mẽ', 'calm': r'calm|quiet|composed|điềm tĩnh|bình thản|nhẹ nhàng|điềm đạm',
    'warm': r'warm|human|ấm|ấm áp|gần gũi|thân thuộc', 'nostalgic': r'nostalg\w*|memory|ký ức|hoài niệm|thuở', 'solemn': r'solemn|ceremon\w*|sacred|trang nghiêm|linh thiêng',
    'playful': r'playful|fun|vui|hài hước|tươi', 'energetic': r'energetic|fast|lively|sôi động|hào hứng', 'luxurious': r'luxur\w*|premium|sang trọng|cao cấp',
    'serious': r'serious|sober|formal|nghiêm túc|trang trọng|chững chạc', 'analytical': r'analytic\w*|data[- ]driven|evidence[- ]based|phân tích|dựa trên số liệu',
    'editorial': r'editorial|journalis\w*|newsy|báo chí|biên tập', 'clear': r'clear|plain|lucid|rõ ràng|dễ hiểu|mạch lạc',
    'authoritative': r'authoritative|credible|trustworthy|đáng tin|uy tín', 'urgent': r'urgent|alarm\w*|khẩn|cấp bách', 'intimate': r'intimate|personal|riêng tư|tâm tình',
    'inspiring': r'inspir\w*|uplifting|truyền cảm hứng', 'minimal': r'minimal\w*|restrained|tối giản|tiết chế', 'raw': r'raw|gritty|thô|bụi',
    'elegant': r'elegant|refined|tinh tế|thanh lịch', 'friendly': r'friendly|approachable|thân thiện',
    'dramatic': r'dramatic|kịch tính', 'respectful': r'respect\w*|reverent|tôn trọng|trân trọng',
}
TONE_VEC['dramatic'] = (0.5, 0.0, 0.2, 0.9)
TONE_VEC['respectful'] = (-0.4, 0.4, 0.6, 0.1)
KIND_PRIOR = {'heritage': {'heritage': 1.0, 'culture': 0.6}, 'product': {'technology': 0.8}, 'pitch': {'business': 0.7, 'technology': 0.4},
              'business': {'business': 1.0, 'finance': 0.6}, 'company-profile': {'business': 0.6}, 'education': {'education': 0.8},
              'event': {'event': 1.0}}
KIND_TONE = {'heritage': ['warm', 'nostalgic', 'solemn'], 'product': ['bold', 'cinematic'], 'pitch': ['bold'], 'business': ['calm', 'serious'],
             'company-profile': ['bold', 'calm'], 'education': ['calm', 'playful'], 'event': ['energetic']}
ZONES = (('head', 4.0, 1.0), ('topic', 2.5, 0.5), ('words', 1.5, 0.3), ('audience', 0.6, 0.1))   # (zone, strong, weak)
ABOUT_MIN = 0.25   # v5.6: share of the leading domain's weight a domain needs to count as what the deck is about
MENTION_CAP = 0.35
EXCLUDE_ASSET_DIRS = {'candidates', 'rejected', '_uncertain', 'uncertain', 'raw', 'thumbs', 'grounds', 'cut', 'film', 'drawn',
                      'samples', 'contact', 'tmp', 'media_orig'}


def read(p):
    return Path(p).read_text(encoding='utf-8', errors='replace') if Path(p).is_file() else ''


def brief(work):
    out = {}
    for line in read(work / 'brief.md').splitlines():
        m = re.match(r'\s*-\s*([a-z_]+)\s*:\s*(.*)', line)
        if m and m.group(1) not in out:
            out[m.group(1)] = m.group(2).strip()
    return out


def user_words(work):
    """The quoted lines under the brief's '## The user's own words' heading."""
    t = read(work / 'brief.md')
    m = re.search(r"^##[^\n]*(?:own words|lời người dùng)[^\n]*\n(.*?)(?=^## |\Z)", t, re.I | re.M | re.S)
    return m.group(1) if m else ''


def _hits(text, pat):
    if not text or not pat:
        return []
    return re.findall(r'(?<![\w])(?:' + pat + r')(?![\w])', text.lower())


def count_terms(text, table):
    """{key: (count, sorted unique hits)} for a {key: regex} table (kept for callers and tests)."""
    out = {}
    for k, pat in table.items():
        hits = _hits(text, pat if isinstance(pat, str) else '|'.join(p for p in pat if p))
        if hits:
            out[k] = (len(hits), sorted(set(hits))[:6])
    return out


def split_topic(topic):
    m = re.split(r'\s[—–-]\s|:|\(|;', topic, maxsplit=1)
    head = m[0] if m else topic
    return head, topic[len(head):]


def brief_value(v):
    """A brief line's value without its (template guidance); '' for TODO / auto / none."""
    v = re.sub(r'\([^)]*\)', ' ', v or '').strip()
    return '' if not v or 'TODO' in v or v.lower() in ('auto', 'none', '-', 'routed') else v


def declared_domains(work, b):
    out, why = {}, ''
    sj = work / 'design/subject.json'
    if sj.is_file():
        try:
            d = json.loads(read(sj))
            out = {k: float(v) for k, v in (d.get('domains') or {}).items()}
            why = d.get('why', '')
        except (ValueError, TypeError, AttributeError):
            pass
    dv = brief_value(b.get('domains', ''))
    if not out and dv:
        names = [x.strip().lower() for x in re.split(r'[,;/]', dv) if x.strip()]
        out = {n: round(max(0.4, 1.0 - 0.15 * i), 2) for i, n in enumerate(names)}
        why = 'declared in brief.md (- domains:)'
    unknown = sorted(k for k in out if k not in DOMAINS)
    return out, why, unknown


def subject_profile(work):
    """Domain weights 0..1 with the words (and where they were found) that produced them; tones."""
    work = Path(work)
    b = brief(work)
    kind = (b.get('deliverable_kind') or 'other').split()[0].lower()
    head, rest = split_topic(b.get('topic', ''))
    zones = {'head': head, 'topic': rest, 'words': user_words(work), 'audience': b.get('audience', '')}
    facts = read(work / 'research/facts.md')
    nwords = max(300, len(facts.split()))
    raw, evidence, about = {}, {}, set()
    for dom, (strong, weak) in DOMAINS.items():
        s, words_hit = 0.0, False
        for zone, ws, ww in ZONES:
            hs, hw = _hits(zones[zone], strong), _hits(zones[zone], weak)
            s += ws * len(hs) + ww * len(hw)
            if (hs or hw) and zone in ('head', 'topic'):
                about.add(dom)
            elif hs and zone == 'words':
                words_hit = True
            for h in hs + hw:
                evidence.setdefault(dom, []).append(f'{h} ({zone})')
        fs, fw = _hits(facts, strong), _hits(facts, weak)
        if words_hit and len(set(fs)) >= 2:          # the user's words count as subject when the research agrees
            about.add(dom)
        s += min(3.0, 0.15 * len(fs) * 1000 / nwords) + min(0.6, 0.03 * len(fw) * 1000 / nwords)
        for h in sorted(set(fs))[:3]:
            evidence.setdefault(dom, []).append(f'{h} (facts)')
        if s:
            raw[dom] = s
    for k, v in KIND_PRIOR.get(kind, {}).items():
        raw[k] = raw.get(k, 0) + 2.0 * v
    top = max(raw.values(), default=1) or 1
    dom = {k: min(1.0, v / top) for k, v in raw.items()}
    # "about" also needs weight: a sub-theme named once in a long topic ("làn sóng đầu tư AI" in an economics
    # brief) is part of the story, not what the deck is about (ABOUT_MIN of the leading domain)
    about = {k for k in about if dom.get(k, 0) >= ABOUT_MIN}
    mentioned = sorted(k for k in dom if k not in about and k not in KIND_PRIOR.get(kind, {}))
    for k in mentioned:
        dom[k] = min(dom[k], MENTION_CAP)
    decl, decl_why, decl_unknown = declared_domains(work, b)
    lexicon = {k: round(v, 3) for k, v in sorted(dom.items(), key=lambda kv: -kv[1])}
    if decl:
        dom = {k: max(v, dom.get(k, 0)) if k in decl else min(dom.get(k, 0), MENTION_CAP) for k, v in {**dom, **decl}.items()}
        for k, v in decl.items():
            dom[k] = v
        # a declaration says what the deck is ABOUT: it replaces the lexicon's "about" set
        about = {k for k in decl if k in DOMAINS}
        mentioned = sorted(k for k in dom if k not in decl and k not in KIND_PRIOR.get(kind, {}) and dom[k] > 0)
    dom = {k: round(v, 3) for k, v in sorted(dom.items(), key=lambda kv: -kv[1]) if v > 0}
    ev = {k: list(dict.fromkeys(evidence.get(k, [])))[:6] for k in dom}
    tone_raw = brief_value(b.get('tone', ''))
    tone_words = [w.strip().lower() for w in re.split(r'[,;/|]|\s[—–-]\s', tone_raw) if w.strip()]
    neg = re.compile(r'^(?:không|chẳng|tránh|not|no|never|avoid|without)\b', re.I)
    excluded = [w for w in tone_words if neg.search(w)]
    tone_txt = ' '.join([', '.join(w for w in tone_words if w not in excluded), zones['words']])
    unknown_t = [w for w in tone_words if w not in excluded and not any(_hits(w, p) for p in TONES.values())]
    found = sorted(k for k in count_terms(tone_txt, TONES) if not any(_hits(x, TONES[k]) for x in excluded))
    declared = bool(tone_raw)
    tones = found or KIND_TONE.get(kind, ['calm'])
    return {'kind': kind, 'domains': dom, 'evidence': ev, 'about': sorted(about), 'mentioned': mentioned,
            'declared': decl, 'declared_why': decl_why, 'declared_unknown': decl_unknown, 'lexicon': lexicon,
            'tones': tones, 'tone_declared': declared, 'tone_unknown': unknown_t, 'tone_excluded': excluded}


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


def credits_rows(work):
    """(kept rows, kept file names) from assets/CREDITS.md tables, stopping at a 'rejected' section."""
    rows, names = [], []
    rejected = False
    for line in read(work / 'assets/CREDITS.md').splitlines():
        if line.startswith('#'):
            rejected = bool(re.search(r'reject|loại|không dùng|candidates?|ứng viên', line, re.I))
            continue
        if rejected or not line.startswith('|'):
            continue
        cells = [c.strip().strip('`') for c in line.strip('|').split('|')]
        f = next((c for c in cells if re.search(r'\.(?:jpe?g|png|webp)$', c, re.I)), None)
        if f:
            rows.append(line)
            names.append(Path(f).name)
    return rows, names


def kept_images(work):
    """The pictures the deck will actually use: the CREDITS table when it lists files, otherwise assets/**
    without candidate, rejected, derived (cut-outs, films, grounds) and contact-sheet files."""
    work = Path(work)
    if not (work / 'assets').is_dir():
        return []
    files = [p for p in sorted((work / 'assets').rglob('*')) if p.suffix.lower() in IMG and not p.name.startswith(('.', '_'))
             and not p.name.lower().startswith('contact') and not (set(x.lower() for x in p.relative_to(work / 'assets').parts[:-1]) & EXCLUDE_ASSET_DIRS)]
    _, names = credits_rows(work)
    if names:
        keep = set(names)
        listed = [p for p in files if p.name in keep]
        if listed:
            return listed
    return files


def material_profile(work):
    """What the kept pictures ARE: measured from the files, not their names."""
    work = Path(work)
    files = kept_images(work)
    rows_txt, _ = credits_rows(work)
    no_urls = re.sub(r'\d+\s*[×x]\s*\d+', ' ', re.sub(r'https?://\S+', ' ', ' '.join(rows_txt)))   # no URLs, no pixel sizes
    years = [int(y) for y in re.findall(r'(?<![\d/.-])(18[5-9]\d|19[0-6]\d)(?![\d/-])', no_urls + ' ' + ' '.join(p.stem for p in files))]
    gen = [p for p in files if 'gen' in p.parts]
    rows = []
    for p in files[:200]:
        t = _img_traits(p)
        if t:
            # archival = an old print: low colour on a lit picture with a warm or neutral cast, or a pre-1970 date in its name
            t['archival'] = bool((t['sat'] < 0.12 and t['lum'] > 0.22 and t['warm'] >= t['cool'])
                                 or re.search(r'(?<!\d)(18[5-9]\d|19[0-6]\d)(?!\d)', p.stem))
            rows.append(t)
    n = len(rows) or 1
    share = lambda f: round(sum(1 for r in rows if f(r)) / n, 3) if rows else 0.0  # noqa: E731
    return {'images': len(rows), 'generated': len(gen), 'photos': max(0, len(rows) - len(gen)),
            'files': [str(p.relative_to(work)) for p in files[:200]],
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


def _vec_sim(a, b):
    import math
    na, nb = math.sqrt(sum(x * x for x in a)) or 1, math.sqrt(sum(x * x for x in b)) or 1
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def tone_fit(want, have):
    """0..1: for each of the deck's tones, the nearest of the family's tones by direction on the tone axes."""
    want = [w for w in want if w in TONE_VEC]
    have = [h for h in have if h in TONE_VEC][:5]
    if not want:
        return 0.3
    if not have:
        return 0.5
    sims = [max(_vec_sim(TONE_VEC[h], TONE_VEC[w]) for w in want) for h in have]
    s = sum(sims) / len(sims)                       # cosine -1..1
    return round(max(0.0, min(1.0, (s - 0.1) / 0.8)), 3)


def describe_material(mat):
    if not mat.get('images'):
        return 'no kept pictures yet'
    keys = ('dark', 'bright', 'saturated', 'muted', 'warm', 'cool', 'cutout', 'archival')
    top = sorted(((mat.get(k, 0), k) for k in keys), reverse=True)[:3]
    return f'{mat["images"]} kept pictures, ' + ', '.join(f'{v:.0%} {k}' for v, k in top)


def _evidence_words(subj, dom, n=3):
    ev = subj['evidence'].get(dom, [])
    pri = [e for e in ev if '(head)' in e or '(topic)' in e] + [e for e in ev if '(words)' in e] + ev
    out = list(dict.fromkeys(e.split(' (')[0] for e in pri))[:n]
    if dom in subj.get('declared', {}):
        out = ['declared'] + out
    return out


def score(cand, subj, mat):
    fit = cand['fit']
    doms = fit.get('domains', {})
    lead = [k for k, v in subj['domains'].items() if v >= 0.5]
    # domain: how well the candidate's domains cover this deck's leading domains (weighted)
    wsum = sum(subj['domains'].values()) or 1
    d = sum(v * doms.get(k, 0) for k, v in subj['domains'].items()) / wsum
    d = min(1.0, d * 1.25)
    t = tone_fit(fit.get('tones', []), subj['tones']) if fit.get('tones') else 0.3
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
    # an avoid fires only for a domain the deck is ABOUT (topic, the user's words or a declaration), never for a
    # word that is merely mentioned in the facts or the photo credits
    about = set(subj.get('about', [])) | set(subj.get('declared', {}))
    for av in fit.get('avoid', []):
        dm = av.get('domain')
        if dm in lead and dm in about:
            because = av.get('because') or av.get('reason', 'mismatch')
            ev = _evidence_words(subj, dm)
            r = (f'{because}; this deck is about {dm} ({subj["domains"][dm]:.2f}: {", ".join(ev) or "kind"}), which needs '
                 f'{DOMAIN_NEEDS.get(dm, "a design of its own")}')
            clash = [k for k, w in m_want.items() if w >= 0.7 and mat.get('images') and mat.get(k, 0) < 0.15]
            if clash:
                r += f'; it also wants {"/".join(clash)} pictures, and here there are {describe_material(mat)}'
            reasons.append(r)
    if not reasons and total < REJECT_BELOW:
        axes = {'subject': d, 'tone': t, 'material': m}
        weak = min(axes, key=axes.get)
        fam_doms = sorted(doms, key=lambda k: -doms[k])[:3]
        if weak == 'subject':
            why = f'its subjects {fam_doms} do not cover what this deck is about {lead[:3]}'
        elif weak == 'tone':
            why = f'its register ({", ".join(fit.get("tones", [])[:3])}) is far from this deck\'s ({", ".join(subj["tones"][:4])})'
        else:
            want_k = sorted(m_want, key=lambda k: -m_want[k])[:2]
            why = f'it wants {"/".join(want_k)} pictures; here: {describe_material(mat)}'
        reasons.append(f'fit {total:.2f} < {REJECT_BELOW:.2f}, weakest on {weak} ({axes[weak]:.2f}): {why}')
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
        dd = d.get('domains')
        if isinstance(dd, (list, tuple)):                         # "domains": ["economy", "finance"] = ranked
            dd = {str(x).lower(): round(max(0.4, 1 - 0.15 * i), 2) for i, x in enumerate(dd)}
        if dd:                                                    # a direction ADDS to its family's subjects
            fit['domains'] = {**fit.get('domains', {}), **{k: max(v, fit.get('domains', {}).get(k, 0)) for k, v in dd.items()}}
        for k in ('tones', 'avoid'):
            if d.get(k):
                fit[k] = d[k]
        if isinstance(fit.get('tones'), str):
            fit['tones'] = [x.strip() for x in fit['tones'].split(',')]
        pal = d.get('palette') or []
        if pal and not d.get('material'):
            fit['material'] = {**fit.get('material', {}), **{k: v for k, v in _palette_material({'ground': pal[0]}).items() if v}}
        out[f'direction:{d.get("id", "?")}'] = {'label': d.get('name', ''), 'fit': fit, 'family': fam}
    return out


def route_inputs(work):
    """Hashes of what routing reads, one per input, so a stale check can say WHICH input changed. Derived files
    (cut-outs, films, grounds, contact sheets, candidates) are not inputs."""
    work = Path(work)
    b = brief(work)
    hx = lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]  # noqa: E731
    return {'brief': hx(json.dumps({k: b.get(k, '') for k in ('topic', 'audience', 'tone', 'deliverable_kind', 'domains', 'style')}, ensure_ascii=False)),
            'user_words': hx(user_words(work)), 'facts': hx(read(work / 'research/facts.md')),
            'kept_images': hx('\n'.join(str(p.relative_to(work)) for p in kept_images(work))),
            'directions': hx(read(work / 'design/directions.json')), 'subject': hx(read(work / 'design/subject.json'))}


def fingerprint(work):
    return hashlib.sha256(json.dumps(route_inputs(work), sort_keys=True).encode()).hexdigest()[:16]


def decide(work, choose=None, why=''):
    """The routing decision, computed in memory (route() writes it)."""
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
        if ok and not why:
            r0 = ok[0]
            lead = [k for k, v in subj['domains'].items() if v >= 0.5][:3]
            why = (f'highest fit {r0["fit"]:.2f}: covers {", ".join(lead) or "the subject"} (subject {r0["domain"]:.2f}), '
                   f'register near {", ".join(subj["tones"][:4])} (tone {r0["tone"]:.2f}), {describe_material(mat)} (material {r0["material"]:.2f})')
        why = why or 'no candidate fits'
    return {'version': '5.6', 'fingerprint': fingerprint(work), 'inputs': route_inputs(work), 'subject': subj, 'material': mat,
            'ranked': scored, 'rejected': {r['name']: r['rejected'] for r in scored if r['rejected']}, 'chosen': chosen, 'how': how,
            'why': why, 'runner_up': [r['name'] for r in ok if r['name'] != chosen][:3]}


def route(work, choose=None, why=''):
    work = Path(work).resolve()
    dec = decide(work, choose, why)
    (work / 'design').mkdir(parents=True, exist_ok=True)
    (work / 'design/routing.json').write_text(json.dumps(dec, ensure_ascii=False, indent=1), encoding='utf-8')
    (work / 'design/routing.md').write_text(render_md(dec), encoding='utf-8')
    return dec


def render_md(dec):
    s, m = dec['subject'], dec['material']
    L = [f'# Routing (v{dec.get("version", "5.6")}) — written by route.py; re-run after the brief or the kept assets change', '',
         f'- kind: {s["kind"]}; about: ' + (', '.join(f'{k} {v:.2f} ({", ".join(s["evidence"].get(k, [])[:4]) or "kind prior"})'
                                                  for k, v in s['domains'].items() if k in s.get('about', [])) or 'nothing yet (fill the topic)'),
         '- also weighed (kind prior, or under a quarter of the leading domain): '
         + (', '.join(f'{k} {v:.2f}' for k, v in list(s['domains'].items()) if k not in s.get('about', []) and k not in s.get('mentioned', [])
                      and v >= 0.01) or 'none'),
         f'- mentioned only (no evidence in the topic or the user\'s words, capped at {MENTION_CAP}): '
         + (', '.join(f'{k} ({", ".join(s["evidence"].get(k, [])[:2])})' for k in s.get('mentioned', []) if s['evidence'].get(k)) or 'none')]
    if s.get('declared'):
        L.append(f'- declared domains: {s["declared"]} ({s.get("declared_why", "")}); lexicon cross-check: '
                 + ', '.join(f'{k} {v:.2f}' for k, v in list(s.get('lexicon', {}).items())[:4]))
    if s.get('declared_unknown'):
        L.append(f'- WARNING: declared domains not in the lexicon (ignored by family fit): {s["declared_unknown"]}')
    L += [f'- tone: {", ".join(s["tones"])}' + ('' if s['tone_declared'] else ' (inferred from the kind; add "- tone: ..." to brief.md)')
          + (f'; not recognised: {s["tone_unknown"]}' if s.get('tone_unknown') else '')
          + (f'; excluded (negated): {s["tone_excluded"]}' if s.get('tone_excluded') else ''),
          f'- material: {m["images"]} kept images ({m["photos"]} photos, {m["generated"]} generated); dark {m["dark"]:.0%}, bright {m["bright"]:.0%}, '
          f'saturated {m["saturated"]:.0%}, muted {m["muted"]:.0%}, warm {m["warm"]:.0%}, cool {m["cool"]:.0%}, cut-outs {m["cutout"]:.0%}, '
          f'archival {m["archival"]:.0%}' + (f', dates {m["old_dates"]}' if m['old_dates'] else ''), '',
          '| rank | candidate | fit | subject | tone | material | verdict |', '|---|---|---|---|---|---|---|']
    for i, r in enumerate(dec['ranked'], 1):
        verdict = 'REJECTED: ' + r['rejected'][0] if r['rejected'] else ('**chosen**' if r['name'] == dec['chosen'] else 'fits')
        L.append(f'| {i} | {r["name"]} | {r["fit"]:.2f} | {r["domain"]:.2f} | {r["tone"]:.2f} | {r["material"]:.2f} | {verdict.replace("|", "/")} |')
    L += ['', '## Decision', f'- chosen: {dec["chosen"]} ({dec["how"]})', f'- why: {dec["why"]}',
          f'- runners-up: {", ".join(dec["runner_up"]) or "none"}',
          '- next: the chosen family is where the genome STARTS (references/design-space.md); the deck still invents its own '
          'palette from its pictures, its layouts and its motion grammar.',
          '- if the subject analysis above is wrong, declare it ("- domains: economy, finance" in brief.md or design/subject.json) and re-run; '
          'never edit the scores.']
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
    if dec.get('fingerprint') == fingerprint(work):
        want.append((True, 'routing is current (its inputs are unchanged since route.py ran)', ''))
    else:
        old, now = dec.get('inputs') or {}, route_inputs(work)
        changed = sorted(k for k in now if old.get(k) != now[k]) if old else ['(routing.json predates v5.6)']
        try:
            again = decide(work, dec.get('chosen') if dec.get('how') == 'author' else None, dec.get('why', '') if dec.get('how') == 'author' else '')
            same = again['chosen'] == dec.get('chosen') and set(again['rejected']) == set(dec.get('rejected', {}))
        except SystemExit:
            same = False
        want.append((same, f'routing is current: inputs changed ({", ".join(changed)}) — '
                     + ('the decision is the same' if same else 'the decision would CHANGE'), 'python3 route.py WORK'))
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
