---
name: motion-pptx-studio
description: Build cinematic, research-backed PowerPoint decks that use Morph (multi-slide keyframe motion, named layers, entrance effects) plus a timed speaker script. Use when someone asks for a "motion pptx", a pitch or contest presentation, a cultural or heritage deck, or a product launch deck that must look professional, be visually rich and be factually exact, especially in Vietnamese. The pipeline is mandatory and gated: research, then verified licensed assets, then art direction, then storyboard, then build, then QA, then delivery.
---

# Motion PPTX Studio

Turn a brief into a **PowerPoint deck with real motion** (Morph keyframes across several slides),
**researched and licensed imagery**, a **speaker script that fits the time limit**, and a delivery
folder with fonts and credits. It works in any harness that has a shell and Python
(Claude Code, Codex, Cursor, Grok Bot, or a plain LLM with tools).

The standard comes from a real user and is kept word for word:

> "Tìm hiểu kỹ văn hoá Ca Trù để tìm và tải backgroud sao cho phù hợp nhé và đảm bảo độ chính xác tuyệt đối"
> "với các pptx chuyên nghiệp tôi đều thấy họ có nhiều cảnh nhiều motion, có khi nhiều slide để phục vụ cho một motion hoàn chỉnh, từng frame và mọi thứ, cần làm chuyên nghiệp nhé"
> "Trông chưa ổn lắm, cần chọn font cần tài nguyên asset, mọi thứ khác nhé" · "Ca Trù phải để tiếng Việt chứ nhỉ ?"

**The failure this skill exists to prevent:** an agent opens a slide tool straight away, uses
generic icons, gradients and invented "cultural" motifs, never downloads a real image, never checks
whether the drum in the picture belongs to the art form, and plans "7 seconds per slide" that turns
into twice the allowed time. Every gate below blocks one part of that failure.

## Non-negotiable rules

1. **No slide before Gate 4 passes.** Research, assets, design and storyboard come first.
2. **Every claim traces to `research/facts.md`; every image to `assets/CREDITS.md`.** No source, no slide.
3. **Look at every image yourself** (contact sheets, renders). Titles, tags and file names are not evidence.
   The skill's own test found string quartets and a North Carolina road sign in a "đàn đáy / ca trù" search.
4. **One motion = several slides.** A scene is 3–5 keyframe slides joined by Morph, with persistent `!!name` layers.
5. **On-slide language follows the audience** (Vietnamese topic, so Vietnamese slides). Foreign script
   *inside photos* counts too: crop or inpaint it.
6. **Budget speech in words, not seconds per slide** (130 wpm). Measure the script before delivery.
7. **Never overstate.** Status (finished, design-only, planned), results, licences and awards are exactly as sourced.
8. **Ask the user at most once, at the start** (time limit, language, honest status). Otherwise choose a
   documented default in `brief.md` and tell them.
9. **Never game a gate.** Do not edit `gates.py`, lower thresholds, create placeholder files or copy rows to pass.
   If a minimum truly does not fit the job, say so in `brief.md` ("Decisions") and in your final message.

## Setup (once per machine)

```bash
bash scripts/setup.sh            # check: python-pptx lxml Pillow fonttools python-docx, LibreOffice, poppler
bash scripts/setup.sh --install  # install what is missing (pip --user, falls back to a venv)
```
Set two variables first and use them in every command:
`S=<absolute path of this skill>/scripts` (e.g. `S=~/.claude/skills/motion-pptx-studio/scripts`) and
`WORK=<project folder>` (e.g. `WORK=$PWD/catru-deck`). Use `python3` if `python` is not Python 3; if setup created a
venv, use `$S/../.venv-motion/bin/python` or the path it printed. Every tool explains itself with `-h`. Harness notes (where skills live, how to look at images, how to run long jobs) are in
`references/harness-adapters.md`.

## The pipeline (each gate is a command; FAIL means stop and do the missing work)

```bash
python $S/gates.py init WORK --kind heritage|product|other   # creates the folders + templates
python $S/gates.py check WORK --gate N                       # N = 0..6, logs to WORK/gates.log
```

### Phase 0: Brief → Gate 0
Fill `WORK/brief.md`: topic, audience, kind, talk_minutes (hard limit), on-slide language, forbidden
items, **honest status**, presenter, reference talk, user media, and **the user's own words verbatim**.
If the user gave a video, a submission form or a repo, read it before anything else. Read the matching case
study (`examples/case-catru-heritage.md` for culture or heritage, `examples/case-neko-core-product.md` for products)
to see the expected depth.

