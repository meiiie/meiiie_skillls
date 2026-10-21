#!/usr/bin/env bash
# Install Anatomy (https://skills.wheresryan.sh/anatomy, MIT, github.com/wheresryan22/anatomy) for signature moments.
# Anatomy is a Claude Code skill + a Node kit (kit/iso-kit.mjs) that draws a technical idea as an isometric
# machine made of many small solid parts. motion-pptx-studio uses its kit headless: scripts/anatomy/film.mjs
# renders a figure module frame by frame in headless Chrome -> MP4 + poster PNG + editable shapes.
#   bash setup_anatomy.sh            # check, clone if missing, print ANATOMY_HOME
#   ANATOMY_HOME=/path bash setup_anatomy.sh
# Needs: git, Node >= 20.10, Chrome/Chromium (google-chrome, chromium, or CHROME=/path).
# As an agent skill (optional, for building figures interactively): npx skills add wheresryan22/anatomy
set -u
HOME_DIR="${ANATOMY_HOME:-$HOME/.local/share/anatomy}"
ok=1
node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a>20||(a==20&&b>=10)?0:1)' 2>/dev/null \
  && echo "OK   node $(node --version)" || { echo "MISS node >= 20.10"; ok=0; }
CH="${CHROME:-$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)}"
[ -n "$CH" ] && echo "OK   chrome $CH" || { echo "MISS Chrome/Chromium (set CHROME=/path)"; ok=0; }
command -v ffmpeg >/dev/null && echo "OK   ffmpeg" || { echo "MISS ffmpeg"; ok=0; }
if [ ! -f "$HOME_DIR/kit/iso-kit.mjs" ]; then
  echo "...  cloning Anatomy into $HOME_DIR"
  git clone -q --depth 1 https://github.com/wheresryan22/anatomy "$HOME_DIR" || { echo "FAIL git clone"; ok=0; }
fi
if [ -f "$HOME_DIR/kit/iso-kit.mjs" ]; then
  echo "OK   anatomy $(git -C "$HOME_DIR" log -1 --format='%h %cs' 2>/dev/null) at $HOME_DIR"
  (cd "$HOME_DIR" && node examples/dial-indicator/build.mjs >/dev/null) && echo "OK   kit builds (examples/dial-indicator)" || { echo "FAIL kit build"; ok=0; }
fi
echo "export ANATOMY_HOME=$HOME_DIR"
[ $ok = 1 ] || { echo "Anatomy unavailable: use scripts/diagram_video.py or ManimGX for signature moments (references/signature-moments.md §4)"; exit 2; }
