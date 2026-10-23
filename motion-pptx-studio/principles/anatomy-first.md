# anatomy-first
Anatomy (https://skills.wheresryan.sh/anatomy, MIT, github.com/wheresryan22/anatomy) draws an idea as a
real isometric machine built from many small solid parts. Its rule is "the object is the explanation".
**It is required whenever the topic has any structure or process:** architecture, a system, a machine,
a supply chain, a pipeline, a cycle, an organisation, an isometric scene. Then the deck has at least one
Anatomy film in addition to its ManimGX films.

**Step 0, alongside ManimGX: install it and smoke-test it.** It needs Node 20.10+, Chrome or Chromium
(headless) and ffmpeg. The clone is about 27 MB.
- Install: `bash scripts/setup_anatomy.sh`. This checks node, chrome and ffmpeg, clones the repo to
  ~/.local/share/anatomy, builds the dial example and prints `export ANATOMY_HOME=...`.
- **No GitHub** (ChatGPT: git is blocked, npm goes through a proxy, and the `anatomy-figures` npm
  package has no kit):
  - fetch `https://github.com/wheresryan22/anatomy/archive/refs/heads/main.tar.gz` with
    container.download, or ask the user to upload it;
  - `tar xzf` it, then `export ANATOMY_HOME=$PWD/anatomy-main`.
  - If Chrome is missing, set `CHROME=/path/to/chromium`.
- More: references/details/anatomy-first.md (commands, flags, edge cases).
