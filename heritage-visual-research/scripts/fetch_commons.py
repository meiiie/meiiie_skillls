"""Search and download openly licensed images WITH their licence metadata.

Two steps on purpose: (1) pull many candidates and LOOK at them on a contact sheet,
(2) keep only the ones you verified against the fact file, which writes the CREDITS row.

  python fetch_commons.py search "ca trù" [--source commons,openverse] [--limit 40]
         [--out assets/candidates] [--min-width 1000] [--allow-nc]
      -> downloads thumbnails to OUT/, writes OUT/candidates.json + OUT/candidates.tsv
         (filename<TAB>licence · author, usable by contact_sheet.py --captions) and
         OUT/contact.jpg. Search in BOTH the local language and English
         ("ca trù", "ca tru", "đàn đáy", "dan day", "Ca tru singing").
  python fetch_commons.py keep CANDIDATE_ID --as 04_dan_day_real.jpg --why "3 strings, 3 staggered pegs (UNESCO 00309)"
         [--candidates assets/candidates/candidates.json] [--dest assets] [--credits assets/CREDITS.md]
         [--uncertain]
      -> downloads the full-size file to DEST (or DEST/_uncertain/ with --uncertain) and appends
         a row to CREDITS.md: file | subject | why accurate | source page | author | licence |
         attribution text | size.

Licences: kept by default = CC0, Public Domain / PDM, CC BY, CC BY-SA. NC / ND are skipped
unless --allow-nc (a contest video that is broadcast on TV is not "non-commercial" for sure).
Commons metadata comes from the Commons API (extmetadata); Openverse indexes Flickr, museums
and others (https://api.openverse.org). A title or tag is NOT proof of the subject:
a Flickr set titled "Ca Tru" showed đàn tranh and sáo instead. Verify by eye.
"""
import argparse
import html
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

UA = {'User-Agent': 'motion-pptx-studio/2.0 (asset research for a presentation; https://github.com/meiiie/meiiie_skillls)'}


def get(url, binary=False, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
                return data if binary else json.loads(data.decode('utf-8'))
        except Exception as e:  # rate limits / transient errors
            if k == tries - 1:
                raise
            time.sleep(2 + 3 * k)


def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html.unescape(s or ''))).strip()


def fold(s):
    """ASCII-fold: 'đàn đáy' -> 'dan day' (many Flickr/Openverse titles have no diacritics)."""
    s = s.replace('đ', 'd').replace('Đ', 'D')
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')


def commons_query(q, loose):
    if loose or '"' in q or ' ' not in q.strip():
        return q + ' filetype:bitmap'
    return f'"{q}" filetype:bitmap'  # unquoted multi-word queries match unrelated files


