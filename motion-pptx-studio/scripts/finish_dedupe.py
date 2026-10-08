"""Merge byte-identical ppt/media files and downscale wide images when the folder is large.

Usage:
  python finish_dedupe.py UNPACKED_DIR [--max-bytes 22000000] [--max-width 2560]

UNPACKED_DIR is the unpacked deck (it contains ppt/media). Identical files are
replaced by the first name in each hash group (shortest name, then alphabetical).
Relationship targets and content-type overrides are rewritten to that keeper.
When the folder is still larger than --max-bytes, PNG and JPEG files wider than
--max-width are resized to that width.
"""
import argparse
import hashlib
import re
from pathlib import Path

from PIL import Image

# Chat attachments need to stay under about 25 MB. 22 MB leaves room for the
# rest of the package before textures are reduced.
DEFAULT_MAX_BYTES = 22_000_000
DEFAULT_MAX_WIDTH = 2560


def dedupe(unpacked, max_bytes, max_width):
    root = Path(unpacked)
    media = root / 'ppt' / 'media'
    if not media.is_dir():
        raise SystemExit('no media directory: ' + str(media))
    by = {}
    for f in sorted(media.iterdir(), key=lambda p: (len(p.name), p.name)):
        if not f.is_file():
            continue
        by.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(), []).append(f.name)
    rep = {d: v[0] for v in by.values() for d in v[1:]}
    for rels in root.rglob('*.rels'):
        x = rels.read_text()
        y = re.sub(
            r'(Target="(?:\.\./|/ppt/)?media/)([^"]+)"',
            lambda m: m.group(1) + rep.get(m.group(2), m.group(2)) + '"',
            x,
        )
        if y != x:
            rels.write_text(y)
    for name in rep:
        (media / name).unlink()
    content_types = root / '[Content_Types].xml'
    x = content_types.read_text()
    for name in rep:
        x = re.sub(r'<Override [^>]*PartName="/ppt/media/%s"[^>]*/>' % re.escape(name), '', x)
    content_types.write_text(x)
    print('removed dupes', len(rep))
    total = sum(f.stat().st_size for f in media.iterdir() if f.is_file())
    print('media MB', total / 1e6)
    if total > max_bytes:
        for f in media.iterdir():
            if not f.is_file() or f.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
                continue
            im = Image.open(f)
            if im.width > max_width:
                h = round(im.height * max_width / im.width)
                im2 = im.resize((max_width, h), Image.LANCZOS)
                if f.suffix.lower() == '.png':
                    im2.save(f, optimize=True)
                else:
                    im2.convert('RGB').save(f, quality=88, optimize=True)
        total = sum(f.stat().st_size for f in media.iterdir() if f.is_file())
        print('after downscale MB', total / 1e6)
    largest = sorted((f for f in media.iterdir() if f.is_file()), key=lambda p: -p.stat().st_size)[:12]
    for f in largest:
        if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
            print(f.name, Image.open(f).size, round(f.stat().st_size / 1e6, 2))
        else:
            print(f.name, round(f.stat().st_size / 1e6, 2))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Dedupe unpacked ppt/media by hash and downscale wide images.')
    parser.add_argument('unpacked', help='unpacked deck directory (contains ppt/media)')
    parser.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_BYTES, help='downscale only when media exceeds this size')
    parser.add_argument('--max-width', type=int, default=DEFAULT_MAX_WIDTH, help='maximum image width in pixels')
    args = parser.parse_args(argv)
    if args.max_bytes < 1 or args.max_width < 1:
        raise SystemExit('max-bytes and max-width must be positive')
    dedupe(args.unpacked, args.max_bytes, args.max_width)


if __name__ == '__main__':
    main()
