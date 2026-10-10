#!/usr/bin/env bash
# Rebuild: deck.json -> pptx + renders + audit (the grounds are generated from the style pack).
set -euo pipefail
cd "$(dirname "$0")"
python3 make_deck.py
python3 ../../scripts/studio.py build . "$@"
