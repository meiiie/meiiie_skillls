"""Hard gates for the motion-pptx-studio pipeline. A gate that fails means: STOP, do the missing work.

  python gates.py init WORK [--kind heritage|product|other]   create the working folder + templates
  python gates.py check WORK --gate N                          check gate N (0..6); exit 1 on FAIL
  python gates.py check WORK --upto N                          check gates 0..N
  python gates.py check WORK --gate 5 --group g3 --deck WORK/deck/preview-g3.pptx

Gates
  0 brief      brief.md complete (audience, minutes, language, honest status, the user's verbatim words)
  1 research   research/facts.md (sourced, tagged, do-not-say list) + research/accuracy.md
               (+ research/lessons.md when a reference talk was given)
  2 assets     assets/CREDITS.md with enough kept, licensed, verified files; >= 2x as many candidates
               looked at; a contact sheet of the kept set newer than the files; a "Rejected" list
  3 design     design/art-direction.md (fonts, palette hex, motifs, layered objects), fonts/ with
               licence, design/font-check.txt all PASS, >= 2 rendered samples in design/samples/
  4 storyboard storyboard.md: >= 8 scenes, keyframe runs (>= 60 % of scenes have >= 3 slides),
               !! layers on rows, a real visual per row, words budget within the time limit,
               anchor phrase x3, colour arc, motion.json
  5 group      renders/<group>-N/contact*.jpg, notes/<group>.md, check_deck.py passes on the preview
  6 final      deliver/ has pptx + docx + fonts/ + zip + CREDITS; check_deck passes; speaking time
               within 10 % of talk_minutes (or time_overrun_accepted: yes in brief.md)
Thresholds are minimums that reproduced the reference decks; do not lower them unless the user
explicitly accepts a lighter deck (write that in brief.md).
"""
import argparse
import datetime
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / 'assets' / 'templates'
URL = re.compile(r'https?://[^\s)|>\]]+')
TAG = re.compile(r'\[(verified|secondary|claim|disputed|uncertain|claim-in-README|verified-in-[\w-]+|ĐÃ XÁC MINH[^\]]*|THỨ CẤP|TRANH CÃI|CHƯA RÕ|CHƯA XÁC MINH)\]', re.I)
LIC = re.compile(r'CC[ -]?0|CC[ -]BY|public domain|PD|PDM|own work|owner|trademark|official|team|user|drawn|CC BY', re.I)
IMG = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
MIN = {
    'heritage': {'facts': 15, 'domains': 3, 'kept': 12, 'real': 6},
    'product': {'facts': 12, 'domains': 2, 'kept': 6, 'real': 1},
    'other': {'facts': 12, 'domains': 3, 'kept': 8, 'real': 3},
}


class Gate:
    def __init__(self, name):
        self.name, self.rows, self.ok = name, [], True

    def need(self, cond, text, hint=''):
        self.rows.append(('PASS' if cond else 'FAIL', text, '' if cond else hint))
        self.ok &= bool(cond)
        return cond

    def note(self, text):
        self.rows.append(('INFO', text, ''))

    def report(self):
        print(f'== {self.name}')
        for st, t, h in self.rows:
            print(f'  {st:4} {t}' + (f'\n         -> {h}' if h else ''))
        print(f'  {self.name}: {"PASS" if self.ok else "FAIL — stop and do the missing work"}')
        return self.ok


def read(p):
    return Path(p).read_text(encoding='utf-8') if Path(p).is_file() else ''


