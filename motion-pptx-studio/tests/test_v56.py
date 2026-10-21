"""v5.6: the world-economy test (econ-test/NOTES.md I1-I36) and the v5.3.1 leftovers.

Semantic routing (zones, declared domains, tone vectors, composed reasons, kept images, semantic
staleness), genome fixes (arc string, palette provenance, ground2, chrome title + source, every
rejection), construct (text color/fill, closed:false, lit colour), timing (bare pauses, transitions,
Vietnamese rate, fact tags out of the read-aloud script), audits (bg photos and groups in the
fingerprint, sources without on-slide IDs, AI provenance words), gates (phase order, samples,
history file, strict final check), studio (new/fonts without --style), docs and the worked example."""
import contextlib
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from conftest import NS, SKILL, named, slides_xml

S = SKILL / 'scripts'


def call(fn, *args):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            r = fn(*args)
            code = r if isinstance(r, int) else 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, buf.getvalue()


ECON = """# Brief
- topic: Kinh tế thế giới 2026 — tăng trưởng, lạm phát, lãi suất ngân hàng trung ương, thương mại, nợ công và làn sóng đầu tư AI
- audience: sinh viên kinh tế và nhà đầu tư cá nhân
- deliverable_kind: business
- tone: serious, analytical, không cổ động
- domains: auto (what the deck is ABOUT when the words could mislead)
"""
CREDITS = """# CREDITS
| file | what | licence | source |
|---|---|---|---|
| 01_port.jpg | Container port at dusk | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Port.jpg |
| 02_wafer.jpg | Silicon wafer (AI-enabling goods) | public domain, NASA photo 1965×1474 | https://images.nasa.gov/x |

## Rejected during research (and why)
| 03_rocket.jpg | rocket launch, NASA | off-topic |
"""


def photo(p, col):
    im = Image.new('RGB', (96, 64), col)
    for x in range(0, 96, 8):
        for y in range(64):
            im.putpixel((x, y), tuple(min(255, c + 25) for c in col))
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p)


@pytest.fixture
def econ(tmp_path):
    w = tmp_path / 'econ'
    (w / 'research').mkdir(parents=True)
    (w / 'brief.md').write_text(ECON, encoding='utf-8')
    (w / 'research/facts.md').write_text('| 1.1 | IMF: global growth 3.1% | (I1) | [verified] |\n'
                                         '| 1.2 | inflation 4.2%, interest rates held | (I1) | [verified] |\n'
                                         '| 1.3 | AI investment, NASA wafer photo credit | (I2) | [verified] |\n', encoding='utf-8')
    photo(w / 'assets/01_port.jpg', (200, 205, 215))
    photo(w / 'assets/02_wafer.jpg', (190, 200, 220))
    photo(w / 'assets/candidates/03_rocket.jpg', (10, 10, 30))
    photo(w / 'assets/contact.jpg', (0, 0, 0))
    (w / 'assets/CREDITS.md').write_text(CREDITS, encoding='utf-8')
    return w


# ------------------------------------------------------------------ routing: semantic, not keyword hits

def test_ai_and_a_nasa_credit_do_not_make_an_economics_deck_tech(econ):
    import route
    dec = route.decide(econ)
    s = dec['subject']
    assert s['about'] == ['economy'] or s['about'][0] == 'economy'
    assert 'technology' not in s['about'] and 'aerospace' not in s['about']
    assert s['domains']['economy'] == 1.0 and s['domains'].get('technology', 0) <= route.MENTION_CAP
    assert dec['chosen'] in ('boardroom-data', 'swiss-blue', 'paper-editorial')
    assert 'noir-product' not in dec['chosen'] and 'glass-tech' != dec['chosen']


def test_tone_is_scored_by_register_not_by_the_word_calm(econ):
    import route
    s = route.subject_profile(econ)
    assert 'serious' in s['tones'] and 'analytical' in s['tones']
    assert any('cổ động' in x for x in s['tone_excluded'])
    calm_family = ['calm', 'precise', 'clear']
    loud_family = ['playful', 'energetic', 'friendly']
    assert route.tone_fit(calm_family, s['tones']) > 0.8 > 0.3 > route.tone_fit(loud_family, s['tones'])


