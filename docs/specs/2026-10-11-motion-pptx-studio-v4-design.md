# Motion PPTX Studio v4: thiết kế

Ngày: 2026-10-11 · Trạng thái: đã được chủ repo duyệt hướng ("trực tiếp tiến hành theo hướng bạn đã nói")

## 1. Vấn đề

v3 chặn được deck *sai* (sai nguồn, sai bản quyền, sai nhạc cụ, quá giờ, ảnh đứng yên) nhưng không dạy và không tạo ra deck *đẹp*. Bằng chứng đo được:

- `check_deck.py` của v3 đánh FAIL chính deck mẫu `NEKO_CORE_CaTru_motion.pptx` (cặp 31→32 là một nhịp dừng có chủ ý).
- Luật storyboard "≥40% slide ghi mã fact trên slide" và "mỗi layout ≤3 cảnh" đi ngược deck mẫu (0 mã fact trên slide; vẻ đẹp đến từ một hệ thống nhất quán).
- Engine mặc định `build_deck.py` chỉ có 5 hình cơ bản, nền màu trơn, tắt đổ bóng, không nhóm, không thành phần dùng lại. Deck mẫu được dựng bằng PptxGenJS: thiết kế ~11 slide gốc rồi nhân bản thành 48 khung.
- Không có design system: khung, lưới, thang chữ, chữ ký thị giác (deck mẫu có khung viền + 3 dây đàn trên 48/48 slide).
- `make_assets_example.py` vẽ cứng asset ca trù; `cairosvg` chỉ là "khuyến nghị".
- Claude không bao giờ *thấy* chuẩn đẹp: examples chỉ là mô tả bằng chữ.
- Skill chỉ có 3 loại deck (heritage/product/other); người dùng cần một skill tổng quát.

## 2. Mục tiêu

Một skill tạo deck PowerPoint có motion (Morph) đạt chất lượng của các studio motion deck hàng đầu, cho mọi thể loại: văn hoá/di sản, ra mắt sản phẩm/công nghệ, gọi vốn, báo cáo kinh doanh/dữ liệu, giáo dục/khoa học, sự kiện/thương hiệu. Giữ nguyên các thế mạnh của v3: nghiên cứu có nguồn, ảnh có bản quyền, ngân sách lời nói, giao hàng đầy đủ.

Không thuộc phạm vi: thay PowerPoint bằng công cụ khác; video export; nhúng font vào pptx.

## 3. Ý tưởng cốt lõi (học từ Anatomy)

**Một deck motion là một phim ngắn quay trên một phim trường.**
1. *Phim trường (the set)*: một hệ thống thiết kế cố định: nền chất liệu, khung, lưới, thang chữ, màu theo vai trò. Engine áp dụng tự động, không đặt tay từng slide.
2. *Nhân vật chính (the signature)*: một vật thể/hoạ tiết riêng của chủ đề xuất hiện trên ≥80% slide dưới dạng lớp `!!`. Nhỏ khi nghỉ, thành nhân vật chính ở các khoảnh khắc lớn.
3. *Cú máy (the camera)*: mỗi cảnh là 3–5 khung hình mà bố cục thật sự thay đổi (lắp ráp, đẩy máy, đi highlight, lộ dần...).

## 4. Thành phần

