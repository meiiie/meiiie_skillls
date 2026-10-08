---
name: heritage-visual-research
description: Research a cultural or heritage subject (art form, craft, festival, instrument, place) and collect accurate, openly licensed images with a verified credits file. Use before designing any slide deck, video, poster, game or website about a culture, or whenever someone asks for visuals that must be "chính xác tuyệt đối" or culturally accurate. It produces a sourced fact file, a true/wrong motif list, an object anatomy checklist, an audit of the user's media, and a folder of kept images with licences.
---

# Heritage visual research

The work that stops "beautiful but wrong" visuals: an invented national motif, a neighbouring art form's
instrument, an AI image with four pegs on a three-peg lute, Han characters on a pillar in a Vietnamese-only deck.
Standard (user's words): *"Tìm hiểu kỹ văn hoá … để tìm và tải background sao cho phù hợp nhé và đảm bảo độ chính xác tuyệt đối."*

Scripts are in `scripts/` (Python 3.9+, Pillow, lxml; opencv + numpy for inpainting; ffmpeg for video frames). `$S` = that folder.

## Steps (do all of them; write the outputs into `research/` and `assets/` of the project)

1. **Read the user's material first.** Briefs, rules, their video (`python $S/video_frames.py v.mp4 --out research/frames --every 5 --sheet`), earlier documents.
2. **Facts with sources** (`templates/facts.md` → `research/facts.md`). Source ladder: UNESCO file / national institute / museum →
   universities and state media → books and quality press → blogs (only to find better sources). Search in the local language
   and in English, with and without diacritics. Fetch and quote the pages; save them. Tag each fact
   `[verified] [secondary] [claim] [disputed] [uncertain]`. Aim for at least 15 facts from 3 or more domains.
3. **Do-not-say list**: false or unproven claims that are tempting (wrong dates in press, wrong place attributions, pejorative terms).
4. **TRUE / WRONG visual lists + anatomy** (`templates/accuracy.md` → `research/accuracy.md`):
   - TRUE: the objects, instruments, places, roles and symbols the sources tie to the subject.
   - WRONG: generic national icons (for Vietnam, e.g. the Đông Sơn drum, unless a source links it), neighbouring art forms,
     separate heritages, decoration taken for content, AI glow.
   - Anatomy: counts and shapes (e.g. đàn đáy: 3 strings, 3 staggered pegs 2+1, trapezoid body wider at the top; trống chầu:
     one beater; phách: two beaters, one split, struck down onto the bàn phách; the singer is female).
5. **Audit the user's media** frame by frame: OK / keep small / never use, with the reason.
6. **Collect images** and keep only verified ones:
   ```bash
   python $S/fetch_commons.py search "ca trù" --out assets/candidates        # repeat: local, English, no diacritics, object names
   python $S/fetch_commons.py keep "<id>" --as 01_name.jpg --why "<what it shows> (facts X.Y)" --dest assets --credits assets/CREDITS.md
   python $S/contact_sheet.py assets --out assets/contact.jpg                # LOOK at it against accuracy.md
   ```
   Review at least twice as many candidates as you keep, and write down the rejected ones with reasons. Licences: CC0 / PD / CC BY / CC BY-SA;
   no NC/ND for contests, broadcast or commercial use. If the subject is unverified, use `--uncertain` (atmosphere only, never captioned).
7. **Prepare**: `cutout.py` (museum objects on white → transparent PNG), `inpaint_text.py` (remove foreign script inside photos;
   credit "(đã chỉnh sửa)"; BY-SA stays BY-SA). Keep originals.
8. **Fonts for the language** (if the output has text): `python $S/check_fonts.py font.ttf --lang vi --png sample.png`, then look at the sample.

## Done when
`research/facts.md` (sourced, tagged, with a do-not-say list), `research/accuracy.md` (TRUE, WRONG, anatomy, media audit),
`assets/` with kept files, `assets/CREDITS.md` (every row: file, subject, why accurate, source URL, author, licence,
attribution) and a "Rejected" section, and `assets/contact.jpg` of the kept set, which you have looked at.

Real false positives this method caught: a "Ca Tru" Flickr set showing đàn tranh and sáo; string quartets for "dan day";
a North Carolina road sign for "NC CA TRU". Titles are not evidence: look.

For a full motion deck built from this research, use the `motion-pptx-studio` skill (its Phases 1–2 are this skill).