def test_rejections_are_composed_from_this_decks_evidence_and_never_copied(econ):
    import route
    dec = route.decide(econ)
    reasons = [r[0] for r in dec['rejected'].values()]
    assert len(reasons) >= 4 and len(set(reasons)) == len(reasons)          # no two identical reasons
    subj = [r for r in reasons if not r.startswith('fit ')]
    assert subj and all('economy' in r and ('kinh tế' in r or 'lạm phát' in r or 'declared' in r) for r in subj)
    assert all('heritage' not in r.split('this deck is about')[-1][:30] for r in subj)


def test_material_counts_only_kept_images_and_no_pixel_sizes_as_years(econ):
    import route
    m = route.material_profile(econ)
    assert m['images'] == 2                         # candidates/ and contact sheets are not the deck's material
    assert 1965 not in m['old_dates']               # "1965×1474" is a pixel size, not a year


def test_derived_files_do_not_make_routing_stale_and_staleness_names_the_input(econ):
    import route
    route.route(econ)
    photo(econ / 'assets/cut/wafer.png', (255, 255, 255))
    photo(econ / 'assets/film/x.poster.png', (0, 0, 0))
    _, want = route.gate_rows(econ)
    cur = [w for w in want if w[1].startswith('routing is current')][0]
    assert cur[0] and 'unchanged' in cur[1]
    (econ / 'research/facts.md').write_text((econ / 'research/facts.md').read_text(encoding='utf-8') + '| 1.4 | debt 93% of GDP | (I1) |\n',
                                            encoding='utf-8')
    _, want = route.gate_rows(econ)
    cur = [w for w in want if w[1].startswith('routing is current')][0]
    assert 'facts' in cur[1] and 'the decision is the same' in cur[1] and cur[0]


def test_declared_domains_win_and_template_guidance_is_ignored(econ):
    import route
    assert route.declared_domains(econ, route.brief(econ))[0] == {}            # "auto (...)" declares nothing
    b = (econ / 'brief.md').read_text(encoding='utf-8').replace('- domains: auto (what the deck is ABOUT when the words could mislead)',
                                                                 '- domains: finance, economy')
    (econ / 'brief.md').write_text(b, encoding='utf-8')
    s = route.subject_profile(econ)
    assert s['declared'] == {'finance': 1.0, 'economy': 0.85} and set(s['about']) == {'finance', 'economy'}
    assert 'routing.md' and 'declared domains' in route.render_md(route.decide(econ))


def test_the_three_proof_briefs_route_to_their_subject():
    import route
    for w, want_about, bad in (('/workspace/econ-test', 'economy', 'technology'), ('/workspace/v55-spacex', 'aerospace', 'heritage'),
                               ('/workspace/v55-doson', 'heritage', 'aerospace')):
        if not Path(w, 'brief.md').is_file():
            pytest.skip(f'{w} not on this machine')
        d = route.decide(w)
        assert d['subject']['about'][0] == want_about or want_about in d['subject']['about']
        assert bad not in d['subject']['about']


# ------------------------------------------------------------------ style docs for every family

def test_every_family_has_a_style_doc():
    fams = [p.stem for d in ('styles', 'styles-experimental') for p in (SKILL / 'assets' / d).glob('*.json')]
    assert len(fams) >= 14
    missing = [f for f in fams if not (SKILL / 'references/styles' / f'{f}.md').is_file()]
    assert not missing, missing
    bd = (SKILL / 'references/styles/boardroom-data.md').read_text(encoding='utf-8')
    assert '## Layout grammar' in bd and '## Signature motion' in bd and 'economy' in bd


# ------------------------------------------------------------------ genome

def test_genome_arc_string_is_split_not_iterated_by_character(tmp_path):
    import genome
    g = {'route': 'boardroom-data', 'palette': {'ground': '#F5F7FA', 'ink': '#0F1722', 'accent': '#0E7C6B'},
         'arc': 'S1 ground → S2 navy -> S3 ground'}
    st = genome.compile_genome(g, tmp_path)
    md = genome.art_direction_md(g, st, tmp_path)
    assert '- S1 ground → S2 navy → S3 ground' in md and 'S → 1' not in md
    with pytest.raises(SystemExit, match='arc'):
        genome.compile_genome(dict(g, arc=[1, 2]), tmp_path)


