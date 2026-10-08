#!/usr/bin/env bash
# Render a deck to slide images + contact sheet:  pptx -> pdf (LibreOffice) -> jpg (pdftoppm).
# Usage: render.sh DECK.pptx OUT_DIR [DPI]
#   OUT_DIR gets slide-01.jpg ... and contact.jpg (12 per sheet: contact-1.jpg ... for long decks).
# Notes:
#   * Use a NEW OUT_DIR per render (renders/g3-1, renders/g3-2 ...) so you never look at stale images.
#   * LibreOffice shows only the static end state of each slide: Morph, entrances and blink are
#     NOT visible. They can only be verified in PowerPoint 365 / 2019+.
#   * LibreOffice skips hidden slides, so image numbers then shift. Fonts that are not installed
#     render with a fallback: install the deck fonts first (fc-list | grep -i <family>).
set -euo pipefail
DECK="${1:?usage: render.sh DECK.pptx OUT_DIR [DPI]}"
OUT="${2:?usage: render.sh DECK.pptx OUT_DIR [DPI]}"
DPI="${3:-80}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOFFICE="$(command -v soffice || command -v libreoffice || true)"
[ -n "$SOFFICE" ] || { echo "LibreOffice (soffice) not found: run setup.sh" >&2; exit 2; }
command -v pdftoppm >/dev/null || { echo "pdftoppm (poppler-utils) not found: run setup.sh" >&2; exit 2; }
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/lo-profile-XXXXXX")"   # isolated profile: parallel renders don't collide
trap 'rm -rf "$PROFILE"' EXIT
NAME="$(basename "${DECK%.*}")"
timeout 600 "$SOFFICE" -env:UserInstallation="file://$PROFILE" --headless --convert-to pdf --outdir "$OUT" "$DECK" >/dev/null 2>&1 || true
PDF="$OUT/$NAME.pdf"
[ -s "$PDF" ] || { echo "LibreOffice produced no PDF for $DECK" >&2; exit 3; }
pdftoppm -jpeg -r "$DPI" "$PDF" "$OUT/slide"
# pdftoppm pads numbers by page count (slide-01 or slide-001); normalise to two+ digits
for f in "$OUT"/slide-*.jpg; do
  n="${f##*-}"; n="${n%.jpg}"; n=$((10#$n)); printf -v new "%s/slide-%02d.jpg" "$OUT" "$n"
  [ "$f" = "$new" ] || mv "$f" "$new"
done
COUNT=$(ls "$OUT"/slide-*.jpg | wc -l)
python3 "$HERE/contact_sheet.py" "$OUT" --out "$OUT/contact.jpg" --cols 4 --width 400 --per-sheet 12 --label name
echo "rendered $COUNT slides -> $OUT (open contact*.jpg and LOOK at every tile)"
