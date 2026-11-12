# Thơ tiếng Việt: tai nghe, thể thơ và ý

Chọn thể từ yêu cầu: lục bát truyền thống, lục bát biến thể, năm/bảy tiếng, Đường luật, thơ tự do không dùng cùng một bộ kiểm. Đếm tiếng không phải đếm từ vựng: “quê hương” thường là hai tiếng nhưng có thể là một đơn vị từ vựng. Nêu quy ước khi yêu cầu “từ” chưa rõ và cần giới hạn chặt.

## Lục bát truyền thống cơ bản

Cặp câu sáu–tám tiếng. Những vị trí chẵn thường theo khung:
- Câu sáu: tiếng 2 bằng, 4 trắc, 6 bằng.
- Câu tám: tiếng 2 bằng, 4 trắc, 6 bằng, 8 bằng.
- Vần: tiếng 6 câu sáu nối tiếng 6 câu tám; tiếng 8 câu tám nối tiếng 6 câu sáu tiếp theo.
- Bằng: ngang, huyền. Trắc: sắc, hỏi, ngã, nặng. Trong câu tám, vị trí 6 và 8 thường phối ngang–huyền để tránh bằng phẳng, không đồng nhất quy tắc này với mọi biến thể lịch sử.

Đây là khung học/viết thể chuẩn, không đủ để phán cả truyền thống. Có lục bát biến thể, vần thông và đổi nhịp; tác phẩm lệch khung không tự động là “thơ sai”. Nếu người dùng yêu cầu lục bát chuẩn, thực hiện khung trước; nếu sửa văn bản có sẵn, hỏi/ghi rõ lựa chọn giữ biến thể thay vì tự cắt tiếng.

## Viết từ hình ảnh, không từ danh sách vần

Chọn hành động và quan hệ cảm xúc có thể chịu được bốn câu, rồi dựng hai câu nối. Đọc lại nghĩa từng cụm sau khi tìm vần: từ vừa đủ âm có tự nhiên không, có đảo cú pháp miễn cưỡng không, câu sau có phát triển câu trước không? Đổi cả câu khi vần kéo nghĩa đi sai, không chỉ nhét một chữ đệm. Lục bát không bắt buộc nói về làng quê hay dùng “quê hương”, “bình yên”.

Rà ba lượt tách biệt: (1) ý và hình ảnh; (2) số tiếng, thanh, mối nối vần; (3) đọc nghe nhịp. Một bài đủ 6–8 vẫn có thể gượng, sáo và vô nghĩa. Một bài thơ tự do không cần bị ép vào khung 6–8.

## Công cụ hỗ trợ

`scripts/luc_bat.py` cung cấp chẩn đoán hình thức, không tự sửa và không chứng nhận thơ hay. Đọc trợ giúp bằng `python3 SKILL/scripts/luc_bat.py --help`. Kết quả giữ văn bản gốc, phân tích Unicode chuẩn hóa và báo phần không thể suy chắc. Khi có mã, số, ngoại ngữ hoặc tên đọc theo cách riêng, cần người đọc xác định cách phát âm. Dấu nối hoặc khoảng trắng không phải lúc nào cũng biểu diễn đúng tiếng được đọc.

Vần phải được nghe theo phát âm/thi pháp có liên quan: cùng chữ cuối chưa đủ, khác chữ cuối không luôn loại vần thông. Máy chỉ đưa cặp ứng viên để rà. Không đưa một danh sách vần chính tả thành luật chung cho mọi vùng.

## Nguồn và trích dẫn

Tìm bản tác phẩm và niên đại/ấn bản trước khi phân tích. Với ca dao truyền miệng, lưu các dị bản và nơi sưu tầm khi biết; không gắn một bản phổ biến cho tác giả tưởng tượng. Với thơ Hán/Nôm, tách nguyên tác, phiên âm, dịch nghĩa, dịch thơ; không lấy số tiếng bản dịch để khẳng định thể của nguyên tác. Dữ liệu bị hạ chữ thường hoặc bỏ dấu câu không thích hợp làm bản chuẩn về nhịp và trình bày.