def test_palette_provenance_says_sampled_only_for_sampled_keys(tmp_path):
    import genome
    import visual_audit
    photo(tmp_path / 'assets/p.jpg', (30, 90, 160))
    g = {'route': 'boardroom-data', 'light': 'light', 'palette': {'from_image': 'assets/p.jpg', 'ground': '#F4F2EE'},
         'why': {'material': 'a light paper', 'palette': 'from the port photo'}}
    st = genome.compile_genome(g, tmp_path)
    md = genome.art_direction_md(g, st, tmp_path)
    ground = [l for l in md.splitlines() if l.startswith('- ground ')][0]
    accent = [l for l in md.splitlines() if l.startswith('- accent ')][0]
    assert 'explicit in the genome' in ground and 'sampled from' not in ground
    assert 'sampled from assets/p.jpg' in accent
    assert any(l.startswith('- ground2 ') for l in md.splitlines())
    _, unsourced = visual_audit.palette_report(md)
    assert st['palette']['ground2'].upper() not in unsourced and not unsourced


def test_genome_chrome_runs_the_title_and_a_source_line(build, tmp_path):
    import genome
    g = {'route': 'boardroom-data', 'palette': {'ground': '#F5F7FA', 'ink': '#0F1722', 'accent': '#0E7C6B'}}
    st = genome.compile_genome(g, tmp_path)
    over = {c['name']: c for c in st['chrome']['over']}
    assert over['!!running']['text'] == '{title}' and over['!!source']['text'] == '{source}'
    assert genome.compile_genome(dict(g, chrome={'running': 'scene'}), tmp_path)['chrome']['over'][2]['text'] == '{scene}'
    (tmp_path / 'st.json').write_text(json.dumps(st), encoding='utf-8')
    _, slides, _ = build({'title': 'Kinh tế 2026', 'style': str(tmp_path / 'st.json'), 'slides': [
        {'scene': 'S1', 'source': 'Nguồn: IMF WEO 10/2026', 'shapes': []}, {'scene': 'S2', 'shapes': []}]})
    from conftest import text
    assert text(named(slides[0], '!!running')) == 'Kinh tế 2026' and 'IMF' in text(named(slides[0], '!!source'))
    assert named(slides[1], '!!source') is None                       # an empty source is skipped, not an empty box


def test_art_direction_lists_every_rejection_subject_reasons_first(tmp_path):
    import genome
    (tmp_path / 'design').mkdir()
    rej = {'kinetic-type': ['fit 0.20 < 0.40, weakest on tone'], 'heritage-collage': ['collage softness ...; this deck is about economy'],
           'lacquer-heritage': ['gold ...; this deck is about economy'], 'neo-brutal': ['fit 0.12 < 0.40'], 'studio-pop': ['cartoon ...; about economy']}
    (tmp_path / 'design/routing.json').write_text(json.dumps({'chosen': 'boardroom-data', 'why': 'w', 'rejected': rej}), encoding='utf-8')
    g = {'route': 'boardroom-data', 'palette': {'ground': '#F5F7FA', 'ink': '#0F1722', 'accent': '#0E7C6B'}}
    md = genome.art_direction_md(g, genome.compile_genome(g, tmp_path), tmp_path)
    lines = [l for l in md.splitlines() if l.startswith('- rejected:')]
    assert len(lines) == 5
    assert [('fit ' in l) for l in lines] == [False, False, False, True, True]


# ------------------------------------------------------------------ construct

