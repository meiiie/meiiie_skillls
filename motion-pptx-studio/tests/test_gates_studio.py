import contextlib
import io
import json
from pathlib import Path

import pytest

import gates
import studio


def call(fn, *args):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            r = fn(*args)
            code = r if isinstance(r, int) else (0 if r in (None, True) else 1)
        except SystemExit as e:
            code = e.code or 0
    return code, buf.getvalue()


@pytest.mark.parametrize('kind', ['heritage', 'product', 'pitch', 'business', 'education', 'event', 'other'])
def test_init_accepts_every_kind(tmp_path, kind):
    code, out = call(gates.main, ['init', str(tmp_path / kind), '--kind', kind])
    assert code == 0
    assert f'deliverable_kind: {kind}' in (tmp_path / kind / 'brief.md').read_text()


def test_studio_new_builds_a_starter(tmp_path):
    work = tmp_path / 'w'
    code, out = call(studio.main, ['new', str(work), '--kind', 'product', '--style', 'noir-product', '--title', 'Sản phẩm mới'])
    assert code == 0
    assert (work / 'design' / 'style.json').exists()
    spec = json.loads((work / 'deck.json').read_text())
    assert spec['style'] == 'design/style.json' and len(spec['slides']) == 5
    code, out = call(studio.main, ['build', str(work), '--no-render'])
    assert (work / 'deck' / 'preview-all.pptx').exists()   # v5.4: no --group = the whole deck
    assert 'RESULT' in out and 'system:' in out
    assert code == 0, out


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def storyboard(rows, cite=True, layout='split'):
    head = ('- target: 6 min · budget: 700 words\n- anchor: "Hỏi trước"\n'
            '- colour arc: S1-S4 #0E0A07 → S5-S9 #F1E4C8\n- circular close: slide 1 again\n\n'
            '| # | scene | keyframe role | layout | layers | visual | on-slide text | source | words | morph ms |\n'
            '|---|---|---|---|---|---|---|---|---|---|\n')
    body = ''
    for i in range(1, rows + 1):
        sc = f'S{(i - 1) // 3 + 1}'
        body += (f'| {i} | {sc} | K{(i - 1) % 3 + 1} | {layout} | !!sig | drawn:sig{(i - 1) // 3} | Hỏi trước rồi mới làm, một câu đủ dài '
                 f'| {"1.1" if cite else "-"} | 20 | 1300 |\n')
    return head + body


def test_gate4_fact_ids_in_source_column_and_repeated_layout_pass(tmp_path):
    work = tmp_path / 'w'
    call(gates.main, ['init', str(work), '--kind', 'other'])
    write(work / 'research' / 'facts.md', '| 1.1 | một sự thật | (S1) https://example.org | [verified] |\n')
    write(work / 'storyboard.md', storyboard(27))
    write(work / 'motion.json', '{}')
    b = (work / 'brief.md').read_text().replace('talk_minutes: TODO (hard limit of the video or talk; ask, else write the default you chose)',
                                                 'talk_minutes: 6')
    write(work / 'brief.md', b)
    code, out = call(gates.g4, work)
    assert 'cite a fact ID' not in ''.join(l for l in out.splitlines() if 'FAIL' in l), out
    assert 'layout' not in ''.join(l for l in out.splitlines() if 'FAIL' in l), out


def test_gate4_still_needs_sources(tmp_path):
    work = tmp_path / 'w'
    call(gates.main, ['init', str(work), '--kind', 'other'])
    write(work / 'research' / 'facts.md', '| 1.1 | một sự thật | (S1) https://example.org | [verified] |\n')
    write(work / 'storyboard.md', storyboard(27, cite=False))
    code, out = call(gates.g4, work)
    assert any('FAIL' in l and 'fact ID' in l for l in out.splitlines()), out


def test_gate3_needs_signature_and_compare(tmp_path):
    work = tmp_path / 'w'
    call(gates.main, ['init', str(work), '--kind', 'product'])
    code, out = call(gates.g3, work)
    assert 'signature' in out and 'compare' in out
