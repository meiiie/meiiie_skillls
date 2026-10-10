#!/usr/bin/env bash
# Rebuild: drawn product screens -> deck.json -> pptx + renders + audit.
set -euo pipefail
cd "$(dirname "$0")"
S=../../scripts
python3 make_screens.py
python3 make_deck.py
python3 "$S/studio.py" build . "$@"
