#!/usr/bin/env bash
# Check (default) or install the toolchain motion-pptx-studio needs.
#   bash setup.sh            check only: prints OK / MISSING per tool, exit 1 if a REQUIRED tool is missing
#   bash setup.sh --install  pip-installs the missing Python packages (user site, or a venv if pip refuses),
#                            plus yt-dlp; prints the system-package command for binaries (never runs sudo)
#   bash setup.sh --install --with-rembg   also installs rembg (background removal, ~200 MB model on first use)
# REQUIRED : python3 >= 3.9, python-pptx, lxml, Pillow, fonttools, python-docx, LibreOffice (soffice), pdftoppm
# RECOMMENDED: numpy, scipy, opencv-python-headless (inpainting), cairosvg (vector motifs), requests, ffmpeg, yt-dlp, fontconfig (fc-list)
# OPTIONAL : rembg (cut-outs), node + pptxgenjs (if you prefer building the family deck in JS),
#            Anthropic "pptx"/"docx" skills (Claude Code), markitdown (quick text dump)
set -u
MODE="check"; REMBG=0
for a in "$@"; do case "$a" in --install) MODE=install;; --with-rembg) REMBG=1;; -h|--help) sed -n 2,12p "$0"; exit 0;; esac; done
PY="${PYTHON:-python3}"
missing_req=0; missing_py=()
ok(){ printf '  OK       %-26s %s\n' "$1" "${2:-}"; }
miss(){ printf '  %-8s %-26s %s\n' "$1" "$2" "${3:-}"; }
echo "== python"
if ! command -v "$PY" >/dev/null; then miss MISSING python3 "install Python 3.9+"; exit 1; fi
ok python3 "$($PY --version 2>&1)"
check_mod(){ # module pipname level
  if "$PY" -c "import $1" 2>/dev/null; then ok "$2"; else
    if [ "$3" = req ]; then miss MISSING "$2" "(required)"; missing_req=1; else miss missing "$2" "($3)"; fi
    missing_py+=("$2"); fi; }
check_mod pptx python-pptx req
check_mod lxml lxml req
check_mod PIL Pillow req
check_mod fontTools fonttools req
check_mod docx python-docx req
check_mod numpy numpy recommended
check_mod cv2 opencv-python-headless recommended
check_mod cairosvg cairosvg recommended
check_mod scipy scipy recommended
check_mod requests requests recommended
if [ $REMBG = 1 ]; then check_mod rembg "rembg[cpu]" optional; fi
echo "== binaries"
check_bin(){ # name level hint
  if command -v "$1" >/dev/null; then ok "$1" "$(command -v "$1")"; else
    if [ "$2" = req ]; then miss MISSING "$1" "(required) $3"; missing_req=1; else miss missing "$1" "($2) $3"; fi; fi; }
if command -v soffice >/dev/null || command -v libreoffice >/dev/null; then ok soffice "$(command -v soffice || command -v libreoffice)"; else miss MISSING soffice "(required) LibreOffice: apt install libreoffice-impress | brew install --cask libreoffice | winget install TheDocumentFoundation.LibreOffice"; missing_req=1; fi
check_bin pdftoppm req "poppler: apt install poppler-utils | brew install poppler | conda install poppler"
check_bin ffmpeg recommended "apt install ffmpeg | brew install ffmpeg | winget install Gyan.FFmpeg"
if command -v yt-dlp >/dev/null || "$PY" -c "import yt_dlp" 2>/dev/null; then ok yt-dlp; else miss missing yt-dlp "(recommended) pip install yt-dlp"; missing_py+=("yt-dlp"); fi
check_bin fc-list recommended "fontconfig (Linux/macOS). On Windows check fonts in Settings > Fonts"
check_bin node optional "only if you build the family deck with pptxgenjs"
echo "== fonts installed for rendering (fc-list)"
if command -v fc-list >/dev/null; then echo "  $(fc-list : family | wc -l) font families; install deck fonts into ~/.local/share/fonts (Linux) or ~/Library/Fonts (macOS) then fc-cache -f"; fi
if [ "$MODE" = install ] && [ ${#missing_py[@]} -gt 0 ]; then
  echo "== installing: ${missing_py[*]}"
  if ! "$PY" -m pip install --user "${missing_py[@]}" 2>/dev/null; then
    echo "  pip --user refused (PEP 668?). Creating venv .venv-motion in $(pwd)"
    "$PY" -m venv .venv-motion && ./.venv-motion/bin/pip install python-pptx lxml Pillow fonttools python-docx numpy scipy opencv-python-headless cairosvg requests yt-dlp $( [ $REMBG = 1 ] && echo 'rembg[cpu]') \
      && echo "  done: run scripts with $(pwd)/.venv-motion/bin/python (export PYTHON=$(pwd)/.venv-motion/bin/python)" \
      && { echo "== re-checking with the venv"; PYTHON="$(pwd)/.venv-motion/bin/python" exec bash "$0"; }
  fi
  echo "== re-checking"; exec bash "$0"
fi
echo
if [ $missing_req = 1 ]; then echo "RESULT: MISSING REQUIRED TOOLS. Fix them before Gate 0 (bash setup.sh --install for Python packages)."; exit 1; fi
echo "RESULT: READY (required tools present)."
