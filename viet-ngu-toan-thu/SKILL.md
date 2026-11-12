---
name: viet-ngu-toan-thu
description: Use when Vietnamese prose, poetry, editing, dialogue, texting, teencode, regional register, grammar, or meaning needs careful handling, or the user invokes Việt ngữ toàn thư. Not a grammar for every language of Vietnam.
license: MIT
metadata:
  version: "3.0.0"
---

# Việt ngữ toàn thư

Viết đúng việc, đúng người, có giọng sống. Bản văn là sản phẩm; kiểm tra hỗ trợ bản văn. Đây là hướng dẫn có giới hạn, không phải kho tri thức đã học hết tiếng Việt.

## Chọn đúng chế độ

| Đầu vào / việc giao | Làm gì, đọc gì |
|---|---|
| Có nguyên văn để sửa | Giữ ý và giọng; đọc [bảo toàn nghĩa](references/meaning-and-causality.md). Đoạn đã đạt có thể giữ nguyên. |
| Viết truyện, tản văn, miêu tả | Dựng cảnh, điểm nhìn, nhịp; đọc [văn chương](references/literary-craft.md). |
| Thơ, đặc biệt lục bát | Đọc [thi pháp](references/poetry.md); phân biệt thể chuẩn, biến thể và thơ tự do. |
| Tin nhắn, hội thoại, teencode, Gen Z | Đọc [ngữ dụng và nhắn tin](references/texting-pragmatics.md). |
| Giải thích tiếng Việt hoặc tri thức Việt Nam | Đọc [tri thức và nguồn](references/knowledge-and-corpora.md); khi cần dữ kiện hiện hành phải tra nguồn. |
| Văn bản chuyên môn, hành chính, kỹ thuật | Đọc [thể loại](references/genres-and-register.md), [hồ sơ văn bản](references/document-profiles.md) và [bảo toàn nghĩa](references/meaning-and-causality.md). |

Chọn từ yêu cầu thực, không từ một từ khóa. Ưu tiên nguyên văn và mẫu giọng người dùng hơn nhãn tuổi/vùng. Thiếu thông tin không thiết yếu thì dùng giọng ít giả định; chỉ hỏi khi thiếu đó quyết định nghĩa, quan hệ hoặc nội dung cần gửi. Soạn tin không có nghĩa là được gửi.

## Một lượt viết, một lượt đọc thật

1. Xác định đầu ra: tác phẩm hay bản sửa; độc giả, quan hệ, nơi dùng và ràng buộc đã được nêu. Giữ nguồn riêng khi làm việc với tệp. Trong sáng tác hư cấu được tạo chi tiết; trong thông tin chỉ dùng dữ kiện có căn cứ.
2. Viết một bản có trục rõ. Văn cảnh đi theo vật/người và biến đổi quan sát được; tin nhắn hoàn thành hành vi giao tiếp; văn chuyên môn giữ điều kiện và độ chắc chắn. Đừng dùng chung giọng báo cáo cho mọi việc.
3. Đọc như người nhận. Tìm nơi chủ thể bị trôi, bổ ngữ gắn nhầm, hình ảnh không thể theo dõi, nhịp lặp vô ý, lời nói quá thân/quá lạnh. Khi sửa, đối chiếu sáu bất biến và cả sắc thái. Nếu đại từ có nhiều tiền ngữ, **giữ đại từ trong bản sửa**; khi đầu ra cho phép thì hỏi riêng, không thay tên rồi mới xin xác nhận.
4. Chỉnh chỗ có vấn đề cụ thể. Với bản văn ngắn, rà thủ công là mặc định. Với tệp cần kiểm toán, sửa dài hoặc yêu cầu kiểm bằng máy, dùng [kiểm tra](references/checking.md); công cụ không quyết định văn hay, đúng nghĩa hay phù hợp văn hóa.

Ví dụ: sửa tối thiểu “mai tui ghé nha, bà có nhà hong :)))” có thể giữ nguyên. Đây đã là một tin nhắn thân mật có chức năng; đổi thành “Ngày mai tôi sẽ đến, bạn có ở nhà không?” làm thay giọng và tăng mức cam kết.

## Tra đúng chỗ

- Câu, đề–thuyết, tham chiếu: [ngữ pháp](references/grammar.md). Chính tả/Unicode: [trình bày](references/orthography-and-punctuation.md).
- Câu dịch cứng, danh từ rỗng, ẩn dụ: [biên tập sâu](references/editorial-techniques.md). Thiếu dữ kiện: [phục hồi dữ kiện](references/fact-recovery.md).
- Vùng giọng, cộng đồng: [biến thể](references/regional-and-community.md), [phạm vi](references/coverage-registry.md). Không coi các ngôn ngữ dân tộc khác là phương ngữ tiếng Việt.
- Corpus, bản quyền, tri thức: [nguồn nghiên cứu v3](references/research-provenance.md), [nguồn nền](references/sources.md). Dữ liệu chuẩn hóa không phải tiêu chuẩn bắt mọi người nhắn tin giống nhau.
- Host/quyền chạy: [tích hợp](references/host-integration.md). Nguồn gốc thiết kế: [kiến trúc](references/architecture.md).

## Giao kết quả

Trả đúng dạng đã xin: một tin thì một tin, chỉ thơ thì chỉ thơ. Bản sửa trước; nhận xét sau chỉ khi hữu ích hoặc được yêu cầu. Không chèn quy trình/lint vào tác phẩm. Báo trung thực kiểm tra chưa chạy khi người dùng hỏi hoặc cần bàn giao kiểm toán. Không suy ra chất lượng từ số cảnh báo, hash hoặc số bài kiểm thử. Bằng chứng trong `evals/` phân biệt kiểm code, mẫu hành vi và nhận xét thẩm mỹ.
