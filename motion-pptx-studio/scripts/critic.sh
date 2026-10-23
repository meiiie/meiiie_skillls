#!/bin/bash
# Independent critic (v6.11/6.13). usage: critic.sh RENDER_DIR [OUT=critique.md] | critic.sh --pick SAMPLES_DIR [OUT=pick.md]
# Runs a FRESH codex session (no builder context) that compares the contact sheets with examples/yardsticks.
# If codex cannot start (sandboxed agent, no CLI): hand references/critic-prompt.md + the same images to a fresh
# subagent / new chat; never score yourself in its place - write "critic: unavailable, reason" in NOTES.md.
S=$(cd "$(dirname "$0")/.." && pwd); PR=critic-prompt.md
if [ "$1" = --pick ]; then PR=critic-pick-prompt.md; shift; R=$1; OUT=${2:-pick.md}   # R = samples dir with A/ B/ C/
  IMG=(); for f in "$S"/examples/yardsticks/[123]-*.jpg; do IMG+=(-i "$f"); done
  for x in A B C; do f=$(ls -t "$R"/$x/renders/*/contact*.jpg "$R"/$x/contact*.jpg 2>/dev/null | head -1); [ -n "$f" ] && IMG+=(-i "$f"); done
elif [ "$1" = --slides ]; then PR=critic-slides-prompt.md; shift; R=$1; OUT=${2:-critique-slides.md}   # v6.18 per-slide
  PREVR=$3; PREVC=$4   # v6.19 persistent: previous render dir + previous critique -> before/after of each ordered slide
  IMG=(-i "$S/examples/yardsticks/1-trai-dat.jpg" -i "$S/examples/yardsticks/1-spacex.jpg")
  if [ -n "$PREVC" ] && [ -f "$PREVC" ]; then PR=critic-followup-prompt.md
    for n in $(grep -oE '^ORDER [0-9]+' "$PREVC" | awk '{printf "%02d ", $2}'); do
      for f in "$PREVR"/slide-$n.* "$R"/slide-$n.*; do [ -f "$f" ] && IMG+=(-i "$f"); done; done
    [ -f "$R/contact-1.jpg" ] && for f in "$R"/contact-*.jpg; do IMG+=(-i "$f"); done
    EXTRA="PREVIOUS CRITIQUE (yours):
$(cat "$PREVC")
LIBRARY (photos you may order; name the file): $(cd "$R/../.." 2>/dev/null && find . -path '*library*' -name '*.jpg' -not -name 'board-*' | head -120 | tr '\n' ' ')"
  else
    for f in "$R"/slide-*.jpg "$R"/slide-*.png; do [ -f "$f" ] && IMG+=(-i "$f"); done
    EXTRA="LIBRARY (photos you may order; name the file): $(cd "$R/../.." 2>/dev/null && find . -path '*library*' -name '*.jpg' -not -name 'board-*' | head -120 | tr '\n' ' ')"; fi
else R=$1; OUT=${2:-critique.md}
  IMG=(); for f in "$S"/examples/yardsticks/[123]-*.jpg "$R"/contact-*.jpg; do IMG+=(-i "$f"); done; fi
codex exec --skip-git-repo-check -s workspace-write "${IMG[@]}" -- "$(cat "$S/references/$PR")
$EXTRA
Write it to $OUT." < /dev/null \
  && test -s "$OUT" && echo "<!-- signed: critic.sh $(date +%FT%T) fresh session -->" >> "$OUT" && echo "critic: wrote $OUT" || { echo "critic: unavailable - use a fresh subagent with references/critic-prompt.md"; exit 2; }
