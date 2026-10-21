"""Build a speaker-script .docx from slide notes and a scene list.

Usage:
  python3 script_docx.py --notes NOTES.txt --scenes SCENES.json --out script.docx
      [--title TEXT] [--subtitle TEXT] [--timing timing.json]
      [--wpm-low 130] [--wpm-high 150] [--pause "[ngừng 2 giây]"]

NOTES.txt is split on '##### N' headings (one block per slide; `ooxml.py notes-get` writes it).
SCENES.json is a list of {"name", "start", "end"} objects; start and end are deck positions.
Spoken words and pauses are counted exactly like words_budget.py: lines that begin with
Nguồn/Source/Ảnh/Photo/Motion/Ghi chú/Note/Cue/Credit are directions or sources (grey, not read),
[bracketed] text is not spoken, and "[ngừng N giây]" / "[pause Ns]" add N seconds.
--pause is kept for compatibility and ignored (pause seconds are parsed from the marks).
"""
import argparse
import json
import re
from pathlib import Path

import sys

from docx import Document
from docx.shared import Pt, RGBColor

# Spoken-rate band used for the timing range (words per minute). The low rate
# is the longer estimate. Vietnamese notes are counted by whitespace-separated
# tokens, which tracks syllables for this script style.
DEFAULT_WPM = (130, 150)
PAUSE_SECONDS = 2
DEFAULT_PAUSE = '[ngừng 2 giây]'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from words_budget import SKIP, spoken  # one counting rule for plan, measure and the script document


# v5.6 (I20/I35): fact tags help the author trace numbers; they are not read aloud, so the read-aloud
# text drops them and an appendix lists them by page
FACT_TAG = re.compile(r'\s*\[(?:fact\s*)?\d+\.\d+[a-z]?(?:\s*[,;/]\s*(?:fact\s*)?\d+\.\d+[a-z]?)*\]', re.I)
FACT_ID = re.compile(r'\d+\.\d+[a-z]?')


def strip_facts(line):
    """(line without fact tags, [fact ids])"""
    ids = [i for m in FACT_TAG.finditer(line) for i in FACT_ID.findall(m.group(0))]
    return FACT_TAG.sub('', line).rstrip(), ids


def kind(line):
    return 'src' if SKIP.match(line) else 'say'


def words(line):
    return spoken(line)[0]


def pause_seconds(line):
    return spoken(line)[1]


def load_notes(path):
    text = Path(path).read_text(encoding='utf-8')
    slides = []
    for blk in text.split('##### ')[1:]:
        head, _, body = blk.partition('\n')
        n = int(head.split()[0])
        slides.append((n, [line for line in body.strip().split('\n') if line.strip()]))
    return slides


def load_scenes(path):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(raw, list) or not raw:
        raise ValueError('scenes file must be a non-empty list')
    scenes = []
    for item in raw:
        name = item['name']
        start, end = int(item['start']), int(item['end'])
        if not isinstance(name, str) or not name or start < 1 or end < start:
            raise ValueError('each scene needs a name and a slide range start..end')
        scenes.append((name, start, end))
    return scenes


def fmt(seconds):
    return f"{int(seconds // 60)}:{int(round(seconds % 60)):02d}"