| Thành phần | Thay đổi |
|---|---|
| `SKILL.md` | Viết lại: ngắn hơn, đặt tay nghề lên trước, chọn thể loại → style pack → signature; quy trình 8 bước; gate vẫn giữ nhưng gọn hơn và theo thể loại. |
| `references/craft.md` (mới) | Design system với số đo cụ thể (lưới, lề an toàn, thang chữ, màu theo vai trò, độ tương phản, chữ trên màn hình, chiều sâu, xử lý ảnh, 12 bố cục, anti-pattern). |
| `references/genres.md` (mới) | Playbook cho 7 thể loại: cung truyện, ý tưởng signature, style pack gợi ý, độ sâu nghiên cứu, kiểu bằng chứng, cạm bẫy. |
| `references/styles.md` (mới) | Danh mục style pack, cách tuỳ biến, cách tạo style từ brand board. |
| `references/reference-bar.md` (mới) | Chuẩn đẹp đo từ deck mẫu + ảnh contact sheet; quy trình so sánh cạnh nhau. |
| `assets/styles/*.json` (mới) | 5 style pack: `lacquer-heritage`, `noir-product`, `paper-editorial`, `boardroom-data`, `studio-pop`. Font OFL có tiếng Việt, đã kiểm tra glyph. |
| `scripts/build_deck.py` v4 | Tương thích ngược. Thêm: `style`, `chrome` (lớp cố định mọi slide, số trang tự động), `role` cho chữ, `col` theo lưới, nền ảnh, đổ bóng, hiệu ứng ảnh, góc bo ảnh, viền ảnh, `group`, thành phần (`heading`, `card`, `stat`, `screen`, `timeline`, `quote`, `bars`, `list`), kiểm tra tràn chữ, ghi `motion.json` từ deck.json. |
| `scripts/typeset.py` (mới) | Đo chữ bằng font thật (fc-match + Pillow) cho build và audit. |
| `scripts/make_assets.py` (mới) | Bộ công cụ asset tổng quát: `ground` (nền chất liệu), `foil` (dát vàng/bạc/đồng/mực/phấn/neon từ SVG/PNG), `layers` (tách SVG thành lớp cho Morph), `photo` (duotone/grade/vignette/mono+màu), `glow`, `pattern`. |
| `scripts/fetch_fonts.py` (mới) | Tải font của style pack, tạo bản static, cài vào máy render, chạy check_fonts. |
| `scripts/studio.py` (mới) | Một lệnh: `new` (khởi tạo theo style), `build` (build→unpack→motion→pack→check→render), `compare` (đặt render cạnh deck mẫu). |
| `scripts/craft_audit.py` (mới) | Kiểm tra tay nghề: signature bền, tràn chữ, lề an toàn, số cỡ chữ, số họ font, độ tương phản (khi có render). |
| `scripts/visual_audit.py` | Hiệu chỉnh: deck mẫu phải PASS. Cho phép "nhịp dừng" (text beat) ≤1/cảnh và ≤10% số cặp. Bỏ luật mã fact trên slide (chuyển sang nguồn trong notes/storyboard). |
| `scripts/gates.py` | Thêm thể loại; Gate 3 kiểm tra style + signature + mẫu render so với chuẩn; Gate 4 bỏ luật mã fact trên slide và luật layout cứng, thêm cột `source`. |
| `scripts/motion.py` | Thêm tuỳ chọn Morph theo slide (`byObject`/`byWord`/`byChar`). |
| `examples/` | Thêm 2 deck mẫu dựng bằng engine mới (sản phẩm công nghệ, câu chuyện dữ liệu) + contact sheet deck ca trù làm chuẩn. |
| `tests/` (mới) | pytest cho engine, asset kit, audit, motion; deck mẫu là fixture hồi quy. |

## 5. Luồng dữ liệu

`brief.md` → research (độ sâu theo thể loại) → `design/style.json` (từ style pack) + signature → `deck.json` → `studio.py build` (pptx + motion + audit + render) → nhìn render, so cạnh chuẩn, sửa → `deliver.py`.

## 6. Xử lý lỗi

Mọi script báo lỗi có tên slide/shape và cách sửa. Thiếu font: build vẫn chạy, cảnh báo "không đo được tràn chữ". Thiếu cairosvg: `foil` dùng rsvg-convert, nếu không có thì báo lệnh cài.

## 7. Kiểm thử

- pytest cho từng tính năng engine (mở pptx kết quả và kiểm XML).
- Hồi quy: deck mẫu ca trù PASS `check_deck.py` (khi có file; biến môi trường `MOTION_REF_DECK`). Deck "slogan" tổng hợp kiểu Genshin vẫn FAIL.
- Hai deck ví dụ build sạch, audit PASS, render được nhìn từng slide.
- Eval: so sánh v3 và v4 trên cùng đề bài bằng subagent.

## 8. Tiêu chí hoàn thành

1. Deck mẫu PASS audit mới; deck lỗi kiểu Genshin vẫn FAIL.
2. Hai deck ví dụ khác thể loại đạt cùng "look" chuyên nghiệp: chrome, signature, thang chữ, nền chất liệu.
3. Toàn bộ test xanh; companion skills được đồng bộ; README, CHANGELOG cập nhật.
