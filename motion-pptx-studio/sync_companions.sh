#!/usr/bin/env bash
# Refresh the script copies in the companion skills from motion-pptx-studio (the canonical copy).
# Lives in motion-pptx-studio/; the companion folders are siblings in the repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
M="$ROOT/motion-pptx-studio"
cp "$M/scripts/"{fetch_commons.py,contact_sheet.py,cutout.py,inpaint_text.py,video_frames.py,check_fonts.py} "$ROOT/heritage-visual-research/scripts/"
cp "$M/assets/templates/"{facts.md,accuracy.md,CREDITS.md} "$ROOT/heritage-visual-research/templates/"
cp "$M/scripts/"{words_budget.py,script_docx.py,ooxml.py} "$ROOT/presentation-speech-craft/scripts/"
cp "$M/assets/templates/lessons.md" "$ROOT/presentation-speech-craft/templates/"
echo "companions synced"
