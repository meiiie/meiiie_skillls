# Kiến trúc, nguồn gốc và phạm vi tương thích

## Đối chiếu Yomiyasu v3.0.0

Tham chiếu đã đọc: [SKILL.md tại tag v3.0.0](https://github.com/nanaism/yomiyasu/blob/v3.0.0/skills/yomiyasu/SKILL.md), blob `a1cc491efb3e9185b5609be92003a7f87a63cf8a`; [README tiếng Anh](https://github.com/nanaism/yomiyasu/blob/v3.0.0/README.en.md); [MIT LICENSE](https://github.com/nanaism/yomiyasu/blob/v3.0.0/LICENSE), blob `f0d06f87f9b209d47c7f7963321ff71bab68c1e8`. Tác giả nguồn: nanaism, copyright 2026. Bản MIT của nguồn được giữ trong LICENSE. Hướng dẫn tiếng Việt là bản thích nghi về kiến trúc và nguyên tắc; mã Python được viết mới, không sao chép bảng Unicode hoặc thuật toán từ nguồn.

| Lớp gốc | Thực hiện ở Việt ngữ toàn thư |
|---|---|
| Bảo toàn ý nghĩa, sắc thái, điều kiện trước độ trôi chảy | Sáu bất biến; phân biệt biên tập với sửa lập luận và fact-check |
| SKILL.md trung tâm, tham chiếu theo thể loại/người đọc | Entrypoint ngắn, tài liệu ngữ pháp, trình bày, nhân quả, thể loại, cộng đồng |
| Lint gợi ý, không tự chứng minh cần sửa | Lint Unicode/khoảng trắng/dấu câu có vùng bảo vệ; không auto-fix |
| Đọc nguồn và bản sửa; diff cảnh báo rủi ro | Danh sách thay đổi số, phủ định, tình thái, nhân quả, quy nguồn, vùng được bảo vệ; người/AI đọc lại toàn văn |
| Check record và verify tệp cuối | SHA-256 nguyên byte của hai tệp, kết quả kiểm tra, ghi nhận reviewer; verify tính lại |
| Giữ nguyên văn nếu sửa có nguy cơ đổi nghĩa | Đưa vấn đề ngoài phạm vi vào nhận xét, không sửa đi sửa lại để đạt “điểm” |
| Thể loại và thông tin thực tế quyết định ngoại lệ | Giữ giọng vùng miền, ẩn dụ và xưng hô; giới hạn chuẩn hành chính/giáo dục |
| Thực thi giới hạn tệp trong thư mục công việc | CLI giới hạn trong cwd, không dùng đường dẫn ẩn hoặc thoát qua symlink; đây không thay sandbox của host |

## Những khác biệt có chủ ý

Đây **không phải port tương thích CLI, plugin/hook hoặc toàn bộ tính năng** của Yomiyasu. Tiếng Việt cần hệ quy tắc riêng; không mang các quy tắc chữ Hán/kana, dấu phẩy tiếng Nhật hoặc kính ngữ tiếng Nhật sang. Không có bộ từ điển “cấm từ AI”, tự phân loại mọi văn bản hay bộ phân tích cú pháp hoàn chỉnh.

Yomiyasu có cơ chế gọi tên tường minh; bản này hỗ trợ chọn tự động khi yêu cầu liên quan đúng phạm vi, theo mặc định host. Không tự bật trong mọi tác vụ lập trình. Không có cơ chế scan tự động các tệp của người dùng khi thiếu đầu vào.

CLI dùng bốn subcommand của `viet_guard.py`, không các script/tùy chọn cùng tên với nguồn. Phiên bản 2 có mode compose và danh sách thuật ngữ JSON tường minh; viet_guard chưa triển khai stdin/no-record, regex người dùng, bộ kiểm tra mọi thể loại hoặc hook cưỡng chế của một sản phẩm cụ thể. Không cấu hình hook hay sửa cài đặt host khi cài thư mục skill. Có thể chạy CLI bằng tay hoặc qua một integration do người dùng chủ động thiết lập; không giả bộ host sẽ cưỡng chế quy trình.

Một record hợp lệ chứng minh tính nhất quán của nội dung record và tệp đã kiểm tra, không phải chữ ký số, không xác thực danh tính reviewer, không chứng minh người dùng đã phê duyệt. Người có quyền sửa record có thể viết lại và tính lại checksum. Luôn giữ rõ reviewer là AI hay người.

## Đánh giá và bảo trì

Mượn cách chia lớp và đối chiếu trước/sau, không mượn kết luận hiệu năng. Bằng chứng của Yomiyasu là benchmark nhỏ, không tự chuyển thành bằng chứng tiếng Việt. Kết quả riêng trong evals và tests chỉ áp dụng bộ trường hợp đã chạy. Cần đánh giá độc lập rộng hơn với người dùng tiếng Việt, nhiều thể loại và cộng đồng trước khi tuyên bố cải thiện tổng quát.

Mỗi thay đổi quy tắc cần: ví dụ lỗi thực tế, phản ví dụ hợp lệ, phạm vi nguồn, bài kiểm thử hồi quy phù hợp, rà khả năng làm đổi nghĩa. Không thêm cấm đoán từ một ví dụ. Mỗi nguồn mới phải ghi rõ văn bản đã đọc hay chỉ metadata/tóm tắt. Không biến danh sách dân tộc hoặc từ địa phương thành bằng chứng đã bao quát toàn bộ ngôn ngữ của họ.

## Phiên bản 2: mức tương ứng thực tế

Đã bổ sung hướng dẫn stance/loại phát ngôn, phục hồi dữ kiện có truy vết, phép thử phương án có hoàn nguyên, giới hạn vòng sửa, hồ sơ 13 thể loại và kỹ thuật biên tập sâu. Đây là thích nghi có chọn lọc, không bản dịch tương đương đầy đủ của Yomiyasu. Các detector tiếng Nhật, dữ liệu Unicode đóng gói, benchmark nguồn, hook và mọi chi tiết Markdown của nguồn không được chuyển sang. Python sử dụng unicodedata chuẩn thay vì sao chép bảng Unicode upstream. Không tuyên bố tương đương toàn bộ cơ chế hay chất lượng.

## Công cụ thơ và phiên bản 3

`luc_bat.py` có đầu vào UTF-8 stdin hoặc tệp thường trong cwd; không ghi record và không gửi mạng. Cùng kiểm đường dẫn với `viet_guard.py`, từ chối đường dẫn ẩn, thoát workspace, symlink thoát và tệp đặc biệt. Đây không thay sandbox và vẫn giả định không có thay symlink đồng thời. Không ép chạy kiểm tệp với tin nhắn/tác phẩm ngắn; xem SKILL.md cho điều kiện chọn kiểm toán.
