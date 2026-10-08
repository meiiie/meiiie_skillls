# Delivery (Phase 6 → Gate 6)

## 1. Finish the deck
```bash
python $S/finish_dedupe.py WORK/deck/unpacked          # identical media merged, oversized images downscaled
python $S/ooxml.py clean WORK/deck/unpacked            # unused slides + orphan media removed
python $S/motion.py WORK/deck/unpacked                 # once more, after the last edit
python $S/ooxml.py pack WORK/deck/unpacked WORK/deck/final.pptx
python $S/check_deck.py WORK/deck/final.pptx --anchor "…" --max-mb 25
bash   $S/render.sh WORK/deck/final.pptx WORK/renders/final-1     # look at every tile one last time
python $S/words_budget.py measure WORK/deck/final.pptx --target 6:00
```
- Credits slide: every CC BY/BY-SA image with author, title, licence, source; "(đã chỉnh sửa)" for edits; fonts (OFL).
- Compare CREDITS.md with the media actually embedded (`ooxml.py inventory` lists the pictures): no missing credit, no stale row.
- Size: most contest portals accept ≤ 25–50 MB; downscale photos to 2560 px wide (1920 for insets).

## 2. Package
```bash
python $S/deliver.py WORK --deck WORK/deck/final.pptx --name CaTru_Motion --title "Ca trù — kịch bản thuyết trình" \
       [--scenes WORK/scenes.json] [--subtitle "Đội …"]
python $S/gates.py check WORK --gate 6
```
`WORK/deliver/` then contains:
| File | What |
|---|---|
| `Name.pptx` | the deck (Morph, entrances, notes) |
| `Name_KichBan.docx` | speaker script per scene with time estimates (`script_docx.py`) |
| `fonts/` | static TTFs, OFL licences, `README_FONTS.txt` (Windows, macOS and Linux install steps, in Vietnamese and English) |
| `CREDITS.md` | image and source credits |
| `Name.zip` | everything above in one file |
Scenes for the script come from storyboard.md scene IDs unless you pass `--scenes`.

## 3. Fonts on the presenter's machine
Fonts are not embedded (PowerPoint embedding is unreliable for OFL TTFs across platforms). The presenter must
install `deliver/fonts/*.ttf` **before** opening the deck, then restart PowerPoint. If you can run commands on the
user's own computer (with their approval), install them for them:
- Windows (PowerShell, current user): copy to `$env:LOCALAPPDATA\Microsoft\Windows\Fonts` and register each one under
  `HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts` (name → full path), or right-click → Install for all users.
- macOS: `cp *.ttf ~/Library/Fonts/`. Linux: `cp *.ttf ~/.local/share/fonts/ && fc-cache -f`.
Ship **static** instances: variable fonts showed wrong weights in PowerPoint during the neko-core delivery.

## 4. Hand-off message (template)
```
Đã xong: <Name>.pptx (<N> trang chiếu, <S> cảnh) + kịch bản <Name>_KichBan.docx + fonts/ + CREDITS.md (zip: <Name>.zip).
Thời lượng lời đọc đo được: <a–b> phút (mục tiêu <T>). <If over: Đã cắt … / Cần bạn đồng ý …>
Cài font trước khi mở: <fonts>. Mở bằng PowerPoint 365/2019+ để thấy Morph và hiệu ứng (bản render LibreOffice không có chuyển động).
Quyết định tôi tự chọn: <…>. Nội dung không đưa lên slide vì chưa xác minh được: <…>.
Nguồn ảnh: <n> ảnh CC/PD, <m> ảnh của đội; danh sách đầy đủ ở trang cuối và CREDITS.md.
```
Upload or send the files only when the user asked for it, and to the destination they named.
