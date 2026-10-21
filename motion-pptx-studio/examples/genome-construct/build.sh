#!/usr/bin/env bash
# Worked example (v5.6): route -> genome -> directions -> deck.json -> build. No photos; numbers are fictional.
set -euo pipefail
cd "$(dirname "$0")"
S=../../scripts
python3 $S/route.py .                     # design/routing.md + .json: chosen + rejected, each with the deck's evidence
python3 $S/genome.py compile design/genome.json        # design/style.json + design/art-direction.md
python3 $S/directions.py .                 # design/directions.jpg (+ directions.md when missing)
python3 make_deck.py
python3 $S/studio.py build . "$@"
