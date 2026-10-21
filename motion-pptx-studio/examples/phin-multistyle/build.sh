#!/usr/bin/env bash
# Rebuild: diagram film + editable fragment -> deck.json -> pptx + renders + audit.
set -euo pipefail
cd "$(dirname "$0")"
S=../../scripts
python3 $S/diagram_video.py design/brew.json --mp4 assets/brew.mp4 --poster assets/brew.poster.png --fragment design/brew-shapes.json
python3 make_deck.py
python3 $S/studio.py build . "$@"
python3 $S/verify_motion.py deck/preview-g1.pptx
# optional: python3 $S/preview_motion.py deck/preview-g1.pptx --out preview-SIMULATION.mp4 --max-slide 5.5
