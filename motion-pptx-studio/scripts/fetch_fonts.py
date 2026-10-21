"""Download the OFL fonts a style pack needs, as static TTFs, and install them for rendering.

  python3 fetch_fonts.py --style noir-product --out WORK/fonts [--install] [--check vi]
  python3 fetch_fonts.py --family "Be Vietnam Pro:400,700" --out WORK/fonts --install

Why: a deck rendered with a fallback font is judged on the wrong typography, and a
deck delivered without its fonts falls back on the presenter's machine. Every style
pack lists its families and weights; this script fetches exactly those.

Sources, tried in order (agent sandboxes often allow one and not the other):
  1. npm registry: @expo-google-fonts/<slug> ships Google Fonts as static TTFs with
     full glyph sets (Vietnamese included) and the OFL text (LICENSE_FONT).
  2. GitHub google/fonts static files (ofl/<slug>/static/<Family>-<Style>.ttf).
Static files are what PowerPoint handles well; variable fonts are not used.
The OFL text is written next to the fonts as OFL_<Family>.txt.
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLES = HERE.parent / 'assets' / 'styles'
WEIGHT_NAMES = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium',
                600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}


def slug(family):
    return re.sub(r'[^a-z0-9]+', '-', family.lower()).strip('-')


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={'User-Agent': 'motion-pptx-studio/4'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_weights(spec):
    """'400,700,400i' -> [(400, False), (700, False), (400, True)]"""
    out = []
    for w in spec.split(','):
        w = w.strip()
        if not w:
            continue
        italic = w.endswith('i')
        out.append((int(w.rstrip('i')), italic))
    return out


def from_npm(family, weights, out):
    meta = json.loads(fetch(f'https://registry.npmjs.org/@expo-google-fonts/{slug(family)}/latest'))
    blob = fetch(meta['dist']['tarball'], timeout=300)
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz')
    members = {Path(m.name).name: m for m in tf.getmembers() if m.isfile()}
    got = []
    for w, italic in weights:
        name = f'{family.replace(" ", "")}_{w}{WEIGHT_NAMES[w]}{"_Italic" if italic else ""}.ttf'
        m = members.get(name)
        if m is None:
            raise FileNotFoundError(f'{name} not in the npm package for {family}')
        dest = out / name
        dest.write_bytes(tf.extractfile(m).read())
        got.append(dest)
    lic = members.get('LICENSE_FONT')
    if lic is not None:
        (out / f'OFL_{family.replace(" ", "")}.txt').write_bytes(tf.extractfile(lic).read())
    return got


def from_github(family, weights, out):
    base = f'https://github.com/google/fonts/raw/main/ofl/{family.replace(" ", "").lower()}'
    got = []
    for w, italic in weights:
        style = WEIGHT_NAMES[w] if not italic else (WEIGHT_NAMES[w] + 'Italic' if w != 400 else 'Italic')
        fname = f'{family.replace(" ", "")}-{style}.ttf'
        data = None
        for url in (f'{base}/static/{fname}', f'{base}/{fname}'):
            try:
                data = fetch(url)
                break
            except Exception:  # noqa: BLE001 - try the next location
                continue
        if data is None:
            raise FileNotFoundError(fname)
        dest = out / fname
        dest.write_bytes(data)
        got.append(dest)
    try:
        (out / f'OFL_{family.replace(" ", "")}.txt').write_bytes(fetch(f'{base}/OFL.txt'))
    except Exception:  # noqa: BLE001
        pass
    return got


def fetch_family(family, weights, out):
    errors = []
    for fn in (from_npm, from_github):
        try:
            return fn(family, weights, out), fn.__name__
        except Exception as e:  # noqa: BLE001 - report every source that failed
            errors.append(f'{fn.__name__}: {e}')
    raise SystemExit(f'could not fetch {family}: ' + ' | '.join(errors) +
                     '\nDownload the static TTFs by hand (fonts.google.com) into the fonts folder.')


def install(files):
    if sys.platform == 'darwin':
        dest = Path.home() / 'Library' / 'Fonts'
    elif os.name == 'nt':
        dest = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'Microsoft' / 'Windows' / 'Fonts'
    else:
        dest = Path.home() / '.local' / 'share' / 'fonts'
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy(f, dest / f.name)
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f', str(dest)], capture_output=True)
    return dest


def style_families(name):
    p = Path(name)
    if not p.suffix:
        p = STYLES / f'{name}.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    return [(f['family'], f['weights']) for f in data.get('font_files', [])]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--style', help='style pack name or path; fetches every family it lists')
    ap.add_argument('--family', action='append', default=[], help='"Family:400,700,400i" (repeatable)')
    ap.add_argument('--out', required=True, help='folder for the TTFs and OFL texts (e.g. WORK/fonts)')
    ap.add_argument('--install', action='store_true', help='also install for the current user and refresh fontconfig')
    ap.add_argument('--check', metavar='LANG', help='run check_fonts.py on the result (e.g. vi)')
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    wanted = style_families(a.style) if a.style else []
    for f in a.family:
        fam, _, ws = f.partition(':')
        wanted.append((fam.strip(), ws or '400,700'))
    if not wanted:
        ap.error('give --style or --family')
    files = []
    for fam, ws in wanted:
        got, src = fetch_family(fam, parse_weights(ws), out)
        print(f'{fam}: {len(got)} file(s) via {src}')
        files += got
    if a.install:
        print('installed to', install(files))
    if a.check:
        r = subprocess.run([sys.executable, str(HERE / 'check_fonts.py'), *map(str, files), '--lang', a.check],
                           capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            return r.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