### Phase 1: Research → Gate 1 (`references/research-protocol.md`, `references/cultural-visual-accuracy.md`)
- `research/facts.md`: sourced facts in tables, each tagged `[verified]` / `[secondary]` / `[claim]` /
  `[disputed]` / `[uncertain]`. Heritage: at least 15 facts from 3 or more domains (UNESCO dossier, national
  institutes, museums, scholarly or press sources). Product: at least 12 facts from the repo, README,
  CHANGELOG, releases and site.
- A **do-not-say list** (at least 3): claims that are tempting but false or unproven.
- `research/accuracy.md`: the **TRUE motifs and objects**, the **WRONG associations** (generic national
  symbols, neighbouring art forms, AI-looking glow), an **object anatomy checklist** (counts, shapes, who
  holds what), and an **audit of the user's media** (frame by frame: OK / keep small / never use).
- Reference talk given? Write `research/lessons.md` from the real video or transcript (`references/speech-craft.md`).

### Phase 2: Assets → Gate 2 (`references/asset-sourcing.md`)
```bash
python $S/fetch_commons.py search "ca trù" --out WORK/assets/candidates      # also English + no-diacritics queries
python $S/fetch_commons.py keep "<id>" --as 04_dan_day.jpg --why "3 strings, 3 staggered pegs (facts 3.1)" \
       --dest WORK/assets --credits WORK/assets/CREDITS.md --candidates WORK/assets/candidates/candidates.json
python $S/contact_sheet.py WORK/assets --out WORK/assets/contact.jpg        # then LOOK, against accuracy.md
```
- Look at **at least twice as many candidates as you keep**. Write the rejected ones and the reason.
- Licences: CC0 / PD / CC BY / CC BY-SA by default; **no NC/ND** for contest, TV or commercial use. An edited BY-SA
  image stays BY-SA and is credited "(đã chỉnh sửa / edited)". Subject not verified → `assets/_uncertain/`,
  never captioned as the subject.