def brief(work):
    out = {}
    for line in read(work / 'brief.md').splitlines():
        m = re.match(r'\s*-\s*([a-z_]+)\s*:\s*(.*)', line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def kind_of(work):
    k = brief(work).get('deliverable_kind', 'other').split()[0].lower() if brief(work).get('deliverable_kind') else 'other'
    return k if k in MIN else 'other'


def section(text, pattern):
    """Return the body of the first markdown heading matching pattern."""
    m = re.search(r'^#{1,4}[^\n]*(' + pattern + r')[^\n]*\n(.*?)(?=^#{1,4} |\Z)', text, re.I | re.M | re.S)
    return m.group(2) if m else None


def items(body):
    if not body:
        return []
    return [l for l in body.splitlines() if re.match(r'\s*([-*]|\d+\.|\|)\s*\S', l)
            and 'TODO' not in l and not re.match(r'\s*\|[-\s|]+\|\s*$', l) and not re.match(r'\s*\|\s*(file|#|fact)\s*\|', l, re.I)]


def table(text, need_cols):
    """Parse the first markdown table whose header contains all need_cols (case-insensitive)."""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.strip().startswith('|'):
            head = [c.strip().lower() for c in l.strip().strip('|').split('|')]
            if all(any(n in h for h in head) for n in need_cols):
                rows = []
                for r in lines[i + 2:]:
                    if not r.strip().startswith('|'):
                        break
                    cells = [c.strip() for c in r.strip().strip('|').split('|')]
                    rows.append(dict(zip(head, cells + [''] * (len(head) - len(cells)))))
                return head, rows
    return None, []


def col(row, name):
    for k, v in row.items():
        if name in k:
            return v
    return ''


def g0(work):
    g = Gate('GATE 0 brief')
    b = brief(work)
    g.need((work / 'brief.md').is_file(), 'brief.md exists', 'python gates.py init WORK, then fill brief.md')
    for k in ('topic', 'audience', 'deliverable_kind', 'talk_minutes', 'on_slide_language', 'honest_status', 'presenter'):
        v = b.get(k, '')
        g.need(v and not v.startswith('TODO'), f'brief: {k} = {v[:60]!r}', f'fill "{k}" (ask the user once; otherwise choose a default and record it)')
    quotes = section(read(work / 'brief.md'), "user's own words|verbatim")
    g.need(len(items(quotes)) >= 1, "brief: the user's verbatim quality words are recorded", 'paste the user\'s instructions word for word')
    try:
        float(re.findall(r'[\d.]+', b.get('talk_minutes', 'x'))[0])
    except (IndexError, ValueError):
        g.need(False, 'talk_minutes is a number', 'e.g. "talk_minutes: 6"')
    return g.report()


def g1(work):
    g = Gate('GATE 1 research')
    k = kind_of(work)
    m = MIN[k]
    facts = read(work / 'research/facts.md')
    ids = set(re.findall(r'^\s*[-*]?\s*\(([A-Z]{1,3}\d{1,3})\)[^\n]*https?://', facts, re.M))
    prefixes = set(re.findall(r'`?(\w+):`?\s*=\s*`?https?://', facts))  # e.g. GH: = https://github.com/.../blob/main/
    idref = re.compile(r'\((?:[^()]*\b)?(' + '|'.join(map(re.escape, ids)) + r')\b') if ids else None
    pref = re.compile(r'`?\b(' + '|'.join(map(re.escape, prefixes)) + r'):') if prefixes else None
    rows = []
    for l in facts.splitlines():
        st = l.strip()
        if not st.startswith(('-', '*', '|')) or 'TODO' in l or re.match(r'\s*[-*]?\s*\([A-Z]{1,3}\d{1,3}\)[^\n]*https?://', l):
            continue
        if URL.search(l) or (idref and idref.search(l)) or (pref and pref.search(l)):
            rows.append(l)
    tagged = [l for l in rows if TAG.search(l)]
    domains = {re.sub(r'^www\.', '', u.split('/')[2]) for u in URL.findall(facts)}
    g.need(len(rows) >= m['facts'], f'facts.md: {len(rows)} fact rows with a source URL (min {m["facts"]} for {k})',
           'research more: primary/official sources first (UNESCO dossier, museum, institute, repo/README/API)')
    g.need(len(tagged) >= 0.6 * max(1, len(rows)), f'facts.md: {len(tagged)}/{len(rows)} rows carry a verification tag',
           'tag every row: [verified] [secondary] [claim] [disputed] [uncertain]')
    g.need(len(domains) >= m['domains'], f'facts.md: {len(domains)} distinct source domains (min {m["domains"]})', 'cross-check with independent sources')
    dns = section(facts, r'do not|do-not|không được|overstate|pitfall|cạm bẫy|thổi phồng')
    g.need(len(items(dns)) >= 3, f'facts.md: do-not-say / pitfall list has {len(items(dns))} items (min 3)',
           'write what the deck must NOT claim (wins, rankings, "playable", wrong dates, wrong lists)')
    acc = read(work / 'research/accuracy.md')
    g.need(len(items(section(acc, r'true|đúng|use them'))) >= 3, 'accuracy.md: >= 3 TRUE motifs/objects with sources', 'list what really belongs to the subject')
    g.need(len(items(section(acc, r'wrong|sai|never use'))) >= 2, 'accuracy.md: >= 2 WRONG associations', 'list tempting but wrong symbols (generic national icons, neighbouring art forms, AI glow...)')
    g.need(len(items(section(acc, r'anatomy|giải phẫu'))) >= 1, 'accuracy.md: object anatomy checklist', 'counts, shapes, who holds what, brand rules')
    b = brief(work)
    if b.get('user_media', 'none').lower() not in ('', 'none', 'no'):
        g.need(len(items(section(acc, r'user media|media audit'))) >= 1, 'accuracy.md: user media audited (frame -> verdict -> reason)',
               'extract frames (video_frames.py), compare each with the true list, mark OK / keep small / never use')
    if b.get('reference_talk', 'none').lower() not in ('', 'none', 'no'):
        les = read(work / 'research/lessons.md')
        g.need(len([l for l in les.splitlines() if l.strip().startswith('-') and 'TODO' not in l]) >= 5,
               'lessons.md: >= 5 observed lessons from the reference talk', 'watch/transcribe the talk (yt-dlp + subtitles + frames)')
    return g.report()


def talk_minutes(work, default=6.0):
    try:
        return float(re.findall(r'[\d.]+', brief(work).get('talk_minutes', ''))[0])
    except IndexError:
        return default


def g2(work):
    g = Gate('GATE 2 assets')
    k = kind_of(work)
    m = dict(MIN[k])
    mins = talk_minutes(work)
    if mins < 5:  # short clips need fewer files; research depth (gate 1) is NOT scaled
        m['kept'] = max(4, math.ceil(m['kept'] * mins / 5))
        m['real'] = max(2, math.ceil(m['real'] * mins / 5))
        g.note(f'{mins:g}-min talk: asset minimums scaled to kept {m["kept"]}, real {m["real"]}')
    cr = read(work / 'assets/CREDITS.md')
    head, rows = table(cr, ['file', 'licence'])
    if head is None:
        head, rows = table(cr, ['file', 'license'])
    allrows = [r for r in rows if col(r, 'file') and 'TODO' not in col(r, 'file')]
    rows = [r for r in allrows if not col(r, 'file').strip('` ').startswith('_uncertain')]
    g.note(f'{len(allrows) - len(rows)} file(s) in _uncertain/ (not counted: atmosphere only, never captioned)')
    g.need(len(rows) >= m['kept'], f'CREDITS.md: {len(rows)} kept files (min {m["kept"]} for {k})',
           'search more (fetch_commons.py search, museum open access, the product repo/site/brand kit); keep only verified files')
    missing = [col(r, 'file') for r in allrows if not (work / 'assets' / col(r, 'file').strip('` ')).exists()]
    g.need(not missing, f'every CREDITS file exists on disk ({len(missing)} missing)', f'missing: {missing[:6]}')
    nolic = [col(r, 'file') for r in rows if not LIC.search(col(r, 'licence') + col(r, 'license'))]
    nourl = [col(r, 'file') for r in rows if not URL.search(' '.join(r.values()))]
    g.need(not nolic, f'every row has a licence ({len(nolic)} without)', f'{nolic[:6]}')
    g.need(not nourl, f'every row has a source URL ({len(nourl)} without)', f'{nourl[:6]}')
    why = [col(r, 'file') for r in rows if len(col(r, 'why')) < 8]
    g.need(not why, f'every row says WHY it is accurate ({len(why)} without)', 'cite the fact-file ID that the image matches')
    cand_dir = work / 'assets/candidates'
    n_cand = len([p for p in cand_dir.rglob('*') if p.suffix.lower() in IMG and not p.name.startswith('contact')]) if cand_dir.is_dir() else 0
    need_c = 2 * len(rows) if k != 'product' else len(rows)
    g.need(n_cand >= need_c, f'{n_cand} candidates looked at (min {need_c})', 'run more searches (local language AND English, with and without diacritics)')
    kept_files = [p for p in (work / 'assets').iterdir() if p.suffix.lower() in IMG and not p.name.startswith('contact')] if (work / 'assets').is_dir() else []
    sheets = sorted((work / 'assets').glob('contact*.jpg'))
    newest = max((p.stat().st_mtime for p in kept_files), default=0)
    g.need(sheets and sheets[-1].stat().st_mtime >= newest, 'assets/contact*.jpg of the KEPT set exists and is newer than every kept file',
           'python contact_sheet.py WORK/assets --out WORK/assets/contact.jpg — then LOOK at it against accuracy.md')
    rej = section(cr, r'reject|loại')
    if k == 'heritage':
        g.need(len(items(rej)) >= 1, f'CREDITS.md lists rejected candidates ({len(items(rej))})', 'write which candidates you rejected and why (wrong instrument, unverified place, NC licence)')
    real = [r for r in rows if not re.search(r'drawn|vẽ|generated|texture', ' '.join(r.values()), re.I)]
    g.need(len(real) >= m['real'], f'{len(real)} real photos/screens/brand files (min {m["real"]})', 'decorations do not replace real imagery of the subject')
    return g.report()


def g3(work):
    g = Gate('GATE 3 design')
    ad = read(work / 'design/art-direction.md')
    g.need(bool(ad), 'design/art-direction.md exists')
    fonts = [p for p in (work / 'fonts').glob('*') if p.suffix.lower() in ('.ttf', '.otf')] if (work / 'fonts').is_dir() else []
    lic = [p for p in (work / 'fonts').glob('*') if re.search(r'ofl|licen[cs]e', p.name, re.I)] if (work / 'fonts').is_dir() else []
    g.need(len(fonts) >= 2, f'fonts/: {len(fonts)} font files (min 2)', 'download the chosen OFL fonts (static TTFs) into WORK/fonts')
    g.need(bool(lic), 'fonts/: licence file present (OFL.txt)')
    fc = read(work / 'design/font-check.txt')
    g.need('PASS' in fc and 'FAIL' not in fc, 'design/font-check.txt: all fonts PASS the glyph check',
           'python check_fonts.py WORK/fonts/*.ttf --lang vi --png WORK/design/font-sample.png > WORK/design/font-check.txt')
    g.need(len(set(re.findall(r'#[0-9A-Fa-f]{6}\b', ad))) >= 3, 'art-direction: >= 3 palette hex codes with a source')
    g.need(len(items(section(ad, r'motif|texture'))) >= 3, 'art-direction: >= 3 motifs/textures (each on the TRUE list)')
    g.need(len(items(section(ad, r'layered|layer'))) >= 1, 'art-direction: layered objects for Morph are planned')
    samples = list((work / 'design/samples').glob('*.jpg')) + list((work / 'design/samples').glob('*.png'))
    g.need(len(samples) >= 2, f'design/samples: {len(samples)} rendered samples (min 2: title + body)', 'render the family deck and copy title + body renders here')
    return g.report()


def g4(work):
    g = Gate('GATE 4 storyboard')
    sb = read(work / 'storyboard.md')
    head, rows = table(sb, ['#', 'scene', 'layers', 'visual', 'words'])
    g.need(head is not None, 'storyboard.md has the slide table (# | scene | ... | layers | visual | ... | words)', 'copy the template table')
    rows = [r for r in rows if col(r, '#').strip().isdigit()]
    scenes = {}
    for r in rows:
        scenes.setdefault(re.split(r'\s', col(r, 'scene').strip() or '?')[0], []).append(r)
    try:
        mins = float(re.findall(r'[\d.]+', brief(work).get('talk_minutes', ''))[0])
    except IndexError:
        mins = 6
    min_sc = min(8, max(2, round(1.5 * mins)))
    g.need(len(scenes) >= min_sc, f'{len(scenes)} scenes (min {min_sc} for {mins:g} min)', 'a pitch of 5-12 min needs 8-15 scenes')
    runs = [s for s, rs in scenes.items() if len(rs) >= 3]
    avg = len(rows) / max(1, len(scenes))
    g.need(len(runs) >= 0.6 * max(1, len(scenes)), f'{len(runs)}/{len(scenes)} scenes are keyframe runs of >= 3 slides',
           '"nhiều slide để phục vụ cho một motion hoàn chỉnh": split each scene into 3-5 keyframe slides')
    g.note(f'{len(rows)} slides, {avg:.1f} slides per scene')
    nolayer = [col(r, '#') for r in rows if '!!' not in col(r, 'layers')]
    g.need(len(nolayer) <= 0.1 * max(1, len(rows)), f'rows without !! layers: {len(nolayer)}', f'rows {nolayer[:10]}: name the persistent layers that move')
    bad_vis = []
    for r in rows:
        v = col(r, 'visual').strip()
        if not v or 'TODO' in v or v in ('-', '—'):
            bad_vis.append(col(r, '#'))
            continue
        for f in re.findall(r'[\w./-]+\.(?:jpg|jpeg|png|webp)', v, re.I):
            f = re.sub(r'^(frame|drawn):', '', f)
            if not any((work / d / f).exists() or (work / d / Path(f).name).exists() for d in ('assets', 'design', 'assets/frames', 'media', '.')):
                bad_vis.append(f'{col(r, "#")}:{f}?')
    g.need(not bad_vis, f'every slide has a real visual ({len(bad_vis)} problems)', f'{bad_vis[:10]} — name a kept asset, drawn:<motif> or frame:<file>')
    words = []
    for r in rows:
        try:
            words.append(int(re.findall(r'\d+', col(r, 'words'))[0]))
        except IndexError:
            words.append(None)
    g.need(None not in words, 'every row has a words budget', 'fill the words column (0 is allowed for silent keyframes)')
    b = brief(work)
    try:
        minutes = float(re.findall(r'[\d.]+', b.get('talk_minutes', ''))[0])
        budget = int(minutes * 130 - 2 * 6 / 60 * 130)
        tot = sum(w for w in words if w)
        g.need(tot <= budget, f'words budget {tot} <= {budget} ({minutes:g} min at 130 wpm)', 'cut words now, not after the script is written')
    except IndexError:
        g.need(False, 'talk_minutes known (brief.md)')
    am = re.search(r'anchor\s*:\s*["“]([^"”]+)["”]', sb, re.I)
    if g.need(bool(am) and 'TODO' not in am.group(1), 'anchor phrase declared (anchor: "...")', 'one short sentence the audience will repeat'):
        n = sum(1 for r in rows if am.group(1).lower() in ' '.join(r.values()).lower())
        g.need(n >= 3, f'anchor phrase appears on {n} slides (min 3: setup / middle / end)')
    g.need(re.search(r'colou?r arc\s*:\s*(?!TODO)\S', sb, re.I) is not None, 'colour arc declared')
    g.need(re.search(r'circular close\s*:\s*(?!TODO)\S', sb, re.I) is not None, 'circular close declared')
    g.need((work / 'motion.json').is_file(), 'motion.json exists (durations keyed by slide FILE number)')
    return g.report()


def run_check_deck(deck, extra):
    cmd = [sys.executable, str(HERE / 'check_deck.py'), str(deck)] + extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if l.startswith(('ERROR', 'RESULT'))]
    return r.returncode == 0, tail