def test_construct_text_fill_becomes_color_with_a_warning_and_closed_false_is_a_stroke():
    import construct

    class Spec:
        warnings = []
    parts = [{'id': 'base', 'kind': 'rect', 'layer': 'base', 'at': [0, 0, 10, 1], 'fill': 'surface'},
             {'id': 'line', 'kind': 'poly', 'layer': 'mechanism', 'on': 'base', 'closed': False, 'points': [[0, 0], [5, -2], [10, -1]],
              'fill': 'accent', 'line': 'accent'},
             {'id': 't', 'kind': 'text', 'layer': 'label', 'on': 'base', 'text': 'night', 'at': [1, 0.2, 2, 0.4], 'fill': 'ink'}]
    sp = Spec()
    prims = {s['name']: s for s in construct.comp_construct(sp, {'type': 'construct', 'name': 'c', 'parts': parts, 'x': 1, 'y': 1, 'w': 8,
                                                                  'reveal': True})}
    assert prims['!!c.t']['color'] == 'ink' and any('"color", not "fill"' in w for w in sp.warnings)
    assert prims['!!c.line'].get('open') is True and 'fill' not in prims['!!c.line']
    assert prims['!!c.line']['anim'][0]['fx'] == 'wipe'                                    # drawn along the stroke (Create)


def test_construct_lit_part_can_take_another_palette_colour():
    import construct
    parts = [{'id': 'base', 'kind': 'rect', 'layer': 'base', 'at': [0, 0, 10, 1]},
             {'id': 'bar', 'kind': 'rect', 'layer': 'structure', 'on': 'base', 'at': [1, -3, 2, 3], 'fill': 'faint', 'lit': 'accent2'},
             {'id': 'cap', 'kind': 'line', 'layer': 'control', 'on': 'base', 'points': [[0, -4], [10, -4]], 'line': 'muted'}]
    prims = {s['name']: s for s in construct.comp_construct(None, {'type': 'construct', 'name': 'c', 'parts': parts, 'x': 1, 'y': 1, 'w': 8})}
    assert prims['!!c.bar']['fill'] == 'accent2'
    parts[1]['lit'] = True
    prims = {s['name']: s for s in construct.comp_construct(None, {'type': 'construct', 'name': 'c', 'parts': parts, 'x': 1, 'y': 1, 'w': 8})}
    assert prims['!!c.bar']['fill'] == 'lit'
    parts[1]['lit'], parts[2]['lit'] = False, 'accent2'
    prims = {s['name']: s for s in construct.comp_construct(None, {'type': 'construct', 'name': 'c', 'parts': parts, 'x': 1, 'y': 1, 'w': 8})}
    assert prims['!!c.cap']['color'] == 'accent2'                                          # a lit stroke is lit in its line


# ------------------------------------------------------------------ timing and the script

def test_bare_pause_counts_a_default_and_warns(tmp_path):
    import words_budget
    n = tmp_path / 'n.md'
    n.write_text('##### 1\nMột hai ba [ngừng] bốn năm\n##### 2\nsáu bảy [ngừng 2 giây]\n', encoding='utf-8')
    code, out = call(words_budget.main, ['measure', str(n)])
    assert '3 s of marked pauses' in out and 'WARN 1 pause mark(s) without seconds' in out
    assert 'with transitions:' in out


def test_plan_guidance_sums_to_the_budget_and_vietnamese_rate(tmp_path):
    import re as _re
    import words_budget
    _, out = call(words_budget.main, ['plan', '--minutes', '12', '--slides', '30', '--keyframes', '4'])
    total = int(_re.search(r'budget: (\d+) words', out).group(1))
    m = _re.search(r'(\d+) keyframe-only slides ~6 words, (\d+) hook/close ~22, (\d+) content slides ~(\d+)', out)
    k, h, c, per = map(int, m.groups())
    assert abs(k * 6 + h * 22 + c * per - total) <= c          # following the guidance fills the talk
    _, vi = call(words_budget.main, ['plan', '--minutes', '10', '--slides', '20', '--lang', 'vi'])
    assert '160 words/min' in vi


def test_transitions_warn_when_pausing_through_them_runs_over(tmp_path):
    import words_budget
    n = tmp_path / 'n.md'
    n.write_text(''.join(f'##### {i}\n' + 'từ ' * 60 + '\n' for i in range(1, 31)), encoding='utf-8')   # 1800 words
    _, out = call(words_budget.main, ['measure', str(n), '--target', '14', '--morph-ms', '1500'])
    assert 'OK' in out and 'WARN with a pause at every transition' in out


