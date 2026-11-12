# Dùng gói kỹ năng

Gói không có dịch vụ mạng, không chứa mô hình và không tự đổi cài đặt host. Chưa tự cài vào tài khoản hoặc thư mục skill hệ thống của người dùng. Cần một AI host có thể đọc SKILL.md; Python 3.9+ chỉ cần cho công cụ kiểm tra.

## Codex hoặc host nhận thư mục skill

Giải nén để có một thư mục `viet-ngu-toan-thu` chứa trực tiếp `SKILL.md`, `references`, `scripts`, `agents`, `tests`, `evals`. Đặt thư mục này vào nơi host đã cấu hình tìm kỹ năng, chẳng hạn thư mục skills của Codex hoặc `.agents/skills/` của dự án nếu host hỗ trợ. Giữ nguyên cấu trúc thư mục. Việc đổi nơi cài không làm script được quyền truy cập mọi tệp.

Gọi `$viet-ngu-toan-thu` hoặc yêu cầu biên tập tiếng Việt trong host có chức năng nhận kỹ năng. Nếu host chỉ hỗ trợ tệp đính kèm, tải SKILL.md và các tham chiếu phù hợp; không giả định host sẽ tự chạy Python. Khả năng nhập ZIP, phát hiện tự động và lệnh gọi phụ thuộc host, chưa kiểm thử mọi host.

Ví dụ yêu cầu: “Dùng Việt ngữ toàn thư sửa lỗi rõ ràng trong đoạn này, giữ giọng Nam Bộ và không sửa nội dung. Trả bản sửa cùng các thay đổi đáng kể.”

## Kiểm thử tại chỗ

Trong thư mục đã giải nén:

```sh
python3 -m unittest discover -s tests -v
```

Các lệnh lint/diff/check/verify và mã thoát ở `references/checking.md`. Chạy từ thư mục công việc chứa bản sao tài liệu được phép đọc; chỉ đường dẫn script trỏ tới nơi cài. Không bật hook tự động: v3 chưa kèm hook tích hợp host.

## Giới hạn được công bố

Bộ hướng dẫn rộng nhưng không toàn tri. Không có từ điển toàn bộ tiếng Việt, bộ phân tích ngữ pháp hoàn chỉnh, nhận diện tất cả phương ngữ, hay ngữ pháp đầy đủ cho các ngôn ngữ của mọi dân tộc. Nguồn đã đọc, chỉ xem tóm tắt và còn thiếu được tách trong `references/sources.md`. Mã kiểm tra không chứng minh bản văn giữ nghĩa. Xem đánh giá thực chạy trong `evals/`, không coi bài thử thiết kế là bài thử đã đạt.

## Phần mới của v3

Tài liệu riêng cho văn chương, thi pháp, nhắn tin và chọn nguồn. Công cụ `scripts/luc_bat.py` phân tích số tiếng ứng viên, thanh chính tả và nêu cặp cần nghe vần, không tự chứng nhận vần. Không cần mạng; không có dữ liệu văn thơ bên thứ ba được gói kèm. Gói này chưa được cài hoặc đẩy lên kho nào.