- Products: official logo, screenshots and brand board first; **never redraw a logo**; label illustrations as illustrations.
- Prepare: `cutout.py` (museum objects, transparent PNG), `inpaint_text.py` (foreign script inside photos),
  `video_frames.py` (frames from the user's video), `make_assets_example.py` (procedural textures and gold-leaf motifs).
  Keep originals in `WORK/media_orig/`.

### Phase 3: Art direction → Gate 3 (`references/art-direction.md`)
- Two or three OFL fonts with full coverage of the on-slide language, as **static** TTFs in `WORK/fonts/` with the OFL text
  (download and instancing commands in the reference):
  `python $S/check_fonts.py WORK/fonts/*.ttf --lang vi --png WORK/design/font-sample.png > WORK/design/font-check.txt`
  (other languages: `--lang none --text-file slide_text.txt` with your real on-slide text). Look at the sample PNG.
- **Install the fonts on the machine that renders** (`~/.local/share/fonts` + `fc-cache -f`, or `~/Library/Fonts`), or
  every render shows a fallback font and you judge the wrong thing.
- A palette with hex codes and where each comes from (brand board, lacquer photo), motifs from the TRUE list
  only, layered objects for Morph, and a colour arc, written in `WORK/design/art-direction.md`.
- Samples: write a 2–4 slide `WORK/deck.json` (title, body, one keyframe pair), then `build_deck.py` + `render.sh` as in Phase 5,
  and copy the title and body renders into `WORK/design/samples/`. Look at them; change direction now, not after 40 slides.

### Phase 4: Storyboard → Gate 4 (`references/storyboard-template.md`, `references/motion-grammar.md`, `references/speech-craft.md`)
```bash
python $S/words_budget.py plan --minutes 6 --slides 34     # → ~754 words total, ~22 per slide
```
`WORK/storyboard.md`: one row per **slide** with scene, keyframe role, layout, `!!` layers, a real visual
(asset file, `drawn:<motif>` or `frame:<file>`), on-slide text and a **words budget**. Required:
8 or more scenes for talks of 5 minutes or longer; at least 60% of scenes are keyframe runs of 3 or more slides;
an anchor phrase on 3 slides (setup, middle, end); a colour arc; a circular close; and `WORK/motion.json`
with the planned Morph durations (keyed by slide **file** number).

### Phase 5: Build in groups of 2–3 slides → Gate 5 per group (`references/build-engine.md`, `references/qa-checklist.md`)
Default engine (no external service): `WORK/deck.json` holds every slide built so far; add 2–3 slides per group
(the spec format is in `references/build-engine.md`; image paths are relative to deck.json). Edit the JSON, never the
unpacked XML, and rebuild everything each round (it takes seconds):
```bash
python $S/build_deck.py WORK/deck.json --out WORK/deck/build.pptx     # "from": "prev" + "set" = next keyframe
rm -rf WORK/deck/unpacked && python $S/ooxml.py unpack WORK/deck/build.pptx WORK/deck/unpacked
python $S/motion.py WORK/deck/unpacked          # 1 Morph per slide, @entrances, @blink; reads WORK/motion.json
python $S/ooxml.py pack WORK/deck/unpacked WORK/deck/preview-g1.pptx
python $S/check_deck.py WORK/deck/preview-g1.pptx --anchor "<anchor phrase>"
bash   $S/render.sh WORK/deck/preview-g1.pptx WORK/renders/g1-1           # NEW folder each round
python $S/gates.py check WORK --gate 5 --group g1 --deck WORK/deck/preview-g1.pptx
```
After each render, **open the contact sheet and every changed slide**, write the defects into
`WORK/notes/g1.md`, fix them in one pass, then re-render to `g1-2`. Typical defects: text over a busy area,
collisions after a Morph move, foreign script in a photo, stretched photos, wrong instrument details,
a lonely `!!` layer, a heading broken mid-word.
Naming: `!!name` = the same object on neighbouring slides (Morph pairs it). `@fade|float|wipe<N>-label` = entrance N.
`@blink<N>-label` = an endless blink loop. A slide in `keep_timing` keeps hand-made animation.

### Phase 6: Finish and deliver → Gate 6 (`references/delivery.md`)
```bash
python $S/finish_dedupe.py WORK/deck/unpacked && python $S/ooxml.py clean WORK/deck/unpacked
python $S/ooxml.py pack WORK/deck/unpacked WORK/deck/final.pptx && bash $S/render.sh WORK/deck/final.pptx WORK/renders/final-1
python $S/words_budget.py measure WORK/deck/final.pptx --target 6:00
python $S/deliver.py WORK --deck WORK/deck/final.pptx --name Project_Motion --title "Kịch bản thuyết trình"
python $S/gates.py check WORK --gate 6
```
`deliver/` = `.pptx` + speaker-script `.docx` + `fonts/` (static TTF, OFL, install README) + `CREDITS.md` + `.zip`.
A credits slide lists every CC BY/BY-SA image. If the script runs more than 10% over time, cut words
(heaviest slides first) or get the user to accept the overrun and record `time_overrun_accepted: yes`.

## Final message to the user (always)
Files delivered; slide and scene count; measured speaking time against the target; fonts to install;
**what must be checked in PowerPoint 365** (Morph, entrances and blink are invisible in LibreOffice renders);
decisions taken without asking; claims left out because they could not be verified.

## Reference map

| File | Read it when |
|---|---|
| `references/research-protocol.md` | Phase 1: source ladder, tagging, do-not-say list, product research |
| `references/cultural-visual-accuracy.md` | any cultural or heritage topic: true and wrong motifs, anatomy, user-media audit |
| `references/asset-sourcing.md` | Phase 2: where to search, licences, keep/reject, cutout, inpaint, frames |
| `references/art-direction.md` | Phase 3: fonts (diacritics, static instances), palette, motifs, colour arc |
| `references/motion-grammar.md` | Phases 4–5: keyframe runs, `!!` layers, durations, entrances, blink |
| `references/storyboard-template.md` | Phase 4: table format, scene patterns, worked example |
| `references/speech-craft.md` | Phases 1/4: hook, anchor, pauses, circular close, word budget |
| `references/build-engine.md` | Phase 5: deck.json spec, OOXML editing, sequences, notes, alternative engines |
| `references/qa-checklist.md` | every render: visual, accuracy, motion, language, licence, timing checks |
| `references/delivery.md` | Phase 6: package, fonts, credits, the final message |
| `references/harness-adapters.md` | installing the skill; Claude Code / Codex / Cursor / Grok Bot / plain LLM differences |
| `examples/case-catru-heritage.md` | a heritage deck (48 slides, 14 scenes) and every correction the user made |
| `examples/case-neko-core-product.md` | a product deck (34 slides) from a GitHub repo, with honesty rules |

Companion skills (optional, same repo): `heritage-visual-research` (Phases 1–2 as a standalone skill)
and `presentation-speech-craft` (the script and talk). Optional external: Anthropic's `pptx` and `docx`
skills (see `references/harness-adapters.md`). They are never required.
