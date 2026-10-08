---
name: motion-pptx-studio
description: >-
  Use when the user wants a cinematic, professional motion PowerPoint (.pptx
  with Morph keyframe sequences, many scenes, researched fonts and licensed
  assets) plus a speaker script, especially for competitions, pitches or
  cultural/heritage topics where factual and visual accuracy matter.
---
# Motion PPTX Studio

End-to-end workflow for a cinematic motion deck: research, story, art direction, multi-slide Morph keyframes, speaker script, delivery. It runs on top of the Cursor-managed `slides` skill (phases family, storyboard, build per group, fix, finish, clean, done by knowledgeWork children that follow `slides-executor`). This skill adds the craft rules and helper scripts. Helper scripts live beside this file in `scripts/`.

## 0. Intake (one short exchange, then default and proceed)
- Platform: PowerPoint .pptx (Morph needs PowerPoint 365 / 2019+).
- Topic, audience (judges, TV, investors), the product or deliverable being presented, and any limits: time limit of the video or talk, required sections, language of on-slide text.
- Honest status of the product: what is finished, what is only a design. Never let a slide or the script claim something is built or playable when it is not.
- If the user skips choice widgets, proceed on sensible defaults and say they can interject.

## 1. Research before design (parallel)
- **Speech craft:** if the user gives a reference talk (e.g. a public-speaking champion video), download it (yt-dlp in a venv), get it described, and extract lessons into `presentation_lessons.md`: sensory hook opening, one anchor phrase repeated 3 times, muted-to-colour reveal at the turning point, circular ending that returns to the opening image, marked pauses `[ngừng 2 giây]` / `[pause 2s]`.
- **Subject facts:** build a fact file with a source URL and verification tag per fact. Every on-slide and spoken claim must trace to it, the user's own product, or their submission. No invented numbers, dates, partners or attendance.
- **Cultural/visual accuracy (heritage topics):** list which motifs, instruments, costumes, architecture truly belong to the subject and which are common wrong associations (generic national symbols, wrong folk-art styles). Check the user's own media against the facts and keep flawed frames small or out (wrong instrument details, AI hand errors, wrong playing technique).
- **Assets:** download licensed photos (Wikimedia Commons, Flickr CC, public domain) into `assets/bg/` with a `CREDITS.md` (author, licence, URL). CC BY / BY-SA need attribution; edited BY-SA images stay BY-SA and are credited "(edited / đã chỉnh sửa)". Keep uncertain-provenance images in `_uncertain/`, never captioned as the subject.
- **Language hygiene:** if the user wants on-slide text in one language only, also scan photos for foreign script (signs, couplets, plaques) and crop or inpaint it; keep originals in `media_orig/`.
- **User media:** if they have a product video, download it (Drive: `curl` the `drive.usercontent.google.com/download?id=...&confirm=t` URL), compress for analysis (ffmpeg 854px CRF 28), extract key frames to a contact sheet, crop burned-in captions, and record which frames are safe to use.

## 2. Art direction (family phase)
- Pick real fonts on purpose (Google Fonts, OFL): a display serif with character + a clean sans; check full diacritic support for the language. Ship them in a `fonts/` folder with OFL licence files and an install README, since the box cannot embed fonts.
- Build hand-made textures and vector ornaments from motifs that are verified for the subject (`scripts/make_assets_example.py` shows the approach: lacquer/gold textures, layered parts of an object so each part can morph separately, ring medallions, woven bands). Cut out mascots/characters with rembg.
- Offer two families with different palettes; if the user wants one shot, make one.

## 3. Storyboard as motion, not bullet slides
- 10-15 scenes, 3-5 keyframe slides per scene (about 35-50 slides for a 5-12 minute talk). Several slides serve one motion: assemble, push-in, reveal, highlight walk, collapse.
- Name persistent layers with a `!!` prefix (`!!str1`, `!!medallion`, `!!screen`, `!!phrase`); same name on neighbouring slides = Morph pairs them. Entrance animations: name objects `@fade1-x`, `@float2-x`, `@wipe3-x` (the number is the order).
- Plan a colour arc: muted/sepia scenes, then a bloom at the emotional turning point (longer 2 s Morph there).
- Anchor phrase as a `!!phrase` layer on 3 slides (setup, middle, end). Close the circle on the opening image.
- Record every layer name per scene in `NOTES.md` so later groups reuse them.

## 4. Build group by group
- One build child, resumed per group of 2-5 slides; each brief repeats the carried rules (allowed/forbidden frames, credit format, language, no false claims, correct page numbers) and the Vietnamese/target-language speaker notes for those slides.
- After every group: re-run `scripts/motion.py <unpacked_dir>` (it strips old transition wrappers, adds one Morph per slide with fallback fade, and builds entrances). Pass special durations as `--dur FILE=ms,FILE=ms`, keyed by slide FILE number (slideN.xml), so they survive re-runs without editing the script.
- Reusable layout helpers: `scripts/roles.py PPT_DIR SLIDE.xml --template TEMPLATE.xml` (three-column highlight walk states). Team video frames only inside a framed `!!screen` layer at <=45% slide width.
- Send each group's renders to the user as you go; accept their changes into the next brief.

## 5. Finish and deliver
- New finish child: merge notes into one continuous script, smooth scene hand-offs, scan for forbidden characters, check page numbers, confirm one transition per slide, confirm `!!` pairs, verify the credits slide against media actually embedded.
- Shrink: `scripts/finish_dedupe.py <unpacked_dir>` merges byte-identical media by hash (decks easily hit 100 MB from duplicates); downscale textures to <=2560 px. Chat attachments must be under 25 MB.
- Script document: `scripts/script_docx.py --notes NOTES.txt --scenes SCENES.json --out script.docx` builds a .docx by slide and scene with pause marks, time per scene and sources in grey. Estimate speaking time (Vietnamese about 130-150 syllables/min) and compare with any time limit; offer to trim.
- Deliver: .pptx, script .docx, fonts/ folder, and a zip of all three. Tell the user to install the fonts and preview Morph in PowerPoint 365, since LibreOffice renders only static keyframes.
- After the user is satisfied, run the clean phase.

## Quality bar
- Professional motion means many keyframes per idea, consistent layer names, and restrained type, not more effects.
- Accuracy beats decoration: drop any motif you cannot source to the subject.
- Honest framing of what is finished versus planned (label future items "Định hướng phát triển" / "Roadmap").
