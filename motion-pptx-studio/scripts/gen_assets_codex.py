"""Second asset source: AI images made by the Codex CLI's built-in image_gen tool.

Use it AFTER licensed sourcing (fetch_commons.py) when real, licensed imagery runs short, and only for
material that is not a factual claim: textures, abstract backgrounds, object renders and scene plates.
Every file is labelled AI-generated in assets/CREDITS.md and in a sidecar JSON next to it.

  python3 gen_assets_codex.py lint  "brushed aluminium texture, cool white and blue light"   # prompt rules only
  python3 gen_assets_codex.py plan  WORK --spec WORK/design/codex-assets.json                # lint every item, no calls
  python3 gen_assets_codex.py run   WORK --spec WORK/design/codex-assets.json [--jobs 2] [--only name,name]
                                    [--codex PATH] [--timeout 600] [--force]
  python3 gen_assets_codex.py probe                     # is the CLI there, logged in, image_gen on?

spec (JSON list):
  [{"name": "ground-alu", "kind": "texture|background|object|plate", "aspect": "16:9|4:3|1:1|3:4|9:16",
    "prompt": "brushed anodised aluminium, fine diagonal grain, white to #1464F4 light",
    "why": "chapter-2 ground: white-and-blue style", "use": "S4-S6 background"}]

Kinds (what is allowed)
  texture     a material surface: metal, paper, concrete, carbon weave, film grain, water caustics
  background  an abstract field: light leaks, gradients, bokeh, topographic lines, data-like particles
  object      a render of a GENERIC object of the subject (a battery cell, a cable, a wheel hub) with no brand,
              no logo, no badge, no readable text; never "the" product (no real model is drawn by a machine)
  plate       an atmospheric scene plate: an unnamed empty road at dawn, a generic coastline, a misty plain;
              never a named real place shown as a document, never an event that happened

Banned (the lint refuses the prompt; references/asset-sourcing.md §AI):
  clichés     books, scales/justice scales, lightbulbs, handshakes, robots/humanoids, globes held by hands,
              puzzle pieces, rockets for "growth", brains for "AI", chess pieces, gears-in-a-head
  identity    logos, brand names, wordmarks, badges, fake UI with a real brand, real people by name, faces
              of public figures, "photo of <person>"
  fake facts  "photo of the <named> factory/showroom/launch/event", "realistic photo of <real model>",
              documentary/press/news photo, charts with numbers, maps with borders (draw those yourself)

Mechanics (tested with codex-cli 0.162.1, 2026-10): `codex exec` runs an agent turn; the agent calls the
built-in `image_gen` tool, which writes PNGs to $CODEX_HOME/generated_images/<session id>/exec-*.png
(no OPENAI_API_KEY needed when the CLI is logged in). This script snapshots that folder, runs one session
per asset, takes the new PNG of that session, converts it to an sRGB JPEG with a long side <= 2560 px,
writes assets/gen/<name>.jpg + <name>.json and appends a CREDITS row (licence "AI-generated").
About 25-60 s per image. Failure (no CLI, not logged in, feature off, network) exits 2 with the honest
fallback: make_assets.py ground/pattern/glow (procedural), drawn SVG (make_assets.py foil/layers),
or a smaller deck (asset_scarcity in brief.md). Never fill the gap with unlicensed web images.
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KINDS = {
    'texture': 'a seamless material texture filling the whole frame, no objects',
    'background': 'an abstract background field, no objects, generous calm negative space for slide text',
    'object': 'a studio render of one generic object on a plain seamless backdrop, no brand marks, no badge, no text',
    'plate': 'an atmospheric scene plate with no people, no vehicles with badges, no signs, no readable text',
}
ASPECTS = ('16:9', '4:3', '1:1', '3:4', '9:16', '4:5')
BANNED = [  # (regex, reason)
    (r'\bbooks?\b|\bbookshel', 'cliché: books stand for "knowledge"'),
    (r'\bscales?\b(?! model)|\bjustice\b', 'cliché: scales stand for "balance/law"'),
    (r'light ?bulbs?|\bbulbs?\b', 'cliché: lightbulb = "idea"'),
    (r'hand ?shakes?|shaking hands', 'cliché: handshake = "partnership"'),
    (r'\brobots?\b|\bhumanoid|\bandroid\b|\bcyborg', 'cliché: robot = "AI/automation" (draw the real machine yourself)'),
    (r'\bglobes?\b|earth in (?:a |the )?hands?|hands? holding', 'cliché: globe/hands = "global/care"'),
    (r'puzzle|chess|\bbrain\b|rocket|target with arrow|dartboard', 'cliché: stock-metaphor object'),
    (r'\blogos?\b|wordmark|\bbadge|emblem|trademark|brand mark', 'identity: no logos or badges (use the real licensed file)'),
    (r'\bportrait of\b|\bphoto of (?:mr|ms|mrs|dr)\b|\bceo\b|\bpresident\b|celebrity|famous person|public figure',
     'identity: no real people'),
    (r'\b(press|news|documentary|editorial) photo|\bphotojournal', 'fake fact: a generated image is never a document'),
    (r'\bchart\b|\bgraph\b|infographic|\bmap of\b|\bborders?\b|statistic', 'fake fact: data and maps are drawn from sources, not generated'),
    (r'\b(text|caption|headline|title|slogan|letters?|numbers?|words?) (?:that )?(?:says|reading|saying)\b|"[^"]{3,}"',
     'no text in the image: slide text is set in the deck'),
]
FACTUAL = re.compile(r'\b(real|actual|authentic|official|the (?:\w+ )?(?:factory|plant|showroom|headquarters|launch|ceremony|event))\b', re.I)
SUFFIX = ('No text, no letters, no numbers, no logos, no badges, no watermarks, no people, no hands. '
          'Not a photograph of any real event, place or product.')


def lint(prompt, kind='texture', brands=()):
    """Return a list of problems with a prompt (empty = allowed)."""
    # the script adds every "no text, no logos..." itself; negations in the prompt are not requests
    p = re.sub(r'\b(?:no|without|avoid|never)\s+(?:\w+\s*,?\s*(?:or|and)?\s*){1,3}', ' ', prompt.lower())
    out = []
    if kind not in KINDS:
        out.append(f'kind {kind!r} is not one of {sorted(KINDS)}')
    for rx, why in BANNED:
        if re.search(rx, p, re.I):
            out.append(f'{why} (matched /{rx}/)')
    if FACTUAL.search(p):
        out.append('fake fact: words like "real/official/the factory/the launch" ask for a document; '
                   'say "generic", "unnamed", "abstract" instead')
    for b in brands:
        if b and re.search(r'\b' + re.escape(b.lower()) + r'\b', p):
            out.append(f'identity: the brand/subject name {b!r} is in the prompt; a generator invents a fake product')
    if len(prompt.split()) < 6:
        out.append('too short: name the material, light, palette and composition (>= 6 words)')
    return out


def full_prompt(item):
    kind = item.get('kind', 'texture')
    aspect = item.get('aspect', '16:9')
    return (f"Use your built-in image_gen tool to generate exactly ONE image, then stop. "
            f"Image: {item['prompt'].strip().rstrip('.')}. Form: {KINDS.get(kind, '')}. "
            f"Aspect ratio {aspect}, landscape if wider. {SUFFIX} "
            f"Do not write any files yourself and do not run other commands; just generate the image and reply DONE.")


def codex_home():
    return Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')


def find_codex(explicit=None):
    for c in [explicit, shutil.which('codex'), str(Path.home() / '.local/bin/codex')]:
        if c and Path(c).exists():
            return c
    return None


def probe(codex=None):
    exe = find_codex(codex)
    if not exe:
        return False, 'codex CLI not found (npm i -g @openai/codex, then codex login)'
    v = subprocess.run([exe, '--version'], capture_output=True, text=True).stdout.strip()
    feats = subprocess.run([exe, 'features', 'list'], capture_output=True, text=True).stdout
    m = re.search(r'^image_generation\s+\S+\s+(true|false)', feats, re.M)
    if m and m.group(1) != 'true':
        return False, f'{v}: feature image_generation is off (codex --enable image_generation ...)'
    if not (codex_home() / 'auth.json').exists() and not os.environ.get('OPENAI_API_KEY'):
        return False, f'{v}: not logged in (codex login)'
    return True, f'{v}: image_generation {"on" if m else "unknown"}; images land in {codex_home()}/generated_images/<session>/'


def to_jpeg(src, dst, long_side=2560):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    if max(im.size) > long_side:
        im.thumbnail((long_side, long_side), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=90, optimize=True)
    return im.size


def run_one(item, work, exe, timeout):
    gen = work / 'assets' / 'gen'
    gen.mkdir(parents=True, exist_ok=True)
    root = codex_home() / 'generated_images'
    before = {p for p in root.rglob('*.png')} if root.is_dir() else set()
    scratch = work / 'assets' / 'gen' / '.codex-run'
    scratch.mkdir(exist_ok=True)
    t0 = datetime.datetime.now()
    cmd = [exe, 'exec', '--skip-git-repo-check', '-s', 'read-only', '-C', str(scratch), full_prompt(item)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        log = r.stdout + r.stderr
    except subprocess.TimeoutExpired as e:
        return item['name'], None, f'timeout after {timeout}s'
    (gen / f'{item["name"]}.codex.log').write_text(log[-20000:], encoding='utf-8')
    sid = re.search(r'session id:\s*([0-9a-f-]{20,})', log)
    model = re.search(r'^model:\s*(\S+)', log, re.M)
    new = sorted(p for p in (root.rglob('*.png') if root.is_dir() else []) if p not in before)
    if sid:
        own = [p for p in new if sid.group(1) in str(p)]
        new = own or new
    if not new:
        return item['name'], None, 'codex ran but produced no image (see .codex.log): ' + log.strip().splitlines()[-1][:200] if log.strip() else 'no output'
    src = max(new, key=lambda p: p.stat().st_mtime)
    dst = gen / f'{item["name"]}.jpg'
    size = to_jpeg(src, dst)
    meta = {'file': f'gen/{dst.name}', 'ai_generated': True, 'tool': 'codex-cli image_gen',
            'model': model.group(1) if model else 'unknown', 'session': sid.group(1) if sid else None,
            'kind': item.get('kind'), 'prompt': item['prompt'], 'full_prompt': full_prompt(item),
            'why': item.get('why', ''), 'use': item.get('use', ''), 'source_png': str(src),
            'made': t0.isoformat(timespec='seconds'), 'size': list(size)}
    (gen / f'{item["name"]}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    return item['name'], meta, None


def credits_row(meta):
    w, h = meta['size']
    return (f"| {meta['file']} | AI-generated {meta['kind']}: {meta['prompt'][:80]} | not a fact: {meta['why'] or 'atmosphere'} "
            f"| local: {meta['file'].replace('.jpg', '.json')} (prompt + session) | Codex CLI image_gen ({meta['model']}) "
            f"| AI-generated (no third-party rights claimed; label as AI) | \"Ảnh tạo bằng AI / AI-generated image\" | {w}×{h} |")


def append_credits(work, metas):
    cr = work / 'assets' / 'CREDITS.md'
    text = cr.read_text(encoding='utf-8') if cr.exists() else '# CREDITS\n\n| file | subject | why accurate (source) | source page | author | licence | attribution text | size |\n|---|---|---|---|---|---|---|---|\n'
    rows = [credits_row(m) for m in metas if f"| {m['file']} |" not in text]
    if not rows:
        return 0
    lines = text.splitlines()
    # insert after the last row of the first file|licence table
    idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith('|') and 'file' in l.lower() and ('licen' in l.lower()):
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith('|'):
                j += 1
            idx = j
            break
    if idx is None:
        lines += ['', '| file | subject | why accurate (source) | source page | author | licence | attribution text | size |', '|---|---|---|---|---|---|---|---|']
        idx = len(lines)
    lines[idx:idx] = rows
    cr.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return len(rows)


def load_spec(path):
    spec = json.loads(Path(path).read_text(encoding='utf-8'))
    items = spec['items'] if isinstance(spec, dict) else spec
    brands = spec.get('brands', []) if isinstance(spec, dict) else []
    for it in items:
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{1,40}', it.get('name', '')):
            raise SystemExit(f'bad name {it.get("name")!r}: lowercase letters, digits, - and _')
        if it.get('aspect', '16:9') not in ASPECTS:
            raise SystemExit(f'{it["name"]}: aspect must be one of {ASPECTS}')
    return items, brands


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('lint'); s.add_argument('prompt'); s.add_argument('--kind', default='texture'); s.add_argument('--brand', action='append', default=[])
    for n in ('plan', 'run'):
        s = sub.add_parser(n); s.add_argument('work'); s.add_argument('--spec', required=True)
        s.add_argument('--only'); s.add_argument('--jobs', type=int, default=2); s.add_argument('--codex')
        s.add_argument('--timeout', type=int, default=600); s.add_argument('--force', action='store_true')
    s = sub.add_parser('probe'); s.add_argument('--codex')
    a = ap.parse_args(argv)
    if a.cmd == 'lint':
        probs = lint(a.prompt, a.kind, a.brand)
        print('OK' if not probs else '\n'.join('REFUSED ' + p for p in probs))
        return 0 if not probs else 1
    if a.cmd == 'probe':
        ok, msg = probe(a.codex)
        print(('OK ' if ok else 'UNAVAILABLE ') + msg)
        return 0 if ok else 2
    work = Path(a.work).resolve()
    items, brands = load_spec(a.spec)
    if a.only:
        keep = set(a.only.split(','))
        items = [i for i in items if i['name'] in keep]
    bad = 0
    for it in items:
        probs = lint(it['prompt'], it.get('kind', 'texture'), brands)
        print(f"{'OK     ' if not probs else 'REFUSED'} {it['name']:<22} {it.get('kind')}: {it['prompt'][:70]}")
        for p in probs:
            print('          - ' + p)
        bad += bool(probs)
    if bad:
        print(f'{bad} prompt(s) refused: fix them (or draw the thing yourself); nothing was generated')
        return 1
    if a.cmd == 'plan':
        return 0
    ok, msg = probe(a.codex)
    if not ok:
        print('UNAVAILABLE ' + msg)
        print('FALLBACK: make_assets.py ground/pattern/glow (procedural grounds), a drawn SVG through make_assets.py '
              'foil/layers, or fewer slides with asset_scarcity in brief.md. Do not use unlicensed web images.')
        return 2
    exe = find_codex(a.codex)
    todo = [i for i in items if a.force or not (work / 'assets/gen' / f"{i['name']}.jpg").exists()]
    print(f'{msg}\ngenerating {len(todo)} image(s), {a.jobs} at a time')
    metas, fails = [], []
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        for name, meta, err in ex.map(lambda it: run_one(it, work, exe, a.timeout), todo):
            if err:
                fails.append((name, err)); print(f'FAIL {name}: {err}')
            else:
                metas.append(meta); print(f'OK   {name} -> assets/{meta["file"]} {meta["size"]}')
    # rows for every generated file present (also earlier runs)
    allmeta = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((work / 'assets/gen').glob('*.json'))]
    n = append_credits(work, allmeta)
    print(f'CREDITS: {n} AI-generated row(s) added. LOOK at every image (contact_sheet.py WORK/assets/gen) before use.')
    if fails:
        print('Some images failed; the honest fallback is make_assets.py (procedural) or fewer slides — not web images.')
    return 0 if not fails else 3


if __name__ == '__main__':
    sys.exit(main())