def commons(query, limit):
    params = {
        'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
        'gsrsearch': query, 'gsrlimit': min(limit, 50), 'prop': 'imageinfo',
        'iiprop': 'url|size|extmetadata|mime', 'iiurlwidth': 640,
    }
    d = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params))
    out = []
    for p in (d.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        if not ii or not ii.get('mime', '').startswith('image/'):
            continue
        m = ii.get('extmetadata', {})
        g = lambda k: clean(m.get(k, {}).get('value', ''))
        out.append({
            'id': 'commons:' + p['title'].replace('File:', '', 1),
            'title': p['title'], 'source': 'commons',
            'page': ii.get('descriptionurl'), 'url': ii.get('url'), 'thumb': ii.get('thumburl') or ii.get('url'),
            'width': ii.get('width'), 'height': ii.get('height'),
            'license': g('LicenseShortName'), 'license_url': g('LicenseUrl'),
            'author': g('Artist')[:120], 'credit': g('Credit')[:200], 'description': g('ImageDescription')[:300],
            'date': g('DateTimeOriginal')[:40],
        })
    return out


def openverse(query, limit):
    params = {'q': query, 'page_size': min(limit, 20), 'mature': 'false'}
    d = get('https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(params))
    out = []
    for r in d.get('results', []):
        lic = (r.get('license') or '').lower()
        ver = r.get('license_version') or ''
        name = 'CC0' if lic == 'cc0' else 'Public Domain Mark' if lic == 'pdm' else f'CC {lic.upper()} {ver}'.strip()
        out.append({
            'id': 'openverse:' + r['id'], 'title': clean(r.get('title')), 'source': 'openverse/' + (r.get('source') or ''),
            'page': r.get('foreign_landing_url'), 'url': r.get('url'), 'thumb': r.get('thumbnail') or r.get('url'),
            'width': r.get('width'), 'height': r.get('height'),
            'license': name, 'license_url': r.get('license_url'), 'author': (r.get('creator') or '')[:120],
            'credit': r.get('attribution') or '', 'description': ', '.join(t['name'] for t in (r.get('tags') or [])[:12]),
            'date': '',
        })
    return out


def licence_ok(c, allow_nc):
    lic = (c.get('license') or '').lower().replace('-', ' ')
    if not lic:
        return False
    if re.search(r'\b(nc|nd)\b|non ?commercial|no ?deriv', lic):
        return allow_nc
    return any(k in lic for k in ('cc0', 'public domain', 'pdm', 'cc by', 'pd ', 'attribution')) or lic.startswith(('by', 'pd'))


def safe(s):
    return re.sub(r'[^\w.-]+', '_', s)[:80]


def cmd_search(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jpath = out / 'candidates.json'
    found = json.loads(jpath.read_text(encoding='utf-8')) if jpath.is_file() else []
    known = {c['id'] for c in found}
    new = []
    queries = [a.query] + ([fold(a.query)] if fold(a.query) != a.query else [])
    res = []
    for src in a.source.split(','):
        for q in queries:
            try:
                got = commons(commons_query(q, a.loose), a.limit) if src == 'commons' else openverse(q, a.limit)
            except Exception as e:
                print(f'{src}: search {q!r} failed ({e}); retry later or search the site in a browser', file=sys.stderr)
                continue
            print(f'{src}: {q!r} -> {len(got)} results')
            res += got
    if True:
        for c in res:
            if c['id'] in known:
                continue
            w = c.get('width') or 0
            c['use'] = 'full-bleed' if w >= 1920 else 'half/panel' if w >= 1000 else 'inset/icon only'
            if w < a.min_width:
                c['skip'] = f"too small ({w}px)"
            elif not licence_ok(c, a.allow_nc):
                c['skip'] = f"licence not usable: {c.get('license') or 'unknown'}"
            c['query'] = a.query
            new.append(c)
            known.add(c['id'])
    caps = []
    for i, c in enumerate(new):
        if c.get('skip'):
            continue
        ext = '.png' if (c.get('thumb') or '').lower().endswith('.png') else '.jpg'
        c['thumb_file'] = f"{len(found) + i:03d}_{safe(c['source'].split('/')[0])}_{safe(c['title'].replace('File:', ''))[:50]}{ext}"
        try:
            (out / c['thumb_file']).write_bytes(get(c['thumb'], binary=True))
        except Exception as e:
            c['skip'] = f'thumbnail download failed: {e}'
        time.sleep(0.3)
    found += new
    jpath.write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding='utf-8')
    for c in found:
        if c.get('thumb_file') and not c.get('skip'):
            caps.append(f"{c['thumb_file']}\t{c['width']}px {c.get('use', '')} · {c['license']} · {c['author'][:30]}")
    (out / 'candidates.tsv').write_text('\n'.join(caps) + '\n', encoding='utf-8')
    usable = [c for c in new if not c.get('skip')]
    print(f'{a.query!r}: {len(new)} new results, {len(usable)} usable, {len(new) - len(usable)} skipped; '
          f'{len(caps)} usable candidates in total in {out}')
    for c in usable:
        print(f"  {c['id'][:70]:70} {c['width']}x{c['height']} {c['license']} · {c['author'][:30]}")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import contact_sheet
        contact_sheet.main([str(out), '--out', str(out / 'contact.jpg'), '--cols', '5', '--width', '320',
                            '--captions', str(out / 'candidates.tsv'), '--per-sheet', '30'])
    except SystemExit:
        pass
    print('NEXT: open the contact sheet(s), compare every image with the fact file / accuracy list, then `keep` the good ones.')


def insert_row(credits, row):
    """Insert the row at the end of the first markdown table (not after later sections)."""
    lines = credits.read_text(encoding='utf-8').splitlines(keepends=True)
    last = None
    for i, l in enumerate(lines):
        if l.lstrip().startswith('|'):
            last = i
        elif last is not None and l.strip():
            break
    if last is None:
        lines.append(row)
    else:
        lines.insert(last + 1, row)
    credits.write_text(''.join(lines), encoding='utf-8')


def cmd_keep(a):
    cands = json.loads(Path(a.candidates).read_text(encoding='utf-8'))
    nfc = lambda x: unicodedata.normalize('NFC', x or '')
    want = nfc(a.id)
    match = [c for c in cands if nfc(c['id']) == want or nfc(c.get('thumb_file')) == want]
    if not match:
        match = [c for c in cands if nfc(c['id']).endswith(want)]
    if len(match) != 1:
        raise SystemExit(f'{len(match)} candidates match {a.id!r}; use the exact id (or thumb_file name) from candidates.json')
    c = match[0]
    if c.get('skip') and not a.force:
        raise SystemExit(f"candidate was skipped: {c['skip']} (use --force only if you verified the licence yourself)")
    dest = Path(a.dest) / ('_uncertain' if a.uncertain else '')
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / a.as_name
    data = get(c['url'], binary=True)
    src_ext = Path(urllib.parse.urlparse(c['url']).path).suffix.lower()
    if src_ext in ('.tif', '.tiff', '.webp', '.bmp') or target.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
        try:
            import io
            from PIL import Image
            im = Image.open(io.BytesIO(data))
            im.load()
            if target.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                target = target.with_suffix('.jpg')
            if target.suffix.lower() in ('.jpg', '.jpeg'):
                im = im.convert('RGB')
            im.save(target, quality=92)
            print(f'converted {src_ext} -> {target.suffix} (PowerPoint-safe)')
        except Exception as e:  # keep raw bytes if Pillow cannot read it
            print('WARN: could not convert:', e)
            target.write_bytes(data)
    else:
        target.write_bytes(data)
    credits = Path(a.credits)
    if not credits.is_file():
        credits.write_text('# CREDITS\n\n| file | subject | why accurate (source) | source page | author | licence | attribution text | size |\n'
                           '|---|---|---|---|---|---|---|---|\n', encoding='utf-8')
    title = clean(c['title']).replace('File:', '')
    author = clean(c['author']) or 'unknown'
    via = 'Wikimedia Commons' if c['source'] == 'commons' else (c['source'].split('/')[-1] or 'Openverse')
    attr = f'"{title}" © {author}, {c["license"]}, via {via}'
    if 'public domain' in c['license'].lower() or c['license'].upper().startswith('CC0'):
        attr = f"{author}, {c['license']} (no attribution required; credit anyway)"
    cell = lambda x: str(x).replace('|', '/').replace('\n', ' ')
    name = ('_uncertain/' if a.uncertain else '') + target.name
    row = '| ' + ' | '.join(cell(x) for x in (name, a.subject or title, a.why, c['page'], author, c['license'], attr,
                                               f"{c['width']}×{c['height']}")) + ' |\n'
    insert_row(credits, row)
    print('kept', target, '->', credits)
    if 'SA' in c['license'].upper():
        print('NOTE: BY-SA: any edited version (crop, grade, inpaint) stays BY-SA and is credited "(edited / đã chỉnh sửa)".')
    if a.uncertain:
        print('NOTE: _uncertain/: may be used only as unlabelled atmosphere, never captioned as the subject.')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('search')
    s.add_argument('query')
    s.add_argument('--source', default='commons,openverse')
    s.add_argument('--limit', type=int, default=40)
    s.add_argument('--out', default='assets/candidates')
    s.add_argument('--min-width', type=int, default=0, help='skip images narrower than this (default keeps all; small ones are tagged inset/icon only)')
    s.add_argument('--allow-nc', action='store_true')
    s.add_argument('--loose', action='store_true', help='do not wrap multi-word Commons queries in quotes')
    s = sub.add_parser('keep')
    s.add_argument('id')
    s.add_argument('--as', dest='as_name', required=True)
    s.add_argument('--why', required=True, help='why this image is accurate, with the fact-file source tag')
    s.add_argument('--subject', default='')
    s.add_argument('--candidates', default='assets/candidates/candidates.json')
    s.add_argument('--dest', default='assets')
    s.add_argument('--credits', default='assets/CREDITS.md')
    s.add_argument('--uncertain', action='store_true', help='licence ok but subject unverified: never caption it as the subject')
    s.add_argument('--force', action='store_true')
    a = ap.parse_args(argv)
    cmd_search(a) if a.cmd == 'search' else cmd_keep(a)


if __name__ == '__main__':
    main()
