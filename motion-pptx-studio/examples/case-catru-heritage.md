# Case study A: Ca trù heritage pitch (48 slides, 14 scenes, Vietnamese)

**Brief.** A student team ("Neko Core") entered a contest with an animated video and a game design: "Hành Trình Tái Sinh
Nghệ Thuật Ca Trù Của Cậu Đàn Đáy", with a mascot đàn đáy called Đáy. The contest asked for "Video đội thi thuyết trình về
sản phẩm đã hoàn thành để phục vụ công tác chấm điểm và phát sóng": a recorded presentation, judged and **broadcast**.
The user asked for a motion pptx "chuyên nghiệp, đặc sắc, đạt tới mức tuyệt đỉnh nghệ thuật", and to learn from a reference
talk (https://youtu.be/-wLEsZWevrA).

## The corrections the user had to make (each one is now a gate)
| User's words | What had gone wrong | Rule / gate now |
|---|---|---|
| "Trông chưa ổn lắm, cần chọn font cần tài nguyên asset, mọi thứ khác nhé" | first family used default fonts and generic shapes | Gate 3: fonts checked for diacritics, real assets, samples rendered |
| "có khi nhiều slide để phục vụ cho một motion hoàn chỉnh, từng frame…" | one slide per idea, Morph used as a mere transition | Gate 4: ≥60% of scenes are keyframe runs of 3+ slides with `!!` layers |
| "Tìm hiểu kỹ văn hoá Ca Trù để tìm và tải backgroud… đảm bảo độ chính xác tuyệt đối" | backgrounds were procedural sơn mài and a **Đông Sơn drum** (no link to ca trù) | Gates 1–2: TRUE/WRONG lists, anatomy checklist, licensed real photos |
| "Ca Trù phải để tiếng Việt chứ nhỉ ?" | some labels in English; Han characters on pillars inside photos | brief.on_slide_language; check_deck CJK scan; inpaint text in photos |
| (after delivery) the script ran 11:53–13:36 | planned as "48 × 7 s = 5.6 min" | words_budget.py plan/measure; Gate 6 time check |

## Research outputs
- `catru_facts.md`: 43 sourced facts tagged [ĐÃ XÁC MINH] / [THỨ CẤP] / [TRANH CÃI] / [CHƯA RÕ]. Sources: the UNESCO nomination
  file and decision 4.COM 14.12 (urgent safeguarding list since 1/10/2009), Viện Âm nhạc, Bảo tàng Dân tộc học, VOV, VnExpress, books.
- A 12-point accuracy checklist, including: đàn đáy 3 strings, 3 staggered pegs, trapezoid body wider at the top, 10–11 high
  frets; trống chầu small and two-headed with **one** roi; phách with 2 beaters (one split) struck down onto the bàn phách;
  the singer is female; 56 thể cách per UNESCO.
- WRONG list: Đông Sơn drum (generic national symbol), Đông Hồ prints (another heritage), sơn mài and Lý–Trần clouds
  (decoration only); avoid "cô đầu" in titles; province names as of 2009.
- Pitfalls found: a typo year in a press article; "Lỗ Khê đình worships the ca trù ancestor" (false).
- Media audit of the team's own video: frames f_037–f_092 had AI errors (hands, 4 symmetric pegs, two drumsticks, sticks
  clapped together), so they were never used. Team frames appear only inside a framed screen at ≤45% width.
- `presentation_lessons.md` from the reference talk: prop hook, anchor ×3–4, ups and downs, muted → colour "magic", pauses, circular close.

## Assets
40 Commons/Openverse candidates reviewed → **16 kept**, 2 in `_uncertain/`, 7 rejected with reasons (one Flickr set titled
"Ca Tru" actually showed đàn tranh and sáo). Kept: performance photos (Michael Coghlan, CC BY-SA 2.0), đình Kim Ngân
(CC BY-SA 4.0), a historic photo (PD), a sedge-mat texture crop, and others. Two photos were inpainted to remove Han characters
(OpenCV TELEA, credited "(đã chỉnh sửa)"). Own drawings from the checklist: đàn đáy in 3 layers (head, neck, body on one
600×2400 canvas), a thẻ trù medallion (3 rings), chậu đồng with tallies, phách, trống chầu with one roi.

## Art direction
Cormorant (display) + Josefin Sans (labels and body); Bodoni Moda rejected (missing ơ ư ỹ ẫ), Great Vibes rejected (marks clash).
Lacquer black and red, gold #EBCB86 / #D9B26A, cream #F3E6CC, muted #BFA983. Colour arc: S1–S5 muted gold-sepia (veil rectangle
at 45–70%), **S6 colour bloom** when Đáy appears, then full colour.

## Scenes (48 slides)
S1 Hook (one string in darkness → three strings → đàn đáy assembles → "a string grows quiet" → title) · S2 Vấn đề ("2009" big
number morphs; the UNESCO label verbatim) · S3 Ba vai (highlight walk over phách / đàn đáy / trống chầu, `roles.py`) · S4 Thẻ trù
(why "trù": tallies fan out, drop into the chậu đồng; anchor #1 "Nghe thì lạ, hiểu rồi thương") · S5 Không gian (đình push-in,
sedge mat rises) · S6 Gặp Đáy (colour bloom) · S7 Video · S8 Game Ch.1 (book opens, screen inside) · S9 Game Ch.2 · S10 Định hướng ·
S11 Hiện tại · S12 Vì sao hiệu quả · S13 Kết (circular close: the string is restored) · S14 Nguồn.
Layers: `!!str1-3 !!ddHead/Neck/Body !!medW/T/C !!day !!phrase !!screen !!hl !!tru1-3 !!book/pageL/pageR !!item1-4 !!dot0-4 !!glow`.
motion.json `dur` = {12: 2000, 22: 2000, 47: 2000} (file numbers: the quiet string, the bloom, the close).

## Finish
srcRect fix for a stretched photo; credits checked against the embedded media; dedupe from 104 MB to 15.8 MB; delivered pptx +
script docx + fonts + CREDITS + zip. Measured script: 1663 words + 24 pauses = 11:53–13:36. **Lesson: budget words from the start.**

## What to copy
Research before design; count the instrument's parts; real photos with licences; a drawn layered hero object; a muted → bloom
colour arc; the anchor phrase on a dedicated `!!phrase` layer; the team's video frames framed small, never as cultural proof.
