# Cultural and visual accuracy (heritage topics, and any topic with real objects)

"Đảm bảo độ chính xác tuyệt đối" means that every motif, object, colour and photo on a slide must be
something that **really belongs to the subject**, with a source. Beautiful but generic is a defect.

## 1. Build the TRUE list before choosing any visual
For the art form, festival, craft or place, collect:
- **Objects and instruments** that are part of it (for ca trù: đàn đáy, phách with bàn phách, trống chầu, thẻ trù
  / thẻ tre, chậu đồng, chiếu cói).
- **Places** (đình làng, ca quán, a named temple), with the place shown in the actual photo verified.
- **People and roles** (ca nương is female and plays the phách; kép đàn plays the đàn đáy; quan viên plays the trống chầu).
- **Symbols that the sources themselves use** (the tally that gives the name "trù").
- **Colours and materials** documented for the subject (lacquer, gold leaf, bamboo, sedge mat), and not "national colours".

## 2. Build the WRONG list (tempting associations that fail the subject)
Typical traps:
| Trap | Example | Rule |
|---|---|---|
| Generic national icon | Đông Sơn bronze drum, nón lá, lotus as "Vietnam" | only if a source links it to *this* subject |
| Neighbouring art form | đàn tranh / sáo in a "Ca Tru" Flickr set; quan họ, chèo costumes | verify instrument by instrument |
| Separate heritage | Đông Hồ woodblock prints in a ca trù deck | a different heritage, so don't mix it in |
| Decorative style taken as content | sơn mài, Lý–Trần cloud scrolls | allowed as *generic decoration* only, never captioned as the subject |
| AI aesthetics | glow, purple gradients, fantasy gold particles | never on heritage, and never on a brand that forbids it |
| Foreign script | Han characters on pillars, plaques or couplets in photos | crop or inpaint when the brief says Vietnamese only |

## 3. Object anatomy checklist (count things)
Write counts and shapes from rung-1/2 sources and check every image and every drawing against them:
- đàn đáy: **3 strings, 3 pegs staggered (2 on one side, 1 on the other)**, flat head, trapezoid body **wider at
  the top**, 10–11 high frets on the lower part of the long neck.
- trống chầu: small, two heads, **one** beater (roi chầu).
- phách: played by the singer with **two beaters, one of them split**, striking **down onto** the bàn phách
  (not two sticks clapped together).
- For products: logo proportions and colours, the cat beside (not inside) the logo, the exact wordmark case.

## 4. Audit the user's own media (frames, renders, AI images)
The user's video may contain errors of its own, and AI-generated frames often do. Grade each frame in
`accuracy.md`:
| frame | verdict | reason |
|---|---|---|
| f_013 | OK | mascot close-up, correct 3 strings |
| f_037–f_092 | never use | AI hands with extra fingers; đàn đáy with 4 symmetric pegs; phách sticks clapped |
| f_148 | keep small | trio correct but low resolution: use at ≤45% slide width inside a frame |
Rule from the ca trù project: team frames go only inside a framed "screen" at ≤45% width, never as a
cultural close-up, so the deck never presents a wrong instrument as the real thing.

## 5. Drawing your own motifs
When no licensed photo exists, draw the object (SVG, cairosvg, or PIL) **from the anatomy checklist**, and
split it into layers for Morph (head, neck and body of the đàn đáy on one shared canvas; strings as live lines).
Show the drawing next to the checklist in a render and verify the counts before using it.

## 6. Language hygiene
- On-slide language = the audience's language. The user's correction "Ca Trù phải để tiếng Việt chứ nhỉ?" means
  everything visible is Vietnamese, including labels, captions, credits ("Ảnh:", "đã chỉnh sửa") and chart axes.
- Scan slides for forbidden scripts: `check_deck.py` flags CJK in text (add `--forbid-notes` for notes too).
  It cannot see text **inside images**: look at each photo, then crop or `inpaint_text.py` it.
- Respect sensitive terms (for example avoid "cô đầu" in titles) and spell names with full diacritics.

## 7. When in doubt
Move the image to `assets/_uncertain/` (unlabelled atmosphere at most), use a drawn motif from the TRUE
list, or ask the user one precise question ("Is this photo from Đình Lỗ Khê?").