def test_script_docx_strips_fact_tags_and_lists_them_in_an_appendix(tmp_path):
    pytest.importorskip('docx')
    import script_docx
    from docx import Document
    n = tmp_path / 'notes.md'
    n.write_text('##### 1\nLạm phát 4,2%. [fact 1.2]\n##### 2\nTăng trưởng 3,1% [1.1, 1.3]\n', encoding='utf-8')
    sc = tmp_path / 'sc.json'
    sc.write_text(json.dumps([{'name': 'A', 'start': 1, 'end': 2}]), encoding='utf-8')
    out = tmp_path / 's.docx'
    script_docx.build(n, sc, out, 'T', '', None, 130, 150, ['[ngừng 2 giây]'])
    body = [p.text for p in Document(out).paragraphs]
    said = [t for t in body if t.startswith(('Lạm phát', 'Tăng trưởng'))]
    assert said == ['Lạm phát 4,2%.', 'Tăng trưởng 3,1%']
    assert any(t == 'Trang 2: 1.1, 1.3' for t in body) and any('chuyển cảnh' in t and '×' in t for t in body)


# ------------------------------------------------------------------ audits

def test_sources_count_a_visible_source_line_and_flag_ids_on_slides():
    import visual_audit
    a = visual_audit.Audit()
    slides = [{'onslide': 'Lạm phát 4,2%\nNguồn: IMF WEO', 'notes': ''}, {'onslide': 'Nợ công 93% [fact 1.4]', 'notes': ''},
              {'onslide': 'GDP 3,1%', 'notes': 'IMF dự báo [fact 1.1]'}]
    visual_audit._density_and_fonts(slides, a, '| 1.1 | x |\n| 1.4 | y |\n', min_slides=99)
    txt = '\n'.join(str(x) for x in (a.warns if hasattr(a, 'warns') else []) + (a.infos if hasattr(a, 'infos') else []))
    txt = txt or json.dumps(a.__dict__, default=str, ensure_ascii=False)
    assert 'sourced slides' in txt and '2/3' in txt and 'fact IDs printed on slides [2]' in txt


def test_fingerprint_sees_background_photos_and_group_contents(build, png):
    import variety_audit
    deck = {'slides': [
        {'bg': {'image': str(png)}, 'shapes': [{'type': 'text', 'name': 't', 'text': 'Cover', 'x': 4, 'y': 3, 'w': 5, 'h': 1, 'size': 40}]},
        {'shapes': [{'type': 'text', 'name': 't', 'text': 'Title', 'x': 4, 'y': 3, 'w': 5, 'h': 1, 'size': 40}]},
        {'shapes': [{'type': 'text', 'name': 't', 'text': 'Chart', 'x': 4, 'y': 3, 'w': 5, 'h': 1, 'size': 40},
                    {'type': 'group', 'name': 'bars', 'shapes': [
                        {'type': 'rect', 'name': f'b{i}', 'x': 1 + i * 1.6, 'y': 4.5 - i * 0.6, 'w': 1.2, 'h': 2 + i * 0.6, 'fill': '#0E7C6B'}
                        for i in range(5)]}]}]}
    _, slides, _ = build(deck)
    fps = [variety_audit.geometry(s)[0] for s in slides]
    assert fps[0] != fps[1] and fps[2] != fps[1] and fps[0] != fps[2]


def test_ai_provenance_words_not_the_word_ai():
    import gates
    for real in ('Silicon wafer, AI-enabling goods', 'AI data centre, server racks', 'Nvidia AI chip on a board'):
        assert not gates.AI_WORD.search(real), real
    for gen in ('AI-generated plate', 'generated by AI', 'ảnh AI', 'tạo bằng AI', 'Midjourney v6', 'made with AI (Codex)'):
        assert gates.AI_WORD.search(gen), gen


# ------------------------------------------------------------------ gates: phase order, samples, history, strict final

def gate_work(tmp_path, kind='product'):
    import gates
    w = tmp_path / 'g'
    call(gates.main, ['init', str(w), '--kind', kind])
    return w


