# Changelog

## 2.0.0
Rebuilt after the user's review: "other models and agents don't research images, sources and assets, so the result lacks
visual richness and pull."
- **Hard gates** (`scripts/gates.py`, Gates 0–6): no slide before brief, research, assets, art direction and storyboard pass.
- **Research protocol** and **cultural visual accuracy** references: source ladder, tags, do-not-say list, TRUE/WRONG motif lists,
  object anatomy checklist, user-media audit.
- **Asset sourcing with licences**: `fetch_commons.py` (Commons + Openverse, quoted and ASCII-folded queries, NC/ND excluded, keep → CREDITS),
  `contact_sheet.py`, `cutout.py`, `inpaint_text.py`, `video_frames.py`.
- **Harness-independent build**: `build_deck.py` (JSON spec with keyframe inheritance) + `ooxml.py`; no dependency on a managed slide service.
- **motion.py rewrite**: lxml-based stripping (no stacked or empty AlternateContent), `@blink`, `keep_timing`, motion.json
  (found in the unpacked folder, deck/ or WORK), duplicate-name warnings; idempotent.
- **Timing by words**: `words_budget.py` plan/measure; script_docx shares its counting rules.
- **QA**: `check_deck.py`, `check_fonts.py` (Vietnamese coverage, variable-font warning), `render.sh`; QA checklist reference.
- **Delivery**: `deliver.py` (static fonts + install README + CREDITS + zip).
- Case studies (ca trù heritage, neko-core product), harness adapters (Claude Code, Codex, Cursor, Grok Bot, plain LLM), companion skills.

## 1.0.0
First version: Morph naming conventions, motion.py, roles.py, finish_dedupe.py, script_docx.py, make_assets_example.py; it relied on
a managed slide workflow for building and had no research or asset rules.
