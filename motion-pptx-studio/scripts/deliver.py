"""Assemble WORK/deliver/: final pptx, speaker-script docx, fonts + licence + install README, CREDITS, zip.

  python deliver.py WORK --deck WORK/deck/final.pptx --name "CaTru_Motion" --title "Ca trù — kịch bản"
         [--scenes WORK/scenes.json] [--subtitle "..."]
Steps: copies the deck -> exports notes (ooxml.py notes-get) -> script_docx.py -> copies static fonts
(warns on variable fonts) + licence files -> CREDITS.md -> zip. Run check_deck.py and gates.py --gate 6 after.
scenes.json: [{"name": "Cảnh 1 · Mở", "start": 1, "end": 3}, ...] (deck positions). Without it, one
scene per storyboard scene id is derived from storyboard.md when possible, else one block for all.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

FONT_README = """FONTS — cài trước khi mở file PowerPoint / install before opening the deck

Windows : chọn tất cả file .ttf → chuột phải → "Install for all users" (Cài cho mọi người dùng).
macOS   : nhấp đúp từng file .ttf → "Install Font" (Font Book).
Linux   : cp *.ttf ~/.local/share/fonts/ && fc-cache -f
Sau khi cài, đóng và mở lại PowerPoint. / Restart PowerPoint after installing.
These are static instances (not variable fonts) so PowerPoint picks the right weight.
Licence: SIL Open Font License 1.1 (see the OFL*.txt files).
"""


def scenes_from_storyboard(work):
    sb = (work / 'storyboard.md').read_text(encoding='utf-8') if (work / 'storyboard.md').is_file() else ''
    rows = [l for l in sb.splitlines() if re.match(r'\s*\|\s*\d+\s*\|', l)]
    out = []
    for l in rows:
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        n, scene = int(cells[0]), cells[1]
        if out and out[-1]['name'] == scene:
            out[-1]['end'] = n
        else:
            out.append({'name': scene, 'start': n, 'end': n})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work')
    ap.add_argument('--deck', required=True)
    ap.add_argument('--name', required=True, help='file stem, ASCII preferred (e.g. CaTru_Motion)')
    ap.add_argument('--title', required=True)
    ap.add_argument('--subtitle', default='')
    ap.add_argument('--scenes')
    a = ap.parse_args(argv)
    work = Path(a.work).resolve()
    d = work / 'deliver'
    d.mkdir(exist_ok=True)
    pptx = d / f'{a.name}.pptx'
    shutil.copy(a.deck, pptx)
    tmp = work / 'deck' / '_deliver_unpacked'
    shutil.rmtree(tmp, ignore_errors=True)
    py = sys.executable
    subprocess.run([py, str(HERE / 'ooxml.py'), 'unpack', str(pptx), str(tmp)], check=True, capture_output=True)
    notes = d / 'notes.txt'
    subprocess.run([py, str(HERE / 'ooxml.py'), 'notes-get', str(tmp), '--out', str(notes)], check=True, capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if a.scenes:
        scenes = Path(a.scenes)
    else:
        sc = scenes_from_storyboard(work)
        if not sc:
            n = len(re.findall(r'^##### ', notes.read_text(encoding='utf-8'), re.M))
            sc = [{'name': a.title, 'start': 1, 'end': n}]
        scenes = d / 'scenes.json'
        scenes.write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding='utf-8')
    docx = d / f'{a.name}_KichBan.docx'
    r = subprocess.run([py, str(HERE / 'script_docx.py'), '--notes', str(notes), '--scenes', str(scenes), '--out', str(docx),
                        '--title', a.title, '--subtitle', a.subtitle], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        sys.exit('script_docx failed')
    fd = d / 'fonts'
    fd.mkdir(exist_ok=True)
    nfont = 0
    for f in sorted((work / 'fonts').glob('*')):
        if f.suffix.lower() in ('.ttf', '.otf'):
            if '[' in f.name or 'Variable' in f.name:
                print(f'WARN: {f.name} looks like a VARIABLE font — ship static instances (fonttools varLib.instancer)')
            shutil.copy(f, fd / f.name)
            nfont += 1
        elif re.search(r'ofl|licen[cs]e', f.name, re.I):
            shutil.copy(f, fd / f.name)
    (fd / 'README_FONTS.txt').write_text(FONT_README, encoding='utf-8')
    cr = work / 'assets' / 'CREDITS.md'
    if cr.is_file():
        shutil.copy(cr, d / 'CREDITS.md')
    else:
        print('WARN: no assets/CREDITS.md')
    z = d / f'{a.name}.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in [pptx, docx, d / 'CREDITS.md'] + sorted(fd.iterdir()):
            if p.exists():
                zf.write(p, p.relative_to(d))
    print(f'deliver/: {pptx.name}, {docx.name}, fonts/ ({nfont} fonts), CREDITS.md, {z.name} ({z.stat().st_size / 1e6:.1f} MB)')
    print('NEXT: python gates.py check WORK --gate 6')


if __name__ == '__main__':
    main()
