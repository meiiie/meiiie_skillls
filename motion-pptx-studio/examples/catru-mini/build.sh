#!/usr/bin/env bash
# Rebuild this example from scratch: gold-foil drawings -> deck.json -> pptx + renders + audit.
set -euo pipefail
cd "$(dirname "$0")"
S=../../scripts
[ -f assets/dd_full.png ] || python3 "$S/make_assets_example.py" --out assets
python3 make_deck.py
python3 "$S/studio.py" build . "$@"
