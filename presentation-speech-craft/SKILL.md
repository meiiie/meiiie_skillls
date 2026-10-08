---
name: presentation-speech-craft
description: Write and time the spoken script for a presentation or pitch video. It covers a hook, an anchor phrase, emotional rhythm, marked pauses, a circular close, a word budget that fits the time limit, speaker notes in the deck, and a speaker-script .docx. Use when someone needs a talk track for slides, a contest presentation video, or a deck whose speaking time must fit a hard limit, or when they ask to learn from a reference talk.
---

# Presentation speech craft

The most common failure is timing: planning "N slides × 7 seconds" and delivering twice the allowed time. Real measurements:
a 48-slide deck planned at 5.6 min ran 11:53–13:36; a 34-slide deck planned at 6 min ran 8:28. **Budget words, not seconds.**

Scripts in `scripts/` (Python 3.9+, python-pptx, lxml, python-docx). `$S` = that folder.

## 1. Learn from a reference talk
Watch the real talk (`yt-dlp` video + auto-subtitles) and write `research/lessons.md` (`templates/lessons.md`) with observed techniques and timecodes.
Default reference: Dananjaya Hettiarachchi, "I See Something" (Toastmasters World Champion 2014, https://youtu.be/-wLEsZWevrA).
He opens with a prop (a rose crushed and dropped in a bin), repeats one anchor sentence, alternates humour and quiet, pauses
2–3 s on key lines, keeps fixed stage positions, and closes the circle (a whole rose from the same bin). He uses no slides.

## 2. Structure
- **Hook**: a sense, an object or a question. Never "Xin chào, hôm nay em xin trình bày…".
- **Anchor phrase**: one short sentence said 3 times (setup, middle, end). If there are slides, it sits on its own layer on those 3 slides.
- **Rhythm**: problem (quiet, muted) → turn (anchor #1) → the work (energetic, concrete) → proof (with caveats) → honest status → close (anchor #3).
- **Pauses**: write `[ngừng 2 giây]` / `[pause 2s]` in the notes. They count as time, not words.
- **Circular close**: return to the opening image or line, resolved.
- **Honesty**: claims only from the fact file; the owner's claims are framed as "chúng tôi thiết kế để…" / "the team says…"; keep caveats aloud.

## 3. Budget and measure
```bash
python $S/words_budget.py plan --minutes 6 --slides 34                    # ≈ 754 words at 130 wpm, minus pauses
python $S/words_budget.py measure deck.pptx --target 6:00 [--scenes scenes.json]   # or a notes .md / folder
```
Vietnamese presentation pace: 130 (careful) to 150 (fluent) words per minute; plan at 130. Silent keyframes carry 0–10 words.
Lines starting with Nguồn / Source / Ảnh / Motion / Ghi chú / Note / Cue / Credit are directions and are not counted. If the script is
more than 10% over, cut from the heaviest slides that `measure` lists.

## 4. Put the script into the deck and a document
```bash
python $S/ooxml.py unpack deck.pptx un && python $S/ooxml.py notes-get un --out notes.md      # edit '##### N' blocks
python $S/ooxml.py notes-set un notes.md && python $S/ooxml.py pack un deck_with_notes.pptx
python $S/script_docx.py --notes notes.md --scenes scenes.json --out KichBan.docx --title "Kịch bản thuyết trình"
```
`scenes.json` = `[{"name": "Cảnh 1 · Mở", "start": 1, "end": 3}, …]` (deck positions). The .docx shows scenes, slide numbers,
spoken text, grey source lines, pauses and time estimates per scene.

## 5. Hand-off tips for the presenter
Look into the lens on the hook question; let each slide's motion finish before speaking; stand still for the anchor phrase;
rehearse twice with a timer; end on the anchor phrase, then silence.

Building the deck itself (motion, research, assets): see the `motion-pptx-studio` skill.
