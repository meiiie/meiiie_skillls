# Báo cáo nghiên cứu · motion-pptx-studio v5 (20/10/2026, giờ Sài Gòn UTC+7)

Mục tiêu: hiểu các bộ PPTX "chuyên về chuyển động" làm gì ngoài Morph, cái nào ta tự sinh được bằng OOXML,
cái nào chạy được ở đâu, và dựng một thư viện phong cách thật sự khác nhau (bố cục, không chỉ đổi màu).

## 1. slidewppt.vn: họ thực sự làm gì

**Nguồn.** Trang chủ https://slidewppt.vn/ và danh mục https://slidewppt.vn/cac-mau-slide/ có 153 sản phẩm.
Các nhóm: Bộ phim, Ứng dụng, Hệ điều hành, Mini game, Ngẫu hứng, Nhãn hàng, Du lịch, Tình yêu, Premium…
(ví dụ https://slidewppt.vn/danh-muc-san-pham/ung-dung/). Đã đọc trang sản phẩm của:
- https://slidewppt.vn/san-pham/netflix-slide/
- https://slidewppt.vn/san-pham/macos-slide/
- https://slidewppt.vn/san-pham/desktop-theme-slide/
- https://slidewppt.vn/san-pham/paper-slide/
- https://slidewppt.vn/san-pham/scribble-it-slide/
- https://slidewppt.vn/san-pham/ngau-hung-slide-10/
- https://slidewppt.vn/san-pham/ai-la-trieu-phu-slide/
- https://slidewppt.vn/san-pham/slide-mo-dau-ao-dieu/

Tải được 6 bộ công khai (Google Drive do trang dẫn): Doraemon, Facebook, Facebook 2021, Netflix, Spotify, Spotify 2.

**Đo bằng XML (6 bộ, 104 slide).**

| Bộ | Slide | Chuyển cảnh | Hiệu ứng | Khác |
|---|---|---|---|---|
| Doraemon | 16 | morph 6 · push 5 · fade 4 · flash 1 | 14 xuất hiện, 4 đường chuyển động, 1 thoát, 1 chữ từng ký tự | 5 GIF |
| Facebook | 18 | fade 16 · push 1 · morph 1 | 67 xuất hiện, 18 đường chuyển động, 5 thoát | |
| Facebook 2021 | 21 | morph 8 · push 7 · fade 6 | 51 xuất hiện, 12 đường, 14 iterate | 33 hyperlink (menu bấm để nhảy) |
| Netflix | 12 | fade 9 · push 3 | 22 xuất hiện, 2 đường | nhạc nền mp3 (mediacall) |
| Spotify | 15 | morph 13 · fade 1 · none 1 | 27 xuất hiện, 2 iterate | |
| Spotify 2 | 22 | fade 18 · morph 2 · push 1 · none 1 | 70 xuất hiện, 14 đường | |

Tổng cộng:
- **Chuyển cảnh:** fade 54/104, Morph chỉ 30/104 (29%), push 17.
- **Hiệu ứng:** 251 hiệu ứng xuất hiện, 50 đường chuyển động, 17 hiệu ứng chạy từng chữ/từng ký tự.
- **Khác:** hyperlink, GIF, âm thanh. Nhiều ảnh dùng hiệu ứng nghệ thuật (.wdp).

**Bài học.**
1. Sức hút đến từ **ý tưởng giao diện quen thuộc** (app, hệ điều hành, game show, giấy, nét vẽ tay), dựng lại bằng shape thật và chỉnh sửa được.
2. Chuyển động là nhiều lớp nhỏ: fade/push giữa các cảnh, các vật bay vào theo nhịp, đường chuyển động, chữ chạy, menu bấm nhảy, nhạc.
3. Morph dùng có chủ đích cho vài cảnh "camera", không phải cho mọi slide.

Bản v4 chỉ có Morph + 3 hiệu ứng nên bị đơn điệu; đó là lý do của v5.

## 2. Kỹ thuật: có sửa được không, có tự sinh được không, chạy ở đâu

Ký hiệu cột: ✓ = chạy · ~ = chạy một phần hoặc thay bằng hiệu ứng khác · ✗ = không. "OOXML sửa được" nghĩa là sau khi sinh, người dùng vẫn mở và chỉnh được trong PowerPoint.

| Kỹ thuật | OOXML sửa được | Skill tự sinh | PPT 365 / 2019 | PPT 2016 | Google Slides | Keynote | LibreOffice | Dự phòng |
|---|---|---|---|---|---|---|---|---|
| Morph (`p159:morph`) | ✓ | ✓ | ✓ | chỉ phát (C2R) | ✗→fade | ✗ (tương tự Magic Move) | ✗ | fade (đã viết sẵn trong AlternateContent) |
| Chuyển cảnh cơ bản (fade, push, wipe, cover, split, dissolve…) | ✓ | ✓ | ✓ | ✓ | ~ (chỉ có fade/slide/flip/cube/gallery/dissolve) | ~ | ✓ | fade |
| Chuyển cảnh Office 2010 (`p14`: vortex, ripple, flash, gallery…) | ✓ | ✓ | ✓ | ✓ | ~ | ~ | ~ | fade |
| Chuyển cảnh Office 2013 (`p15:prstTrans`: curtains, fall over, airplane…) | ✓ | ✓ | ✓ | ✗→fade | ✗ | ✗ | ✗ (curtains→none, fallOver→wipe) | fade |
| Xuất hiện / nhấn mạnh / thoát (fly, zoom, wipe, pulse, teeter, spin…) | ✓ | ✓ | ✓ | ✓ | ~ (fade, fly, zoom, spin) | ~ | ✓ (đã kiểm) | xuất hiện thẳng |
| Đường chuyển động, quỹ đạo, lặp vô hạn | ✓ | ✓ | ✓ | ✓ | ✗ | ~ | ✓ | vị trí tĩnh |
| Chữ chạy từng ký tự / từng từ (`p:iterate`) | ✓ | ✓ | ✓ | ✓ | ~ (theo đoạn) | ~ | ✓ | hiện cả đoạn |
| Trigger (bấm vào vật) | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ~ | đặt vào chuỗi click |
| Hyperlink sang slide (menu) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Video MP4 tự chạy/lặp | ✓ | ✓ | ✓ | ✓ | ~ (cần đưa lên Drive) | ✓ | ~ | ảnh poster |
| Zoom (Summary/Slide/Section) | ✓ | ✗ (chỉ làm bằng UI) | ✓ | chỉ chạy như link | ✗ | ✗ | ✗ | menu link |
| Mô hình 3D, cameo, phát lại nét vẽ | ✓ | ✗ | ✓ (365) | ✗ | ✗ | ✗ | ✗ | MP4 dựng sẵn |

Nguồn:
- Morph: https://support.microsoft.com/en-us/office/use-the-morph-transition-in-powerpoint-8dd1c7b2-b935-44f5-a74c-741d8d9244ea
- Zoom: https://support.microsoft.com/en-us/office/use-zoom-for-powerpoint-to-bring-your-presentation-to-life-9d6c58cd-2125-4d29-86b1-0097c7dc47d7
  (PowerPoint 2016 chỉ chạy Zoom như hyperlink; bản web không chạy).
- Google Slides: https://support.google.com/docs/answer/1689475
- OOXML: ECMA-376 https://ecma-international.org/publications-and-standards/standards/ecma-376/
  và phần mở rộng [MS-PPTX] https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/

Mức kiểm chứng của bảng:
- **Kiểm trực tiếp:** cột LibreOffice (`verify_motion.py`, round-trip sang ODP).
- **Theo tài liệu:** cột PowerPoint.
- **Chưa kiểm trên máy, ghi theo kinh nghiệm import, cần xác nhận:** cột Google Slides và Keynote.

## 3. Hai nguồn cộng đồng gợi ý
- **Anatomy** (https://skills.wheresryan.sh/anatomy): giải thích một vật bằng cách vẽ chính nó, tách lớp, chú
  thích đặt cạnh từng bộ phận. Trong skill thành phong cách `blueprint`: ghép lại → tách rời (Morph) → chú thích
  chạy theo đường dẫn. Mẫu thử là chiếc phin vẽ bằng shape.
- **ManimGX** (https://manimgx.academa.ai/): dùng API Manim với lõi Rust. Đã cài trên box (v0.1.1, Python 3.13)
  và render 1080p60 bằng `manimgx render scene.py`. Dùng để dựng phim toán/thuật toán, chèn vào slide dạng
  `video` có ảnh poster. Với sơ đồ kiến trúc/quy trình, skill có `diagram_video.py`: không cần cài thêm, xuất ra
  MP4 kèm một bản shape sửa được có hiệu ứng gốc.

## 4. Danh mục phong cách (font đều OFL, đã kiểm đủ dấu tiếng Việt)

| Pack | Bảng màu | Font | Ngữ pháp bố cục | Chuyển động đặc trưng |
|---|---|---|---|---|
| kinetic-type | đen #0B0B0C · kem #F4F1EA · đỏ #FF4D33 | Anton / Inter / Space Mono | chữ 110–150 pt là hình; 2 dòng, dòng hai màu nhấn; menu chữ lớn có link | gõ từng ký tự, cắt theo nhịp, một giọt rơi + lặp |
| blueprint | xanh bản vẽ #0D2D52 + lưới · nét #E8F1FF · hổ phách #FFB627 | Space Grotesk / Be Vietnam Pro / JetBrains Mono | vật vẽ tay bên trái, chú thích mono bên phải nối bằng nét chấm, khung tên bản vẽ | ghép → tách (Morph), chú thích wipe, bộ phận sáng "thở", phim sơ đồ |
| swiss-blue (lựa chọn trắng-xanh) | trắng · mực #0B1B3F · cobalt #1F4BFF | Archivo / Inter / IBM Plex Mono | lưới 12 cột, mảng cobalt tràn lề với một con số khổng lồ, lưới 10×10, biểu đồ dốc theo chỉ số | push, các hàng wipe so le, Morph giữa hai trạng thái biểu đồ |
| neo-brutal | ngà #F3EEE3 / chanh #C5F25A · mực · cam #FF5A36 | Dela Gothic One / Space Grotesk / Space Mono | poster: số khổng lồ, ảnh như sticker nghiêng có viền + bóng cứng, băng nhãn | drop, teeter khi bấm (trigger), từng bước theo click, cover |
| retro-terminal | đen CRT + scanline · lân quang #A6FFA6 · hổ phách #FFB000 | VT323 / IBM Plex Mono | dấu nhắc lệnh, lệnh làm tiêu đề, kết quả từng dòng | gõ lệnh, dòng hiện so le, con trỏ nhấp nháy, dissolve |
| lacquer-heritage (v4) | sơn mài #0E0A07 · vàng | Cormorant / Be Vietnam Pro | khung vàng, số năm lớn, ray thời gian | camera lia dọc ray (Morph), curtains |
| noir-product, paper-editorial, boardroom-data, studio-pop (v4) | xem `references/styles.md` | | | |
| glass-tech, papercut-collage, desktop-os | đã có bảng màu, font và nền (`mesh`, `paper`) | | **chưa có bố cục riêng** → để trong `styles-experimental` | |

Font không đạt dấu tiếng Việt (bị loại): Archivo Black, Sora, Syne, Rubik, Instrument Sans/Serif, DM Serif Display,
Red Hat Display, Orbitron, Pixelify Sans, Zilla Slab, Lilita One, Rubik Mono One.

## 5. Kết luận cho skill
- Không có template mặc định. Mỗi bộ slide phải ghi phong cách được chọn và phong cách bị loại (Gate 3).
- Mỗi bộ chọn 2–4 kỹ thuật chuyển động đặc trưng ngoài Morph (Gate 3; `check_deck` cảnh báo khi đơn điệu).
- Starter deck chỉ dùng để kiểm hệ thống, không phải "mẫu phong cách". Bài học từ gallery 13 kiểu bị chê là
  những bản đổi màu của cùng một bố cục.

**Giới hạn của nghiên cứu.**
- Chỉ đo 6 bộ công khai trên tổng 153 sản phẩm; các bộ Premium không tải được.
- Chưa kiểm chứng phát trên PowerPoint thật, Google Slides hay Keynote.
