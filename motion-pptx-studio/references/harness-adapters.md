# Harness adapters: install and run anywhere

The skill is a plain folder: `SKILL.md` + `references/` + `scripts/` (Python 3.9+, LibreOffice, poppler).
It needs four abilities: run shell commands, read and write files, **look at images** (contact sheets and renders), and
fetch web pages. Anything that has these can run it.

## 1. Install the skill folder
| Harness | Where skills are discovered | Install |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` (personal), `.claude/skills/<name>/` (project) | `git clone https://github.com/meiiie/meiiie_skillls /tmp/ms && cp -r /tmp/ms/motion-pptx-studio ~/.claude/skills/` |
| OpenAI Codex (CLI/IDE) | `~/.agents/skills/` (personal), `.agents/skills/` (repo); older `~/.codex/skills` is still scanned | `cp -r /tmp/ms/motion-pptx-studio ~/.agents/skills/` · invoke with `$motion-pptx-studio` |
| Cursor | `.cursor/skills/`, `.agents/skills/`, `~/.cursor/skills/`, `~/.agents/skills/` (also reads `.claude/skills`, `.codex/skills`) | copy the folder there; the frontmatter `name` must equal the folder name |
| Grok Bot | the bot's own skill/workflow store | ask: "install the motion-pptx-studio skill from github.com/meiiie/meiiie_skillls", or copy the folder onto the box and tell the bot to follow its SKILL.md |
| Any other LLM with a shell | n/a | clone the repo, then give the model `SKILL.md` as instructions and the folder path as `$S/..` |
Then run `bash scripts/setup.sh` (check) or `bash scripts/setup.sh --install` once per machine.
`agents/openai.yaml` holds the display name, short description, default prompt and icon for UIs that read it.

## 2. Ability mapping
| Ability | Claude Code | Codex | Cursor | Grok Bot | Plain LLM |
|---|---|---|---|---|---|
| Look at a render | Read the .jpg | view the image / attach it | Read the image | Read the image (inline) | must support image input; otherwise ask the user to look and describe it |
| Web research | WebSearch / WebFetch | web search tool if enabled; else `curl` | web tools; else `curl` | WebSearch / WebFetch; `curl` when a site blocks fetchers | `curl` + `python -m html2text` |
| Long jobs (LibreOffice, rembg) | background bash | background shell | background shell | background shell + await | run synchronously; keep the deck under ~60 slides per render |
| Sub-tasks in parallel | sub-agents (Task) | multiple sessions | background agents | subagents | sequential |
If sub-agents are available, delegate research and asset hunting (Phases 1–2) to one agent and art direction to another,
but **one** agent owns the storyboard and the build, so names and motion stay consistent.

## 3. Weak-model mode (smaller or faster models)
- Follow the gates literally; never skip a `gates.py check`. Paste the FAIL hints into your plan and fix them in order.
- Use `build_deck.py` (path A), not raw XML editing.
- Build 2–3 slides per group; render after every group; one fix pass per group.
- Keep sentences in notes short; run `words_budget.py measure` after every group, not only at the end.
- When unsure whether an image shows the subject: `--uncertain`, and use a drawn TRUE-list motif instead.

## 4. Optional external skills (never required)
| Skill | Use | Install |
|---|---|---|
| Anthropic `pptx` | alternative family-deck builder (html2pptx), thumbnail grids | Claude Code: `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills` (source: github.com/anthropics/skills, `skills/pptx`; see its licence) |
| Anthropic `docx` | richer speaker-script formatting | same plugin (`skills/docx`) |
| `heritage-visual-research` (this repo) | Phases 1–2 alone, for any visual project about a culture | copy the folder like the main skill |
| `presentation-speech-craft` (this repo) | the script and talk alone, for decks built elsewhere | copy the folder like the main skill |
Tools the scripts can use if present: `yt-dlp` (reference talks), `ffmpeg` (frames), `rembg` (cut-outs: `setup.sh --with-rembg`),
`markitdown` (quick text dump of a pptx).

## 5. Platform notes
- Windows: run the Python scripts with `py`; `render.sh` needs Git Bash or WSL (or run `soffice --headless --convert-to pdf` and
  `pdftoppm -jpeg -r 80` by hand). LibreOffice binary: `"C:\Program Files\LibreOffice\program\soffice.exe"`.
- macOS: `brew install --cask libreoffice && brew install poppler ffmpeg`.
- Headless servers: LibreOffice needs no display; `render.sh` uses an isolated profile, so parallel renders don't collide.