def g5(work, group, deck):
    g = Gate(f'GATE 5 group {group}')
    rdirs = sorted((work / 'renders').glob(f'{group}-*')) if (work / 'renders').is_dir() else []
    g.need(bool(rdirs) and any(rdirs[-1].glob('contact*.jpg')), f'renders/{group}-N/contact*.jpg exists', 'render.sh preview.pptx WORK/renders/<group>-<N>, then LOOK')
    g.need((work / 'notes' / f'{group}.md').is_file(), f'notes/{group}.md written (what changed, layers, sources, defects left)')
    if deck:
        ok, tail = run_check_deck(deck, [])
        g.need(ok, f'check_deck.py {Path(deck).name}: ' + (tail[-1] if tail else ''), '; '.join(tail[:6]))
    else:
        g.need(False, 'pass --deck WORK/deck/preview-<group>.pptx')
    return g.report()


def g6(work):
    g = Gate('GATE 6 final')
    d = work / 'deliver'
    pp = sorted(d.glob('*.pptx')) if d.is_dir() else []
    g.need(len(pp) == 1, f'deliver/: one .pptx ({len(pp)})')
    g.need(bool(list(d.glob('*.docx'))) if d.is_dir() else False, 'deliver/: speaker script .docx')
    g.need(bool(list((d / 'fonts').glob('*.ttf')) + list((d / 'fonts').glob('*.otf'))) if (d / 'fonts').is_dir() else False, 'deliver/fonts/ with the font files + licence + install README')
    g.need(bool(list(d.glob('*.zip'))) if d.is_dir() else False, 'deliver/: zip of pptx + docx + fonts')
    g.need(bool(list(d.glob('CREDITS*'))) if d.is_dir() else False, 'deliver/: CREDITS file')
    b = brief(work)
    if pp:
        anchor = re.search(r'anchor\s*:\s*["“]([^"”]+)["”]', read(work / 'storyboard.md'), re.I)
        extra = ['--max-mb', re.findall(r'[\d.]+', b.get('max_deck_mb', '25'))[0] if re.findall(r'[\d.]+', b.get('max_deck_mb', '25')) else '25']
        if anchor:
            extra += ['--anchor', anchor.group(1)]
        ok, tail = run_check_deck(pp[0], extra)
        g.need(ok, 'check_deck.py: ' + (tail[-1] if tail else ''), '; '.join(tail[:6]))
        target = b.get('talk_minutes', '')
        r = subprocess.run([sys.executable, str(HERE / 'words_budget.py'), 'measure', str(pp[0]), '--target', target or '99'],
                           capture_output=True, text=True)
        est = [l for l in r.stdout.splitlines() if l.startswith(('estimate', 'target'))]
        accepted = b.get('time_overrun_accepted', 'no').lower().startswith('y')
        g.need(r.returncode == 0 or accepted, 'speaking time: ' + ' | '.join(est), 'trim the notes (heaviest slides first) or get the user to accept the overrun')
    finals = sorted((work / 'renders').glob('final*')) if (work / 'renders').is_dir() else []
    g.need(bool(finals) and any(finals[-1].glob('contact*.jpg')), 'renders/final-N/contact*.jpg of the delivered deck (looked at)')
    return g.report()


