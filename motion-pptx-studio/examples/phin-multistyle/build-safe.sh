#!/usr/bin/env bash
# No-Morph safe build (PowerPoint 2010+/Google Slides/Keynote/LibreOffice): every Morph becomes classic motion.
# Usage: build-safe.sh [WORK]   (default WORK = ./safe-work)
set -euo pipefail
cd "$(dirname "$0")"
S=../../scripts
WORK="${1:-safe-work}"
[ -f design/brew-shapes.json ] || python3 $S/diagram_video.py design/brew.json --mp4 assets/brew.mp4 --poster assets/brew.poster.png --fragment design/brew-shapes.json
python3 make_deck.py safe
mkdir -p "$WORK"
python3 $S/studio.py build "$WORK" --deck deck-safe.json
python3 $S/verify_motion.py "$WORK/deck/preview-g1.pptx"