def test_gate4_treats_storyboard_films_as_planned_and_gate5_requires_them(tmp_path):
    import gates
    w = tmp_path / 'w'
    w.mkdir()
    (w / 'storyboard.md').write_text('| # | scene | visual |\n|---|---|---|\n| 1 | S1 | film:assets/film/lift.mp4 |\n', encoding='utf-8')
    assert gates.is_planned_film('assets/film/lift.mp4', 'film:assets/film/lift.mp4')
    assert gates.missing_planned_films(w) == ['assets/film/lift.mp4']
    (w / 'assets/film').mkdir(parents=True)
    (w / 'assets/film/lift.mp4').write_bytes(b'0')
    assert gates.missing_planned_films(w) == []
    src = (S / 'gates.py').read_text(encoding='utf-8')
    assert "g.want(not planned, f'planned films not rendered yet" in src


def test_gate3_needs_samples_and_a_compare(tmp_path):
    import gates
    w = gate_work(tmp_path)
    code, out = call(gates.main, ['check', str(w), '--gate', '3'])
    rows = [l for l in out.splitlines() if 'design/samples' in l or 'design/compare' in l]
    assert rows and all(l.lstrip().startswith('FAIL') for l in rows), rows


def test_gates_history_never_writes_the_users_gates_log(tmp_path):
    import gates
    w = gate_work(tmp_path)
    (w / 'gates.log').write_text('my own redirected output\n', encoding='utf-8')
    call(gates.main, ['check', str(w), '--gate', '0'])
    assert (w / 'gates.log').read_text(encoding='utf-8') == 'my own redirected output\n'
    assert 'gate 0' in (w / gates.HISTORY).read_text(encoding='utf-8')


def test_gate6_check_deck_uses_the_final_renders():
    src = (S / 'gates.py').read_text(encoding='utf-8')
    assert "rd0 = latest_round(work / 'renders', 'final')" in src and "extra += ['--renders', str(rd0)]" in src


# ------------------------------------------------------------------ studio

def test_studio_new_without_style_says_what_was_not_made(tmp_path):
    import studio
    code, out = call(studio.main, ['new', str(tmp_path / 'n'), '--kind', 'business', '--fonts'])
    assert code == 0 and 'no starter deck.json' in out and '--fonts: skipped' in out and 'studio.py fonts' in out.replace(str(S) + '/', '')
    assert not (tmp_path / 'n/deck.json').exists()


def test_studio_fonts_takes_the_style_from_the_genome(tmp_path):
    import studio
    w = tmp_path / 'f'
    (w / 'design').mkdir(parents=True)
    assert studio.deck_style_source(w) is None
    (w / 'design/genome.json').write_text(json.dumps({'route': 'boardroom-data', 'palette': {'ground': '#F5F7FA', 'ink': '#0F1722',
                                                                                             'accent': '#0E7C6B'}}), encoding='utf-8')
    call(studio.deck_style_source, w)
    st = json.loads((w / 'design/style.json').read_text(encoding='utf-8'))
    assert st['font_files'] and studio.deck_style_source(w) == str(w / 'design/style.json')


def test_studio_final_runs_one_check_with_renders(tmp_path):
    if not shutil.which('soffice') and not shutil.which('libreoffice'):
        pytest.skip('LibreOffice not installed')
    import studio
    ex = tmp_path / 'ex'
    shutil.copytree(SKILL / 'examples/genome-construct', ex)
    for cmd in ([S / 'genome.py', 'compile', ex / 'design/genome.json'], [ex / 'make_deck.py']):
        subprocess.run([sys.executable, *map(str, cmd)], check=True, capture_output=True, cwd=ex)
    code, out = call(studio.main, ['final', str(ex)])
    assert out.count('RESULT:') == 1 and 'the one final check' in out, out[-1500:]
    assert (ex / 'deck/final-check.txt').is_file() and code == 0


# ------------------------------------------------------------------ components, directions, check_deck hint

def test_timeline_labels_have_their_own_scoped_role(build):
    spec = {'type': {'cardtitle': {'size': 48}, 'timeline.cardtitle': {'size': 20}}, 'slides': [{'shapes': [
        {'type': 'timeline', 'name': 'tl', 'x': 1, 'y': 3, 'w': 10, 'nodes': [{'t': '2024'}, {'t': '2025'}, {'t': '2026'}], 'active': 1}]}]}
    _, slides, _ = build(spec)
    t0 = named(slides[0], 'tl.t0') if named(slides[0], 'tl.t0') is not None else named(slides[0], '!!tl.t0')
    sizes = {r.get('sz') for r in t0.iter('{%s}rPr' % NS['a'])}
    assert sizes == {'2000'}