def build(notes, scenes, out, title, subtitle, timing, wpm_low, wpm_high, pauses, morph_s=1.3, keep_facts=False):
    slides = load_notes(notes)
    scene_rows = load_scenes(scenes)
    wpm = (wpm_low, wpm_high)
    stat = []
    tot_w = 0
    tot_p = 0
    for name, start, end in scene_rows:
        w = p = 0
        for n, lines in slides:
            if start <= n <= end:
                for line in lines:
                    if kind(line) == 'say':
                        w += words(line)
                        p += pause_seconds(line)
        tot_w += w
        tot_p += p
        stat.append((name, start, end, w, p, w / wpm[1] * 60 + p, w / wpm[0] * 60 + p))
    lo = tot_w / wpm[1] * 60 + tot_p
    hi = tot_w / wpm[0] * 60 + tot_p
    pages = max(end for _, _, end in scene_rows)
    trans = round(pages * morph_s, 1)   # v5.6 (I34): the time if the speaker waits for every transition
    payload = {
        'transitions_s': trans, 'hi_with_transitions': fmt(hi + trans),
        'words': tot_w,
        'pauses': tot_p,
        'lo': fmt(lo),
        'hi': fmt(hi),
        'scenes': [(row[0], row[3], row[4], fmt(row[5]), fmt(row[6])) for row in stat],
    }
    timing_path = Path(timing) if timing else Path(out).with_suffix('.timing.json')
    timing_path.parent.mkdir(parents=True, exist_ok=True)
    timing_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    document = Document()
    style = document.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    document.add_heading(title, 0)
    if subtitle:
        document.add_paragraph(subtitle)
    pause_label = pauses[0]
    document.add_paragraph(
        f'Bài trình bày {pages} trang chiếu, {len(scene_rows)} cảnh. '
        f'Lời đọc khoảng {tot_w} từ và {tot_p:g} giây ngừng có đánh dấu. '
        f'Ước tính thời gian nói: {fmt(lo)} – {fmt(hi)} '
        f'(tốc độ {wpm[1]}–{wpm[0]} từ/phút, đã cộng các lần ngừng). '
        f'Nếu dừng lời ở mỗi lần chuyển cảnh ({pages} lần × {morph_s:g} giây ≈ {trans:g} giây): '
        f'{fmt(lo + trans)} – {fmt(hi + trans)}; nói tiếp trong lúc chuyển cảnh thì giữ được mức trên.'
    )
    document.add_paragraph(
        'Quy ước: chữ thường là lời đọc; [ngừng N giây] và chỉ dẫn trong ngoặc vuông không đọc; '
        'dòng in nghiêng màu xám là nguồn và ghi chú, không đọc.'
    )
    table = document.add_table(rows=1, cols=4)
    table.style = 'Light Grid Accent 1'
    for cell, heading in zip(table.rows[0].cells, ['Cảnh', 'Trang', 'Số từ', 'Thời gian ước tính']):
        cell.text = heading
    for row in stat:
        cells = table.add_row().cells
        cells[0].text = row[0]
        cells[1].text = f'{row[1]}–{row[2]}' if row[1] != row[2] else str(row[1])
        cells[2].text = str(row[3])
        cells[3].text = f'{fmt(row[5])} – {fmt(row[6])}'
    total = table.add_row().cells
    total[0].text = 'Tổng'
    total[2].text = str(tot_w)
    total[3].text = f'{fmt(lo)} – {fmt(hi)}'
    facts_by_page = {}
    for row in stat:
        document.add_heading(f'{row[0]}  ·  khoảng {fmt(row[5])} – {fmt(row[6])}', 1)
        for n, lines in slides:
            if row[1] <= n <= row[2]:
                heading = document.add_paragraph()
                run = heading.add_run(f'Trang {n}')
                run.bold = True
                run.font.color.rgb = RGBColor(0x8A, 0x5A, 0x10)
                for line in lines:
                    if not keep_facts:
                        line, ids = strip_facts(line)
                        facts_by_page.setdefault(n, []).extend(ids)
                        if not line.strip():
                            continue
                    paragraph = document.add_paragraph()
                    run = paragraph.add_run(line)
                    if kind(line) == 'src':
                        run.italic = True
                        run.font.size = Pt(9)
                        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
                    elif line.startswith('['):
                        run.bold = True
                        run.font.color.rgb = RGBColor(0xA0, 0x20, 0x20)
    if facts_by_page and any(facts_by_page.values()):
        document.add_heading('Phụ lục: mã dữ kiện theo trang (không đọc)', 1)
        for n in sorted(facts_by_page):
            if facts_by_page[n]:
                para = document.add_paragraph()
                run = para.add_run(f'Trang {n}: ' + ', '.join(dict.fromkeys(facts_by_page[n])))
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(out_path)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build a speaker-script .docx from notes and a scene list.')
    parser.add_argument('--notes', required=True, help="slide notes split on '##### N' headings")
    parser.add_argument('--scenes', required=True, help='JSON list of {name, start, end} scene ranges')
    parser.add_argument('--out', required=True, help='output .docx path')
    parser.add_argument('--title', default='Kịch bản thuyết trình', help='document title')
    parser.add_argument('--subtitle', default='', help='optional line under the title')
    parser.add_argument('--timing', help='timing JSON path (default: beside the .docx)')
    parser.add_argument('--wpm-low', type=int, default=DEFAULT_WPM[0], help='slower words-per-minute bound')
    parser.add_argument('--wpm-high', type=int, default=DEFAULT_WPM[1], help='faster words-per-minute bound')
    parser.add_argument('--pause', action='append', default=None, help='pause mark to count (repeatable; default [ngừng 2 giây])')
    parser.add_argument('--morph-s', type=float, default=1.3, help='seconds per slide transition (for the "pause at every transition" estimate)')
    parser.add_argument('--keep-facts', action='store_true', help='keep [fact X.Y] tags in the read-aloud text (default: strip, list in an appendix)')
    args = parser.parse_args(argv)
    if args.wpm_low < 1 or args.wpm_high < 1:
        raise SystemExit('speaking rates must be positive')
    pauses = args.pause or [DEFAULT_PAUSE]
    try:
        build(args.notes, args.scenes, args.out, args.title, args.subtitle, args.timing, args.wpm_low, args.wpm_high, pauses,
              morph_s=args.morph_s, keep_facts=args.keep_facts)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit('could not build the script: ' + str(error))


if __name__ == '__main__':
    main()
