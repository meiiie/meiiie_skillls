"""Gates for the motion-pptx-studio pipeline (v5.5).

  python3 gates.py init WORK [--kind heritage|product|pitch|business|company-profile|education|event|other]
  python3 gates.py check WORK --gate N                          check gate N (0..6); exit 1 on FAIL
  python3 gates.py check WORK --upto N                          gates 0..N; gate 5 runs for every group
                                                                 that has renders/<group>-N and deck/preview-<group>.pptx
  python3 gates.py check WORK --gate 5 --group g3 --deck WORK/deck/preview-g3.pptx
  python3 gates.py check WORK --gate 5 --group all              v5.4: the whole deck (deck/preview-all.pptx from
                                                                 studio.py build WORK); --upto 5+ runs it too
  --stop-on-fail (with --upto) stops at the first failing gate; --upto always ends with a SUMMARY line

Two kinds of row (v5.3):
  FAIL  hard: facts (every fact row sourced, numbers on slides trace to a fact ID), licences (every
        image credited, AI images labelled), render integrity (fonts pass, renders exist, check_deck
        passes, the signature films exist, move and are embedded) and the creative floor
        (3 art directions sketched, >= 2 signature moments, style shifts on 20+ slides).
  WARN  advisory: counts and thresholds (fact counts, domains, kept/candidate counts, scene counts,
        keyframe runs, word averages, anchor, colour arc, samples, compare). They are good habits that
        reproduced the reference decks, not a quality bar; a WARN never stops the pipeline.

Gates
  0 brief      brief.md complete (audience, minutes, language, honest status, the user's verbatim words)
  1 research   research/facts.md: every fact row has a source; a do-not-say list (not counted as facts)
  2 assets     assets/CREDITS.md: every image under assets/ and assets/gen/ has a row with licence, source
               and why; AI-generated files carry "AI-generated" and their .json sidecar
  3 design     v5.5 routing: design/routing.json exists (route.py analysed subject, audience, tone and the
               real pictures), a direction was chosen, >= 1 mismatched direction rejected with a reason, and
               the deck's style family is not a rejected one (FAIL); routing current and fit >= 0.60 (WARN).
               art-direction.md with a style (genome.py compile writes it); design/directions.md +
               directions.jpg (3 different art directions, one chosen and why); fonts/ with licence and
               font-check PASS
  4 storyboard storyboard table parses (malformed rows fail loudly); a real visual per row; numbers trace
               to fact IDs; design/signature-moments.md (>= 2 hand-built moments: anatomy / manim);
               decks of 20+ slides change style at least once
  5 group      renders/<group>-N (numerically latest) with a contact sheet; check_deck passes (size is a
               warning above 80% of the limit, the hard limit is at gate 6); legibility (caps body FAIL,
               text on photo without scrim WARN, FAIL in heritage-collage)
    whole deck deck/preview-all.pptx is current and complete; check_deck on all slides (deck-wide geometry,
               image reuse, variety) passes
  6 final      deliver/ has pptx + docx + fonts/ + zip + CREDITS; check_deck passes; renders/final-N; the
               signature films are embedded in the pptx and move
The skill is a floor, not a ceiling (SKILL.md): pass the gates, then go past them.
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
from visual_audit import (  # noqa: E402
    FACT_SLIDE_MIN, OFFICE_DEFAULTS, SUBJECT_REUSE_MAX, WORDS_AVG_MIN,
    cites_fact, colour_arc_ok, fact_ids, font_family_from_file, palette_report,
    storyboard_density_errors, storyboard_layout_errors, storyboard_visual_errors, visual_keys,
)
URL = re.compile(r'https?://[^\s)|>\]]+')
TAG = re.compile(r'\[(verified|secondary|claim|disputed|uncertain|claim-in-README|verified-in-[\w-]+|ĐÃ XÁC MINH[^\]]*|THỨ CẤP|TRANH CÃI|CHƯA RÕ|CHƯA XÁC MINH)\]', re.I)
LIC = re.compile(r'CC[ -]?0|CC[ -]BY|public domain|PD|PDM|own work|owner|trademark|official|team|user|drawn|CC BY', re.I)
IMG = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
MIN = {  # research depth and imagery scale with the kind of deck (references/genres.md)
    'heritage': {'facts': 15, 'domains': 3, 'kept': 12, 'real': 6},
    'product': {'facts': 12, 'domains': 2, 'kept': 6, 'real': 1},
    'pitch': {'facts': 12, 'domains': 3, 'kept': 6, 'real': 1},
    'business': {'facts': 10, 'domains': 2, 'kept': 4, 'real': 0},
    'company-profile': {'facts': 15, 'domains': 3, 'kept': 8, 'real': 3},
    'education': {'facts': 12, 'domains': 3, 'kept': 8, 'real': 3},
    'event': {'facts': 6, 'domains': 2, 'kept': 6, 'real': 2},
    'other': {'facts': 10, 'domains': 2, 'kept': 6, 'real': 2},
}
ANATOMY_KINDS = ('heritage', 'product', 'education')


class Gate:
    def __init__(self, name):
        self.name, self.rows, self.ok = name, [], True

    def need(self, cond, text, hint=''):
        self.rows.append(('PASS' if cond else 'FAIL', text, '' if cond else hint))
        self.ok &= bool(cond)
        return cond

    def want(self, cond, text, hint=''):
        """Advisory: printed as WARN, never fails the gate."""
        self.rows.append(('PASS' if cond else 'WARN', text, '' if cond else hint))
        return cond

    def note(self, text):
        self.rows.append(('INFO', text, ''))

    def report(self):
        print(f'== {self.name}')
        for st, t, h in self.rows:
            print(f'  {st:4} {t}' + (f'\n         -> {h}' if h else ''))
        n_warn = sum(1 for r in self.rows if r[0] == 'WARN')
        print(f'  {self.name}: {"PASS" if self.ok else "FAIL — stop and do the missing work"}'
              + (f' ({n_warn} advisory warning(s))' if n_warn else ''))
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


def section(text, pattern, start=False):
    """Return the body of the first markdown heading matching pattern.

    start=True (v5.4): the heading must BEGIN with the pattern (after '#', numbering and punctuation), so
    "## Signature (one motif)" is not taken for "## Motifs and textures"."""
    lead = r'^#{1,4}\s*(?:[\d.]+\s*)?[^\w\n]*(' if start else r'^#{1,4}[^\n]*('
    m = re.search(lead + pattern + r')[^\n]*\n(.*?)(?=^#{1,4} |\Z)', text, re.I | re.M | re.S)
    return m.group(2) if m else None


NEGATION = re.compile(r"\b(?:never|no|not|avoid|without|don't|do not|nor|instead of|không|tránh|đừng|chẳng|cấm)\b[^.;:\n]*", re.I)


def strip_negated(text):
    """Drop clauses that start with a negation ("never fly", "no zoom, no spin") before counting vocabulary."""
    return NEGATION.sub(' ', text)


def items(body):
    if not body:
        return []
    return [l for l in body.splitlines() if re.match(r'\s*([-*]|\d+\.|\|)\s*\S', l)
            and 'TODO' not in l and not re.match(r'\s*\|[-\s|]+\|\s*$', l) and not re.match(r'\s*\|\s*(file|#|fact)\s*\|', l, re.I)]


class Rows(list):
    """Table rows; .bad lists malformed lines (wrong cell count, a row broken across lines)."""
    bad = ()


def _cells(line):
    body = line.strip()
    body = body[1:] if body.startswith('|') else body
    body = body[:-1] if body.endswith('|') and not body.endswith('\\|') else body
    return [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', body)]


def table(text, need_cols):
    """Parse the first markdown table whose header contains all need_cols (case-insensitive).

    v5.3: a row with the wrong number of cells, or a row broken across lines by a newline inside a
    cell, is reported in rows.bad (gate 4 fails on it) instead of silently ending the table."""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.strip().startswith('|'):
            head = [c.lower() for c in _cells(l)]
            if all(any(n in h for h in head) for n in need_cols):
                rows, bad = Rows(), []
                j = i + 2
                while j < len(lines):
                    r = lines[j]
                    if not r.strip().startswith('|'):
                        # a newline inside a cell: the table resumes within a few lines
                        nxt = next((k for k in range(j + 1, min(j + 4, len(lines))) if lines[k].strip().startswith('|')), None)
                        if r.strip() and nxt is not None:
                            bad.append(f'line {j + 1}: row broken across lines ({r.strip()[:50]!r}); keep each row on one line')
                            j = nxt
                            continue
                        break
                    cells = _cells(r)
                    if len(cells) != len(head):
                        bad.append(f'line {j + 1}: {len(cells)} cells, header has {len(head)} ({r.strip()[:50]!r}); '
                                   'escape a literal | as \\|')
                    rows.append(dict(zip(head, cells + [''] * (len(head) - len(cells)))))
                    j += 1
                rows.bad = bad
                return head, rows
    return None, Rows()


def col(row, name):
    for k, v in row.items():
        if name in k:
            return v
    return ''


def g0(work):
    g = Gate('GATE 0 brief')
    b = brief(work)
    g.need((work / 'brief.md').is_file(), 'brief.md exists', 'python3 gates.py init WORK, then fill brief.md')
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


FACT_TABLE_ROW = re.compile(r'^\s*\|\s*`?F?\d+(?:\.\d+)*[a-z]?`?\s*\|')


def g1(work):
    g = Gate('GATE 1 research')
    k = kind_of(work)
    m = MIN[k]
    facts = read(work / 'research/facts.md')
    g.need(bool(facts.strip()), 'research/facts.md exists', 'python3 gates.py init WORK, then research (references/research-protocol.md)')
    ids = set(re.findall(r'^\s*[-*]?\s*\(([A-Z]{1,3}\d{1,3})\)[^\n]*https?://', facts, re.M))
    prefixes = set(re.findall(r'`?(\w+):`?\s*=\s*`?https?://', facts))  # e.g. GH: = https://github.com/.../blob/main/
    idref = re.compile(r'\((?:[^()]*\b)?(' + '|'.join(map(re.escape, ids)) + r')\b|\b(' + '|'.join(map(re.escape, ids)) + r')\b') if ids else None
    pref = re.compile(r'`?\b(' + '|'.join(map(re.escape, prefixes)) + r'):') if prefixes else None
    # v5.3: the do-not-say / pitfall list is NOT a fact list, even when its lines carry URLs
    dns = section(facts, r'do not|do-not|không được|overstate|pitfall|cạm bẫy|thổi phồng')
    dns_lines = set(l.strip() for l in (dns or '').splitlines() if l.strip())
    rows, unsourced = [], []
    for l in facts.splitlines():
        st = l.strip()
        if not st.startswith(('-', '*', '|')) or 'TODO' in l or st in dns_lines \
                or re.match(r'\s*[-*]?\s*\([A-Z]{1,3}\d{1,3}\)[^\n]*https?://', l):
            continue
        sourced = URL.search(l) or (idref and idref.search(l)) or (pref and pref.search(l))
        if sourced:
            rows.append(l)
        elif FACT_TABLE_ROW.match(l):
            unsourced.append(st[:60])
    g.need(bool(rows), f'facts.md: {len(rows)} sourced fact rows (do-not-say list not counted)', 'every claim needs a source URL or a source ID (S1) defined with its URL')
    g.need(not unsourced, f'facts.md: every fact table row has a source ({len(unsourced)} without)',
           f'{unsourced[:4]} — add the URL or source ID, or move the row to the Gaps section')
    tagged = [l for l in rows if TAG.search(l)]
    domains = {re.sub(r'^www\.', '', u.split('/')[2]) for u in URL.findall(facts)}
    g.want(len(rows) >= m['facts'], f'facts.md: {len(rows)} fact rows (habit: {m["facts"]}+ for {k})',
           'research more: primary/official sources first (filings, dossier, museum, repo/README/API)')
    g.want(len(tagged) >= 0.6 * max(1, len(rows)), f'facts.md: {len(tagged)}/{len(rows)} rows carry a verification tag',
           'tag rows: [verified] [secondary] [claim] [disputed] [uncertain]')
    g.want(len(domains) >= m['domains'], f'facts.md: {len(domains)} distinct source domains (habit: {m["domains"]}+)', 'cross-check with independent sources')
    g.need(len(items(dns)) >= 1, f'facts.md: a do-not-say / pitfall list ({len(items(dns))} items)',
           'write what the deck must NOT claim (wins, rankings, wrong dates, company claims stated as fact)')
    g.want(len(items(dns)) >= 3, f'facts.md: do-not-say list has {len(items(dns))} items (habit: 3+)')
    acc = read(work / 'research/accuracy.md')
    true_n, wrong_n = len(items(section(acc, r'true|đúng|use them'))), len(items(section(acc, r'wrong|sai|never use')))
    (g.need if k == 'heritage' else g.want)(true_n >= 3, f'accuracy.md: {true_n} TRUE motifs/objects with sources (3+)', 'list what really belongs to the subject')
    (g.need if k == 'heritage' else g.want)(wrong_n >= 2, f'accuracy.md: {wrong_n} WRONG associations (2+)', 'list tempting but wrong symbols (generic national icons, AI glow, clichés)')
    if k in ANATOMY_KINDS:
        g.want(len(items(section(acc, r'anatomy|giải phẫu'))) >= 1, 'accuracy.md: object anatomy checklist', 'counts, shapes, who holds what, brand rules')
    b = brief(work)
    if b.get('user_media', 'none').lower() not in ('', 'none', 'no'):
        g.need(len(items(section(acc, r'user media|media audit'))) >= 1, 'accuracy.md: user media audited (frame -> verdict -> reason)',
               'extract frames (video_frames.py), compare each with the true list, mark OK / keep small / never use')
    if b.get('reference_talk', 'none').lower() not in ('', 'none', 'no'):
        les = read(work / 'research/lessons.md')
        g.want(len([l for l in les.splitlines() if l.strip().startswith('-') and 'TODO' not in l]) >= 5,
               'lessons.md: >= 5 observed lessons from the reference talk', 'watch/transcribe the talk (yt-dlp + subtitles + frames)')
    return g.report()


def asset_scarcity(work):
    """A reason means the subject has no openly licensed imagery.

    `no`, `none`, or `no (a parenthetical)` stay off. A sentence that merely starts with
    "no", such as "no openly licensed screenshots exist", is a reason and stays on.
    """
    v = brief(work).get('asset_scarcity', 'no').strip()
    core = re.sub(r'\s*\(.*\)\s*$', '', v).strip()
    low = core.lower()
    if not core or low in ('no', 'none', 'false', 'n', 'todo') or low.startswith('todo'):
        return None
    return core


def storyboard_filled(rows):
    """The init template is one example row (drawn:string). That is not a storyboard yet."""
    if len(rows) < 3:
        visuals = ' '.join(col(r, 'visual') for r in rows)
        if 'TODO' in visuals or visuals.strip() in ('', 'drawn:string') or len(rows) <= 1:
            return False
    return len(rows) >= 3


def talk_minutes(work, default=6.0):
    try:
        return float(re.findall(r'[\d.]+', brief(work).get('talk_minutes', ''))[0])
    except IndexError:
        return default


AI_LABEL = re.compile(r'AI[- ]generated|AI-gen|tạo bằng AI', re.I)


def asset_files(work):
    """Images that can land on a slide: assets/*.ext and assets/gen/*.ext (not candidates, contact sheets, _uncertain)."""
    out = []
    for d in (work / 'assets', work / 'assets' / 'gen'):
        if d.is_dir():
            out += [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in IMG and not p.name.startswith('contact')]
    return out


def contact_fresh(work, kept_files):
    """(ok, why). v5.3: compare the sheet's manifest with the files instead of trusting mtimes."""
    sheets = sorted((work / 'assets').glob('contact*.jpg'))
    if not sheets:
        return False, 'no assets/contact*.jpg'
    names = {}
    for man in (work / 'assets').glob('contact*.json'):
        try:
            for r in json.loads(man.read_text(encoding='utf-8')).get('files', []):
                names[r['name']] = r.get('bytes')
        except (ValueError, KeyError, TypeError):
            continue
    top = [p for p in kept_files if p.parent == work / 'assets']
    if names:
        missing = [p.name for p in top if p.name not in names]
        changed = [p.name for p in top if p.name in names and names[p.name] not in (None, p.stat().st_size)]
        if missing or changed:
            return False, f'sheet is stale: not on it {missing[:5]}, changed since {changed[:5]}'
        return True, f'manifest lists all {len(top)} kept files'
    newest = max((p.stat().st_mtime for p in top), default=0)
    return sheets[-1].stat().st_mtime >= newest, 'no manifest (pre-5.3 sheet): compared file times'


def rows_outside_table(text, head, names):
    """'line N: file' for lines of CREDITS.md that name an uncredited file: the row exists but the table parser
    never reached it (a blank line, heading or list ends a markdown table)."""
    out = []
    for i, l in enumerate(text.splitlines()):
        for n in names:
            if Path(n).name in l:
                out.append(f'line {i + 1}: {Path(n).name}')
                break
    return out


def g2(work):
    g = Gate('GATE 2 assets')
    k = kind_of(work)
    m = dict(MIN[k])
    mins = talk_minutes(work)
    if mins < 5:  # short clips need fewer files; research depth (gate 1) is NOT scaled
        m['kept'] = max(4, math.ceil(m['kept'] * mins / 5))
        m['real'] = max(2, math.ceil(m['real'] * mins / 5))
        g.note(f'{mins:g}-min talk: asset habits scaled to kept {m["kept"]}, real {m["real"]}')
    cr = read(work / 'assets/CREDITS.md')
    g.need(bool(cr), 'assets/CREDITS.md exists')
    head, rows = table(cr, ['file', 'licence'])
    if head is None:
        head, rows = table(cr, ['file', 'license'])
    for b in getattr(rows, 'bad', ()):
        g.need(False, f'CREDITS.md table: {b}', 'one row per line, a cell per column')
    allrows = [r for r in rows if col(r, 'file') and 'TODO' not in col(r, 'file')]
    rows = [r for r in allrows if not col(r, 'file').strip('` ').startswith('_uncertain')]
    g.note(f'{len(allrows) - len(rows)} file(s) in _uncertain/ (not counted: atmosphere only, never captioned)')
    g.want(len(rows) >= m['kept'], f'CREDITS.md: {len(rows)} kept files (habit: {m["kept"]}+ for {k})',
           'search more (fetch_commons.py search, museum open access, brand kit), or make own assets (gen_assets_codex.py, make_assets.py)')
    fname = lambda r: col(r, 'file').strip('` ')
    missing = [fname(r) for r in allrows if not (work / 'assets' / fname(r)).exists()]
    g.need(not missing, f'every CREDITS file exists on disk ({len(missing)} missing)', f'missing: {missing[:6]}')
    nolic = [fname(r) for r in rows if not (LIC.search(col(r, 'licence') + col(r, 'license')) or AI_LABEL.search(col(r, 'licence') + col(r, 'license')))]
    ai_rows = [r for r in rows if AI_LABEL.search(' '.join(r.values()))]
    nourl = [fname(r) for r in rows if r not in ai_rows and not URL.search(' '.join(r.values()))]
    g.need(not nolic, f'every row has a licence ({len(nolic)} without)', f'{nolic[:6]}')
    g.need(not nourl, f'every row has a source URL ({len(nourl)} without; AI-generated rows use their sidecar instead)', f'{nourl[:6]}')
    why = [fname(r) for r in rows if len(col(r, 'why')) < 8]
    g.need(not why, f'every row says WHY it is accurate / what it is for ({len(why)} without)', 'cite the fact ID it matches, or say "ground texture, no claim"')
    # v5.3 licence integrity: nothing reaches a slide without a row
    credited = {Path(fname(r)).name for r in allrows} | {fname(r) for r in allrows}
    kept_files = asset_files(work)
    uncredited = [str(p.relative_to(work / 'assets')) for p in kept_files
                  if p.name not in credited and str(p.relative_to(work / 'assets')) not in credited]
    outside = rows_outside_table(cr, head, uncredited)
    g.need(not uncredited, f'every image in assets/ and assets/gen/ has a CREDITS row ({len(uncredited)} without)',
           (f'{outside[:4]} — these rows sit OUTSIDE the credits table (a non-table line such as a list or a blank '
            'line ends a markdown table): move them up into the table' if outside else
            f'{uncredited[:6]} — add a row, or move the file to assets/candidates/'))
    gen = [p for p in kept_files if p.parent.name == 'gen']
    unlabelled = [p.name for p in gen if not any(AI_LABEL.search(' '.join(r.values())) for r in allrows if Path(fname(r)).name == p.name)]
    nosidecar = [p.name for p in gen if not p.with_suffix('.json').is_file()]
    if gen:
        g.need(not unlabelled, f'assets/gen: {len(gen)} AI-generated file(s), every row labelled "AI-generated" ({len(unlabelled)} not)', f'{unlabelled[:6]}')
        g.need(not nosidecar, f'assets/gen: every file has its .json sidecar (prompt, model, session) ({len(nosidecar)} without)', f'{nosidecar[:6]}')
    cand_dir = work / 'assets/candidates'
    n_cand = len([p for p in cand_dir.rglob('*') if p.suffix.lower() in IMG and not p.name.startswith('contact')]) if cand_dir.is_dir() else 0
    sourced = [r for r in rows if r not in ai_rows]
    need_c = 2 * len(sourced)   # v5.3: one rule for every kind, advisory
    g.want(n_cand >= need_c, f'{n_cand} candidates looked at for {len(sourced)} sourced files (habit: 2x = {need_c})',
           'run more searches (local language AND English, with and without diacritics)')
    ok, why_c = contact_fresh(work, kept_files)
    g.want(ok, f'assets/contact*.jpg shows the current kept set ({why_c})',
           'python3 contact_sheet.py WORK/assets WORK/assets/gen --out WORK/assets/contact.jpg — then LOOK at it against accuracy.md')
    rej = section(cr, r'reject|loại')
    if k == 'heritage':
        g.want(len(items(rej)) >= 1, f'CREDITS.md lists rejected candidates ({len(items(rej))})', 'write which candidates you rejected and why')
    scarce = asset_scarcity(work)
    if scarce:
        m['real'] = 0
        g.note(f'asset_scarcity: {scarce[:90]} — real-photo habit is 0. Illustrations still need a CREDITS row '
               f'(licence drawn / own work / AI-generated) and must be labelled as illustrations.')
    real = [r for r in rows if not NOT_REAL.search(' '.join(r.values())) and not AI_WORD.search(' '.join(r.values()))]
    g.want(len(real) >= m['real'], f'{len(real)} real photos/screens/brand files (habit: {m["real"]}+)', 'decorations do not replace real imagery of the subject')
    sb_head, sb_rows = table(read(work / 'storyboard.md'), ['#', 'scene', 'visual'])
    sb_rows = [r for r in sb_rows if col(r, '#').strip().isdigit()]
    if storyboard_filled(sb_rows):
        for e in storyboard_visual_errors(sb_rows, col):
            g.want(False, 'storyboard visuals: ' + e, 'name a different kept file or drawn:<motif> per scene')
    return g.report()


HEX6 = re.compile(r'#[0-9A-Fa-f]{6}\b')
# v5.4: whole words only ("domain", "train", "aperture" are real photos); "AI" only in capitals
NOT_REAL = re.compile(r'\b(?:drawn|vẽ|generated|textures?|illustrations?|minh họa|own work: ground|procedural)\b', re.I)
AI_WORD = re.compile(r'(?<![A-Za-z])AI(?![a-z])|AI-generated')


def directions_report(work):
    """design/directions.md: >= 3 '## Direction ...' sections, a chosen one and why. Returns (errors, info)."""
    txt = read(work / 'design/directions.md')
    errs = []
    if not txt:
        return ['design/directions.md missing'], []
    secs = re.findall(r'^#{2,3}\s*(?:direction|hướng)\s*([^\n]*)\n(.*?)(?=^#{1,3} |\Z)', txt, re.I | re.M | re.S)
    secs = [(n.strip(), b) for n, b in secs if 'TODO' not in n + b]
    if len(secs) < 3:
        errs.append(f'{len(secs)} direction section(s) filled ("## Direction A — name"; need 3)')
    pals = []
    for n, b in secs:
        hexes = {h.upper() for h in HEX6.findall(b)}
        words = len(re.findall(r'\w+', b))
        if len(hexes) < 2:
            errs.append(f'direction {n[:30]!r}: name its palette (2+ hexes)')
        if words < 25:
            errs.append(f'direction {n[:30]!r}: {words} words — say ground, type, composition, motion and the signature visual')
        pals.append(hexes)
    for i in range(len(pals)):
        for j in range(i + 1, len(pals)):
            a, b = pals[i], pals[j]
            if a and b and len(a & b) / len(a | b) > 0.5:
                errs.append(f'directions {secs[i][0][:20]!r} and {secs[j][0][:20]!r} share most of their palette: '
                            'they are variations, not different directions')
    ch = re.search(r'^\s*[-*]?\s*(?:chosen|chọn)\s*:\s*(.+)$', txt, re.I | re.M)
    why = re.search(r'^\s*[-*]?\s*(?:why|because|vì sao|lý do)\s*:\s*(.+)$', txt, re.I | re.M)
    if not ch or 'TODO' in ch.group(1):
        errs.append('no "- chosen: <direction>" line')
    if not why or 'TODO' in why.group(1) or len(why.group(1).split()) < 8:
        errs.append('no "- why: ..." line of 8+ words (what the subject asks for, what the others get wrong)')
    if not list((work / 'design').glob('directions*.jpg')) + list((work / 'design').glob('directions*.png')):
        errs.append('design/directions.jpg missing (3 thumbnails side by side: python3 directions.py WORK)')
    return errs, [f'{len(secs)} directions: ' + ', '.join(n[:28] for n, _ in secs)]


def g3(work):
    g = Gate('GATE 3 design')
    ad = read(work / 'design/art-direction.md')
    g.need(bool(ad), 'design/art-direction.md exists')
    # v5.5 routing: the deck is routed from its subject, audience, tone and real assets BEFORE design;
    # mismatched directions are rejected in writing, and a deck built in a rejected style fails
    import route
    r_need, r_want = route.gate_rows(work)
    for ok, text, hint in r_need:
        g.need(ok, text, hint)
    for ok, text, hint in r_want:
        g.want(ok, text, hint)
    # v5.3 anti-template: three genuinely different directions BEFORE the storyboard
    derr, dinfo = directions_report(work)
    for i in dinfo:
        g.note(i)
    g.need(not derr, 'design/directions.md + directions.jpg: 3 different art directions sketched, one chosen and why',
           '; '.join(derr[:4]) + ' — references/art-directions.md; python3 directions.py WORK --spec design/directions.json')
    fonts = [p for p in (work / 'fonts').glob('*') if p.suffix.lower() in ('.ttf', '.otf')] if (work / 'fonts').is_dir() else []
    lic = [p for p in (work / 'fonts').glob('*') if re.search(r'ofl|licen[cs]e', p.name, re.I)] if (work / 'fonts').is_dir() else []
    g.need(len(fonts) >= 1, f'fonts/: {len(fonts)} font files', 'download the chosen OFL fonts (static TTFs) into WORK/fonts')
    fams = []
    for p in fonts:
        k = font_family_from_file(p)
        if k and k not in OFFICE_DEFAULTS and k not in fams:
            fams.append(k)
    g.want(2 <= len(fams) <= 4, f'fonts/: {len(fams)} family/families {fams or ["(none)"]} (2-3, a 4th only as one chapter display face)',
           'Noto Sans and Noto Sans Display are one family. Pair a display face with a different body family. Office defaults do not count.')
    g.need(bool(lic), 'fonts/: licence file present (OFL.txt)')
    fc = read(work / 'design/font-check.txt')
    g.need('PASS' in fc and 'FAIL' not in fc, 'design/font-check.txt: all fonts PASS the glyph check',
           'python3 check_fonts.py WORK/fonts/*.ttf --lang vi --png WORK/design/font-sample.png > WORK/design/font-check.txt')
    has_style = (work / 'design/style.json').is_file() or re.search(r'^\s*-?\s*style\s*:\s*(?!TODO)\S', ad, re.I | re.M)
    g.need(bool(has_style), 'art-direction: a style is declared (style pack or design/style.json)',
           'python3 studio.py new WORK --style <pack> (copies design/style.json), or write "- style: <pack>"')
    hexes, unsourced = palette_report(ad)
    g.want(len(hexes) >= 3, f'art-direction: {len(hexes)} palette hex codes (3+)', 'write at least 3 #RRGGBB colours, each with where it comes from')
    g.want(not unsourced, f'art-direction: every palette hex has a source on its line ({len(unsourced)} without)', f'{unsourced[:8]}')
    arc = section(ad, r'colou?r arc') or ''
    arc_ok, arc_hex, arc_sc = colour_arc_ok(arc)
    g.want(arc_ok, f'art-direction colour arc: {len(arc_hex)} hex(es) {arc_hex} across {len(arc_sc)} scene id(s) {arc_sc}',
           'name ≥2 different background hexes and ≥2 scene ids, e.g. "S1-S4 #0E0A07 → S6-S11 #F1E4C8"')
    g.want(len(items(section(ad, r'motifs?|textures?|materials?', start=True) or section(ad, r'motifs? (?:and|&) textures?'))) >= 2,
           'art-direction: >= 2 motifs/textures (a "## Motifs and textures" section)')
    g.want(len(items(section(ad, r'layered|layer'))) >= 1, 'art-direction: layered objects for Morph are planned')
    samples = list((work / 'design/samples').glob('*.jpg')) + list((work / 'design/samples').glob('*.png'))
    g.want(len(samples) >= 2, f'design/samples: {len(samples)} rendered samples (2+: title + body)', 'render the family deck and copy title + body renders here')
    g.want(len(items(section(ad, r'signature'))) >= 1, 'art-direction: a signature object/motif that carries through the deck',
           'name ONE recurring object that lives on most slides as !! layers (references/craft.md §2)')
    choice = items(section(ad, r'style choice'))
    routed = bool(read(work / 'design/routing.json'))
    g.want(routed or len(choice) >= 2 and any(re.search(r'reject|instead|rather than|not |thay vì|không chọn|loại|bỏ', l, re.I) for l in choice),
           f'art-direction: "## Style choice" names the style(s) chosen AND a rejected alternative with the reason ({len(choice)} item(s))',
           'e.g. "- chosen: blueprint for S3 (the phin is a machine)" + "- rejected: paper-editorial (too quiet for a hook)"')
    vocab_txt = strip_negated(' '.join(items(section(ad, r'motion vocabulary')))).lower()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import motionlib
        names = (set(motionlib.PRESETS) | set(motionlib.TRANSITIONS)) - {'morph', 'none', 'fade', 'appear', 'video'}
    except Exception:  # pragma: no cover
        names = {'push', 'wipe', 'zoom', 'fly', 'path', 'pulse', 'type', 'curtains'}
    names |= {'video', 'letter', 'motion path', 'trigger', 'loop', 'hyperlink', 'link', 'manim', 'diagram', 'anatomy'}
    found = sorted(n for n in names if re.search(r'\b' + re.escape(n) + r'\b', vocab_txt))
    g.want(len(found) >= 2, f'art-direction: "## Motion vocabulary" names >= 2 techniques beyond Morph/fade ({found or "none"})',
           'pick 2-4 signature techniques from references/motion-library.md and say where they play')
    cmp_ = list((work / 'design').glob('compare*.jpg'))
    g.want(bool(cmp_), 'design/compare*.jpg: the samples were put next to the reference deck', 'python3 studio.py compare WORK WORK/renders/<sample>')
    return g.report()


SIG_TOOLS = ('anatomy', 'manim', 'manimgx')
SIG_CLICHE = re.compile(r'\bbooks?\b|\bscales? of\b|\bjustice\b|light ?bulb|hand ?shake|shaking hands|globe|hands? holding|'
                        r'puzzle|\bchess\b|\bbrain\b|\brocket\b|dartboard|target with arrow|\bgears? turning\b|crystal ball', re.I)
NUMBER_CLAIM = re.compile(r'\d[\d.,]*\s*%|\d{2,}')


def _ffprobe_seconds(p):
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                           capture_output=True, text=True, timeout=60)
        return float(r.stdout.strip() or 0)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return 0.0


def _gray_frame(p, t):
    try:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(p), '-frames:v', '1',
                            '-vf', 'scale=64:36,format=gray', '-f', 'rawvideo', '-'], capture_output=True, timeout=60)
        return r.stdout if len(r.stdout) == 64 * 36 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def film_moves(p, dur):
    """Largest mean absolute difference (0-255) between frames at 10/40/70 % of the film."""
    frames = [f for f in (_gray_frame(p, dur * k) for k in (0.1, 0.4, 0.7)) if f]
    if len(frames) < 2:
        return 0.0
    return max(sum(abs(a - b) for a, b in zip(frames[i], frames[j])) / len(frames[i])
               for i in range(len(frames)) for j in range(i + 1, len(frames)))


def signature_rows(work):
    head, rows = table(read(work / 'design/signature-moments.md'), ['moment', 'tool', 'mechanism'])
    return head, [r for r in rows if col(r, 'moment').strip() and 'TODO' not in ' '.join(r.values())], getattr(rows, 'bad', ())


def signature_report(work, stage='plan', pptx=None):
    """v5.3 signature moments. stage: plan (gate 4) | film (gate 5) | final (gate 6). Returns (errors, infos)."""
    errs, info = [], []
    head, rows, bad = signature_rows(work)
    if head is None:
        return ['design/signature-moments.md has no table (| # | moment | tool | mechanism | facts | film | editable | slides |)'], info
    errs += [f'signature-moments.md: {b}' for b in bad]
    fallback = brief(work).get('signature_fallback', '').strip()
    fallback = '' if fallback.lower() in ('', 'no', 'none', 'todo') or fallback.startswith('TODO') else fallback
    hand = [r for r in rows if col(r, 'tool').strip().lower().split(' ')[0] in SIG_TOOLS]
    other = [r for r in rows if r not in hand]
    if fallback:
        info.append(f'signature_fallback: {fallback[:80]} — diagram_video/drawn moments count')
        hand = rows
    if len(hand) < 2:
        errs.append(f'{len(hand)} hand-built signature moment(s) with tool anatomy|manim (need 2; '
                    f'{len(other)} other row(s) do not count without "signature_fallback: <reason>" in brief.md)')
    ids = fact_ids(read(work / 'research/facts.md'))
    for r in rows:
        name = col(r, 'moment')[:40]
        mech = col(r, 'mechanism')
        if len(mech.split()) < 8:
            errs.append(f'{name!r}: the mechanism needs a sentence (8+ words): what moves and what that motion means')
        if SIG_CLICHE.search(col(r, 'moment') + ' ' + mech):
            errs.append(f'{name!r}: stock metaphor ({SIG_CLICHE.search(col(r, "moment") + " " + mech).group(0)}) — draw the subject\'s own mechanism')
        if ids and not cites_fact(col(r, 'facts'), ids):
            errs.append(f'{name!r}: cite the fact IDs the figure shows (facts column)')
    info.append(f'signature moments: {len(rows)} planned, {len(hand)} hand-built')
    if stage == 'plan':
        return errs, info
    media_hashes = set()
    xml_all = ''
    if pptx and Path(pptx).is_file():
        import hashlib
        import zipfile
        with zipfile.ZipFile(pptx) as z:
            for n in z.namelist():
                if n.startswith('ppt/media/') and n.lower().endswith(('.mp4', '.m4v', '.mov')):
                    media_hashes.add(hashlib.sha256(z.read(n)).hexdigest())
                elif n.startswith('ppt/slides/slide') and n.endswith('.xml'):
                    xml_all += z.read(n).decode('utf-8', 'replace')
    embedded = 0
    for r in hand:
        name = col(r, 'moment')[:40]
        film = col(r, 'film').strip('` ')
        fp = work / film
        if not film or not fp.is_file():
            errs.append(f'{name!r}: film {film or "(none)"} not found')
            continue
        dur = _ffprobe_seconds(fp)
        if dur < 3:
            errs.append(f'{name!r}: {film} plays {dur:.1f} s (need 3+)')
        mv = film_moves(fp, dur) if dur else 0
        if mv < 1.0:
            errs.append(f'{name!r}: {film} barely changes (frame difference {mv:.1f}/255): it is a still, not a film')
        stem = fp.name[:-len(fp.suffix)]
        if not any((fp.parent / f'{stem}.poster{e}').is_file() for e in ('.png', '.jpg')):
            errs.append(f'{name!r}: no poster {stem}.poster.png next to the film')
        ed = col(r, 'editable').strip('` ')
        if not ed or ed.lower() in ('-', 'none', 'no'):
            errs.append(f'{name!r}: name its editable version (shapes.json path or a !!layer on the slide)')
        elif ed.startswith('!!'):
            if stage == 'final' and f'name="{ed}"' not in xml_all:
                errs.append(f'{name!r}: editable layer {ed} not in the delivered deck')
        elif not (work / ed).is_file():
            errs.append(f'{name!r}: editable file {ed} not found')
        if stage == 'final':
            import hashlib
            if hashlib.sha256(fp.read_bytes()).hexdigest() in media_hashes:
                embedded += 1
            else:
                errs.append(f'{name!r}: {film} is not embedded in {Path(pptx).name if pptx else "the deck"}')
        info.append(f'{name}: {film} {dur:.1f} s, motion {mv:.1f}')
        if col(r, 'tool').strip().lower().startswith('anatomy'):   # v5.3.1 density / contrast (anatomy_film.py audit)
            fj = fp.parent / stem / 'film.json'
            au = {}
            try:
                au = json.loads(read(fj)).get('audit') or {}
            except (ValueError, OSError):
                pass
            if not au:
                info.append(f'WARN {name!r}: no figure audit in {fj.relative_to(work) if fj.is_relative_to(work) else fj} (re-run anatomy_film.py)')
            else:
                if au.get('line_contrast', 9) < 3.0:
                    errs.append(f'{name!r}: the figure edges reach only {au["line_contrast"]}:1 against its card: unreadable on a projector '
                                '(lift --anatomy-hi/--anatomy-mid; references/signature-moments.md, "Density and contrast")')
                for w in au.get('warnings', []):
                    info.append(f'WARN {name!r}: {w}')
    if stage == 'final':
        info.append(f'{embedded} signature film(s) embedded in the deck')
    return errs, info


def deck_styles(work):
    """Distinct styles a deck.json uses (slide "style" holds until changed). None when there is no deck.json."""
    p = work / 'deck.json'
    if not p.is_file():
        return None, 0
    try:
        spec = json.loads(read(p))
    except ValueError:
        return None, 0
    cur = spec.get('style', 'default')
    seen, n = [], 0
    for s in spec.get('slides', []):
        cur = s.get('style', cur)
        key = json.dumps(cur, sort_keys=True) if not isinstance(cur, str) else cur
        if key not in seen:
            seen.append(key)
        n += 1
    return seen, n


def style_shift_report(work, rows):
    styles, n = deck_styles(work)
    if styles is None:
        n = len(rows)
        styles = []
        for r in rows:
            v = col(r, 'style').strip()
            if v and v not in styles:
                styles.append(v)
        src = 'storyboard "style" column'
    else:
        src = 'deck.json'
    if n < 20:
        return None, f'{n} slides: scene-level style shifts optional'
    ok = len(styles) >= 2
    return ok, f'{n} slides use {len(styles)} style(s) ({src}): {[s[:24] for s in styles][:6]}'


def g4(work):
    g = Gate('GATE 4 storyboard')
    sb = read(work / 'storyboard.md')
    head, rows = table(sb, ['#', 'scene', 'layers', 'visual', 'words', 'layout', 'on-slide'])
    g.need(head is not None, 'storyboard.md has the slide table (# | scene | layout | layers | visual | on-slide text | source | words)', 'copy the template table')
    bad = list(getattr(rows, 'bad', ()))
    g.need(not bad, f'storyboard table parses: {len(bad)} malformed row(s)', '; '.join(bad[:4]))
    rows = [r for r in rows if col(r, '#').strip().isdigit()]
    scenes = {}
    for r in rows:
        scenes.setdefault(re.split(r'\s', col(r, 'scene').strip() or '?')[0], []).append(r)
    mins = talk_minutes(work)
    min_sc = min(8, max(2, round(1.5 * mins)))
    scarce = asset_scarcity(work)
    if scarce:
        keys = []
        for r in rows:
            for k in visual_keys(col(r, 'visual')):
                if k not in keys:
                    keys.append(k)
        min_sc = max(2, min(min_sc, len(keys) if keys else 2))
        g.note(f'asset_scarcity: {scarce[:80]} — scene habit lowered to {min_sc}')
    g.want(len(scenes) >= min_sc, f'{len(scenes)} scenes (habit: {min_sc}+ for {mins:g} min)')
    runs = [s for s, rs in scenes.items() if len(rs) >= 3]
    g.want(len(runs) >= 0.5 * max(1, len(scenes)), f'{len(runs)}/{len(scenes)} scenes are keyframe runs of >= 3 slides (habit: half)',
           'motion needs keyframes: split the scenes that carry a mechanism into 3-5 slides')
    g.note(f'{len(rows)} slides, {len(rows) / max(1, len(scenes)):.1f} slides per scene')
    nolayer = [col(r, '#') for r in rows if '!!' not in col(r, 'layers')]
    g.want(len(nolayer) <= 0.1 * max(1, len(rows)), f'rows without !! layers: {len(nolayer)}', f'rows {nolayer[:10]}')
    bad_vis = []
    for r in rows:
        v = col(r, 'visual').strip()
        if not v or 'TODO' in v or v in ('-', '—'):
            bad_vis.append(col(r, '#'))
            continue
        for f in re.findall(r'[\w./-]+\.(?:jpg|jpeg|png|webp|mp4)', v, re.I):
            f = re.sub(r'^(frame|drawn|film):', '', f)
            if not any((work / d / f).exists() or (work / d / Path(f).name).exists()
                       for d in ('assets', 'assets/gen', 'assets/film', 'design', 'assets/frames', 'media', '.')):
                bad_vis.append(f'{col(r, "#")}:{f}?')
    g.need(not bad_vis, f'every slide has a real visual ({len(bad_vis)} problems)', f'{bad_vis[:10]} — name a kept asset, film:, drawn:<motif> or frame:<file>')
    for e in storyboard_visual_errors(rows, col):
        g.want(False, 'visuals: ' + e, 'one file on at most 4 rows; distinct visuals ≥ scenes')
    for e in storyboard_layout_errors(rows, col):
        g.note('layout labels: ' + e + ' — advisory label count only; the measure that decides is check_deck\'s rendered '
               'geometry fingerprint (gate 5 deck check), which fails text-left/photo-right on 4+ slides')
    facts_txt = read(work / 'research/facts.md')
    ids = fact_ids(facts_txt)
    # the scene column holds scene ids (S1, S2...) that collide with source ids (S1): never count it as a citation
    cite_txt = lambda r: ' '.join(str(v) for k, v in r.items() if not re.match(r'(#|scene|keyframe)', k))
    cited = [r for r in rows if cites_fact(cite_txt(r), ids)]
    g.need(bool(cited) or not rows, f'{len(cited)}/{len(rows)} rows cite a fact ID', 'put the fact ID in the "source" column')
    numbers = [col(r, '#') for r in rows if NUMBER_CLAIM.search(col(r, 'on-slide'))
               and not cites_fact(cite_txt(r), ids)]
    g.need(not numbers, f'every row with a number on the slide cites a fact ID ({len(numbers)} without)',
           f'rows {numbers[:10]}: a number on screen is a claim; put its fact ID in the source column')
    for e in storyboard_density_errors(rows, col, facts_txt):
        g.want(False, 'content: ' + e, f'habit: ≥ {WORDS_AVG_MIN:g} words a slide on average, ≥ {FACT_SLIDE_MIN:.0%} of rows cite')
    words = []
    for r in rows:
        try:
            words.append(int(re.findall(r'\d+', col(r, 'words'))[0]))
        except IndexError:
            words.append(None)
    g.want(None not in words, 'every row has a words budget', 'fill the words column (0 is allowed for silent keyframes)')
    budget = int(mins * 130 - 2 * 6 / 60 * 130)
    tot = sum(w for w in words if w)
    g.want(tot <= budget, f'words budget {tot} <= {budget} ({mins:g} min at 130 wpm)', 'cut words now, not after the script is written')
    am = re.search(r'anchor\s*:\s*["“]([^"”]+)["”]', sb, re.I)
    if g.want(bool(am) and 'TODO' not in am.group(1), 'anchor phrase declared (anchor: "...")', 'one short sentence the audience will repeat'):
        n = sum(1 for r in rows if am.group(1).lower() in ' '.join(r.values()).lower())
        g.want(n >= 3, f'anchor phrase appears on {n} slides (setup / middle / end)')
    am_arc = re.search(r'colou?r arc\s*:\s*(.*)', sb, re.I)
    arc_ok, arc_hex, arc_sc = colour_arc_ok(am_arc.group(1) if am_arc else '')
    g.want(arc_ok, f'colour arc names ≥2 background hexes across ≥2 scenes (hexes {arc_hex}, scenes {arc_sc})')
    g.want(re.search(r'circular close\s*:\s*(?!TODO)\S', sb, re.I) is not None, 'circular close declared')
    deck_ms = False
    if (work / 'deck.json').is_file():
        try:
            deck_ms = any('ms' in sl for sl in json.loads(read(work / 'deck.json')).get('slides', []))
        except ValueError:
            deck_ms = False
    g.want((work / 'motion.json').is_file() or deck_ms, 'durations planned (motion.json, or "ms" on slides in deck.json)')
    # v5.3 creative floor
    serr, sinfo = signature_report(work, 'plan')
    for i in sinfo:
        if i.startswith('WARN '):
            g.want(False, i[5:])
        else:
            g.note(i)
    g.need(not serr, 'design/signature-moments.md: >= 2 hand-built animated diagrams tied to the mechanism',
           '; '.join(serr[:4]) + ' — references/signature-moments.md')
    ok, txt = style_shift_report(work, rows)
    if ok is None:
        g.note(txt)
    else:
        g.need(ok, 'style shifts: ' + txt, 'a 20+ slide deck changes style at scene level at least once (slide "style": ..., references/art-directions.md)')
    return g.report()


def run_check_deck(deck, extra):
    cmd = [sys.executable, str(HERE / 'check_deck.py'), str(deck)] + extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if l.startswith(('ERROR', 'RESULT'))]
    return r.returncode == 0, tail


def latest_round(renders, group):
    """renders/<group>-N with the highest N (numeric, not lexical: g1-10 beats g1-9)."""
    if not renders.is_dir():
        return None
    best = None
    for p in renders.iterdir():
        m = re.fullmatch(re.escape(group) + r'-(\d+)', p.name)
        if p.is_dir() and m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), p)
    return best[1] if best else None


def max_mb(work):
    v = re.findall(r'[\d.]+', brief(work).get('max_deck_mb', '25'))
    return float(v[0]) if v else 25.0


def g5(work, group, deck):
    g = Gate(f'GATE 5 group {group}')
    rd = latest_round(work / 'renders', group)
    g.need(rd is not None and any(rd.glob('contact*.jpg')), f'renders/{group}-N/contact*.jpg exists ({rd.name if rd else "none"})',
           'python3 studio.py build WORK --group <group> (renders a new round), then LOOK')
    g.want((work / 'notes' / f'{group}.md').is_file(), f'notes/{group}.md written (what changed, layers, sources, defects left)')
    if deck and Path(deck).is_file():
        ok, tail = run_check_deck(deck, ['--max-mb', '100000'])   # v5.3: size is checked once, at gate 6
        g.need(ok, f'check_deck.py {Path(deck).name}: ' + (tail[-1] if tail else ''), '; '.join(tail[:6]))
        legibility_rows(g, work, deck)
        mb = Path(deck).stat().st_size / 1e6
        g.want(mb <= 0.8 * max_mb(work), f'preview size {mb:.1f} MB (final limit {max_mb(work):g} MB; warn above 80%)',
               'keep_asset downsizes to 2560 px; finish_dedupe.py; shorter or lower-bitrate films (the final is checked hard at gate 6)')
    else:
        g.need(False, f'pass --deck WORK/deck/preview-{group}.pptx ({deck or "none"})')
    return g.report()


COLLAGE_STYLES = ('heritage-collage',)


def style_pack(work, st):
    """The shipped pack a deck style comes from: a pack name, a copied design/style.json ("name"), or an
    inline deck.json style ("extends")."""
    st = str(st)
    try:
        spec = json.loads(read(work / 'deck.json')) if (work / 'deck.json').is_file() else {}
    except ValueError:
        spec = {}
    inline = (spec.get('styles') or {}).get(st) or (spec.get('style_overrides') or {}).get(st)
    if isinstance(inline, dict):
        return Path(str(inline.get('extends') or inline.get('name') or st)).stem
    if st.endswith('.json'):
        p = Path(st) if Path(st).is_absolute() else work / st
        try:
            return json.loads(read(p)).get('name') or p.stem
        except (ValueError, OSError, AttributeError):
            return p.stem
    return st


def legibility_rows(g, work, deck):
    """v5.4 gate rows: capitals only for headlines (always a FAIL); text on photos over a band or scrim
    (a FAIL for the heritage-collage style, whose critique rule it is; a WARN otherwise)."""
    import legibility_audit
    try:
        res = legibility_audit.audit_pptx(deck)
    except Exception as e:   # a broken preview is reported by check_deck already
        g.note(f'legibility audit skipped: {e}')
        return
    caps = [f'slide {i}: {n}' for i, _, cb in res for n, _, _ in cb]
    scr = [f'slide {i}: {n}' for i, sc, _ in res for n in sc]
    g.need(not caps, f'caps only for headlines: {len(caps)} body paragraph(s) in ALL CAPS', '; '.join(caps[:5]) + ' — sentence case')
    styles, _ = deck_styles(work)
    collage = any(style_pack(work, st) in COLLAGE_STYLES for st in (styles or []))
    ok_line = f'text on photos sits on a colour band, chip or gradient scrim ({len(scr)} without)'
    hint = '; '.join(scr[:5]) + ' — add a chip/band (callout, photogrid labels) or a gradient veil under the text'
    (g.need if collage else g.want)(not scr, ok_line, hint)


def g5_deck(work):
    """v5.4: the whole-deck check before Phase 6. Per-group checks cannot see deck-wide repetition (the same
    layout fingerprint, entrance or film treatment on slides 4, 17 and 31), so the full build is checked here."""
    g = Gate('GATE 5 whole deck')
    pv = work / 'deck' / 'preview-all.pptx'
    dj = work / 'deck.json'
    g.need(pv.is_file(), 'deck/preview-all.pptx exists (python3 studio.py build WORK, no --group, builds the whole deck)')
    if pv.is_file():
        g.need(not dj.is_file() or pv.stat().st_mtime >= dj.stat().st_mtime - 1, 'preview-all.pptx is newer than deck.json',
               'deck.json changed after the last full build: rebuild with python3 studio.py build WORK')
        try:
            want = len(json.loads(dj.read_text(encoding='utf-8')).get('slides', [])) if dj.is_file() else 0
        except ValueError:
            want = 0
        import zipfile
        with zipfile.ZipFile(pv) as z:
            have = len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)])
        g.need(not want or have == want, f'preview-all.pptx has every slide ({have} of {want})')
        rd = latest_round(work / 'renders', 'all')
        extra = ['--max-mb', '100000'] + (['--renders', str(rd)] if rd is not None else [])
        ok, tail = run_check_deck(pv, extra)
        g.need(ok, 'check_deck.py on the whole deck (deck-wide variety, layout fingerprints, reuse): ' + (tail[-1] if tail else ''),
               '; '.join(tail[:6]))
        g.want(rd is not None, f'renders/all-N of the whole deck ({rd.name if rd else "none"})')
        legibility_rows(g, work, pv)
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
        extra = ['--max-mb', f'{max_mb(work):g}']
        if anchor:
            extra += ['--anchor', anchor.group(1)]
        ok, tail = run_check_deck(pp[0], extra)
        g.need(ok, 'check_deck.py: ' + (tail[-1] if tail else ''), '; '.join(tail[:6]))
        legibility_rows(g, work, pp[0])
        mb6 = pp[0].stat().st_size / 1e6
        g.need(mb6 <= max_mb(work), f'deliver pptx {mb6:.1f} MB <= {max_mb(work):g} MB')
        g.want(mb6 <= 0.85 * max_mb(work), f'deliver pptx {mb6:.1f} MB has headroom (warn above 85% of {max_mb(work):g} MB)',
               'a venue upload or e-mail limit is often the same number: shrink films (crf 26) or photos (2048 px)')
        target = (re.findall(r'\d+(?:[.,]\d+)?', b.get('talk_minutes', '')) or [''])[0].replace(',', '.')
        r = subprocess.run([sys.executable, str(HERE / 'words_budget.py'), 'measure', str(pp[0]), '--target', target or '99'],
                           capture_output=True, text=True)
        est = [l for l in r.stdout.splitlines() if l.startswith(('estimate', 'target'))]
        accepted = b.get('time_overrun_accepted', 'no').lower().startswith('y')
        g.want(r.returncode == 0 or accepted, 'speaking time: ' + ' | '.join(est), 'trim the notes (heaviest slides first) or get the user to accept the overrun')
        serr, sinfo = signature_report(work, 'final', pp[0])
        for i in sinfo:
            if i.startswith('WARN '):
                g.want(False, i[5:])
            else:
                g.note(i)
        g.need(not serr, 'signature moments: films exist, move, have a poster and an editable version, and are embedded',
               '; '.join(serr[:4]))
    rd = latest_round(work / 'renders', 'final')
    g.need(rd is not None and any(rd.glob('contact*.jpg')), f'renders/final-N/contact*.jpg of the delivered deck ({rd.name if rd else "none"})')
    return g.report()


def cmd_init(work, kind):
    work.mkdir(parents=True, exist_ok=True)
    for d in ('research', 'assets/candidates', 'assets/_uncertain', 'assets/gen', 'assets/film', 'design/samples', 'design/anatomy',
              'design/manim', 'fonts', 'deck', 'renders', 'notes', 'deliver', 'media_orig'):
        (work / d).mkdir(parents=True, exist_ok=True)
    plan = {'brief.md': 'brief.md', 'facts.md': 'research/facts.md', 'accuracy.md': 'research/accuracy.md', 'lessons.md': 'research/lessons.md',
            'CREDITS.md': 'assets/CREDITS.md', 'art-direction.md': 'design/art-direction.md', 'storyboard.md': 'storyboard.md', 'motion.json': 'motion.json',
            'directions.md': 'design/directions.md', 'signature-moments.md': 'design/signature-moments.md'}
    for src, dst in plan.items():
        if not (work / dst).exists() and (TEMPLATES / src).is_file():
            shutil.copy(TEMPLATES / src, work / dst)
    b = (work / 'brief.md').read_text(encoding='utf-8')
    if kind:
        b = re.sub(r'- deliverable_kind: TODO[^\n]*', f'- deliverable_kind: {kind}', b)
        (work / 'brief.md').write_text(b, encoding='utf-8')
    print('initialised', work)
    for p in sorted(work.rglob('*')):
        print('  ', p.relative_to(work))


def groups_with_renders(work):
    found = set()
    if (work / 'renders').is_dir():
        for p in (work / 'renders').iterdir():
            m = re.fullmatch(r'(g\d+)-\d+', p.name)
            if m and p.is_dir():
                found.add(m.group(1))
    return sorted(found, key=lambda s: int(s[1:]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init'); s.add_argument('work'); s.add_argument('--kind', choices=tuple(MIN))
    s = sub.add_parser('check'); s.add_argument('work'); s.add_argument('--gate', type=int); s.add_argument('--upto', type=int)
    s.add_argument('--group', help='gN for one group; "all" for the whole-deck check'); s.add_argument('--deck')
    s.add_argument('--stop-on-fail', action='store_true', help='with --upto: stop at the first failing gate')
    a = ap.parse_args(argv)
    work = Path(a.work).resolve()
    if a.cmd == 'init':
        return cmd_init(work, a.kind)
    gates = list(range(0, a.upto + 1)) if a.upto is not None else [a.gate if a.gate is not None else 0]
    fns = {0: g0, 1: g1, 2: g2, 3: g3, 4: g4, 6: g6}
    ok = True
    summary = []

    def log(n, res, grp=''):
        with (work / 'gates.log').open('a', encoding='utf-8') as f:
            f.write(f'{datetime.datetime.now().isoformat(timespec="seconds")} gate {n}{" " + grp if grp else ""}: {"PASS" if res else "FAIL"}\n')

    for n in gates:
        if a.stop_on_fail and not ok:
            break
        if n == 5:
            if a.group == 'all':
                res = g5_deck(work)
                ok &= res
                log(5, res, 'all')
                summary.append(('5 all', res))
                continue
            if a.group:
                todo = [(a.group, a.deck or str(work / 'deck' / f'preview-{a.group}.pptx'))]
            else:   # v5.3: --upto no longer skips gate 5; it checks every group that was rendered
                todo = [(gr, str(work / 'deck' / f'preview-{gr}.pptx')) for gr in groups_with_renders(work)]
                if not todo:
                    print('== GATE 5: no renders/gN-M folders yet (build a group: python3 studio.py build WORK --group g1)')
                    if a.upto is None:
                        ok = False
            for gr, dk in todo:
                res = g5(work, gr, dk)
                ok &= res
                log(5, res, gr)
                summary.append((f'5 {gr}', res))
            if a.upto is not None:   # v5.4: --upto 5 is the check before Phase 6, so it includes the whole deck
                res = g5_deck(work)
                ok &= res
                log(5, res, 'all')
                summary.append(('5 all', res))
            continue
        res = fns[n](work)
        ok &= res
        log(n, res)
        summary.append((str(n), res))
    if len(summary) > 1:
        first = next((k for k, r in summary if not r), None)
        print('\n== SUMMARY: ' + '  '.join(f'gate {k} {"PASS" if r else "FAIL"}' for k, r in summary))
        print('first FAIL: gate ' + first + ' (fix it first; later gates often fail because of it)' if first else 'all PASS')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