def test_directions_md_has_no_dangling_dash(tmp_path):
    import directions
    md = tmp_path / 'd.md'
    directions.write_md({'directions': [{'id': 'A', 'name': 'x', 'composition': 'grid'},
                                        {'id': 'B', 'name': 'y', 'composition': 'split', 'composition_note': 'photo right'}]}, md)
    t = md.read_text(encoding='utf-8')
    assert '- composition: grid\n' in t and '- composition: split — photo right' in t


def test_check_deck_hints_to_rename_a_film_that_shares_its_editable_name():
    src = (S / 'check_deck.py').read_text(encoding='utf-8')
    assert 'name the film and its editable layer differently' in src
    doc = (SKILL / 'references/signature-moments.md').read_text(encoding='utf-8')
    assert 'Name the film and its editable layer differently' in doc and 'import manimgx as m' in doc
    assert 'frame_width has no setter' in doc and 'pixel_width' in doc


# ------------------------------------------------------------------ v5.3.1 #6: Anatomy anchors (untested until now)

ANCHOR_JS = r"""
import { readFileSync } from 'fs';
const src = readFileSync(process.argv[2], 'utf8');
const fn = src.slice(src.indexOf('function anchorsAt'), src.indexOf('// Runs in the page'));
const figureError = (m) => { throw new Error('FIGURE ERROR: ' + m); };
const anchorsAt = new Function('figureError', fn + '; return anchorsAt;')(figureError);
const out = {};
out.obj = anchorsAt({anchors: {a: [1, 2]}}, 0);
out.fn = anchorsAt({anchors: (t) => ({b: {x: t, y: 3}})}, 5);
out.none = anchorsAt({}, 0);
for (const [k, bad] of Object.entries({nested: {c: {p: [1, 2]}}, list: [[1, 2]], nan: {d: ['x', 1]}})) {
  try { anchorsAt({anchors: bad}, 0); out[k] = 'accepted'; } catch (e) { out[k] = e.message; }
}
console.log(JSON.stringify(out));
"""


def test_anatomy_anchors_accept_points_and_functions_and_name_a_bad_anchor(tmp_path):
    node = shutil.which('node')
    if not node:
        pytest.skip('node not installed')
    js = tmp_path / 'a.mjs'
    js.write_text(ANCHOR_JS, encoding='utf-8')
    r = subprocess.run([node, str(js), str(S / 'anatomy/film.mjs')], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o['obj'] == {'a': [1, 2]} and o['fn'] == {'b': [5, 3]} and o['none'] == {}
    assert 'anchor "c"' in o['nested'] and 'must be an object' in o['list'] and 'anchor "d"' in o['nan']


def test_anatomy_film_warns_when_anchors_were_not_exported():
    src = (S / 'anatomy_film.py').read_text(encoding='utf-8')
    assert "WARN the figure mentions anchors but none were exported" in src


# ------------------------------------------------------------------ the worked example

def test_worked_example_routes_compiles_and_builds(tmp_path, build):
    import genome
    import route
    ex = tmp_path / 'ex'
    shutil.copytree(SKILL / 'examples/genome-construct', ex)
    dec = route.route(ex)
    assert dec['chosen'] == 'boardroom-data' and 'studio-pop' in dec['rejected']
    st = genome.compile_genome(json.loads((ex / 'design/genome.json').read_text(encoding='utf-8')), ex)
    (ex / 'design/style.json').write_text(json.dumps(st), encoding='utf-8')
    subprocess.run([sys.executable, str(ex / 'make_deck.py')], check=True, capture_output=True)
    spec = json.loads((ex / 'deck.json').read_text(encoding='utf-8'))
    spec['style'] = str(ex / 'design/style.json')
    import os
    cwd = os.getcwd()
    os.chdir(ex)
    try:
        _, slides, out = build(spec, 'example')
    finally:
        os.chdir(cwd)
    assert len(slides) == 3 and named(slides[2], '!!teu.cap') is not None
    assert (SKILL / 'examples/genome-construct/contact.jpg').is_file()