def cmd_init(work, kind):
    work.mkdir(parents=True, exist_ok=True)
    for d in ('research', 'assets/candidates', 'assets/_uncertain', 'design/samples', 'fonts', 'deck', 'renders', 'notes', 'deliver', 'media_orig'):
        (work / d).mkdir(parents=True, exist_ok=True)
    plan = {'brief.md': 'brief.md', 'facts.md': 'research/facts.md', 'accuracy.md': 'research/accuracy.md', 'lessons.md': 'research/lessons.md',
            'CREDITS.md': 'assets/CREDITS.md', 'art-direction.md': 'design/art-direction.md', 'storyboard.md': 'storyboard.md', 'motion.json': 'motion.json'}
    for src, dst in plan.items():
        if not (work / dst).exists():
            shutil.copy(TEMPLATES / src, work / dst)
    b = (work / 'brief.md').read_text(encoding='utf-8')
    if kind:
        b = b.replace('- deliverable_kind: TODO (heritage | product | other)', f'- deliverable_kind: {kind}')
        (work / 'brief.md').write_text(b, encoding='utf-8')
    print('initialised', work)
    for p in sorted(work.rglob('*')):
        print('  ', p.relative_to(work))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init'); s.add_argument('work'); s.add_argument('--kind', choices=('heritage', 'product', 'other'))
    s = sub.add_parser('check'); s.add_argument('work'); s.add_argument('--gate', type=int); s.add_argument('--upto', type=int)
    s.add_argument('--group'); s.add_argument('--deck')
    a = ap.parse_args(argv)
    work = Path(a.work).resolve()
    if a.cmd == 'init':
        return cmd_init(work, a.kind)
    gates = list(range(0, a.upto + 1)) if a.upto is not None else [a.gate if a.gate is not None else 0]
    fns = {0: g0, 1: g1, 2: g2, 3: g3, 4: g4, 6: g6}
    ok = True
    for n in gates:
        if n == 5:
            if not a.group:
                print('== GATE 5 needs --group gN --deck preview.pptx (skipped in --upto)') if a.upto is not None else None
                if a.upto is None:
                    ok = False
                continue
            res = g5(work, a.group, a.deck)
        else:
            res = fns[n](work)
        ok &= res
        with (work / 'gates.log').open('a', encoding='utf-8') as f:
            f.write(f'{datetime.datetime.now().isoformat(timespec="seconds")} gate {n}{" " + a.group if n == 5 and a.group else ""}: {"PASS" if res else "FAIL"}\n')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
