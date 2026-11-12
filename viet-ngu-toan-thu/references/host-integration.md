# Tích hợp host và Neko an toàn

Skill là hướng dẫn và công cụ kiểm, không tự cấp quyền cho lệnh, không tự cài hook. Hãy dùng đường dẫn tuyệt đối của thư mục chứa SKILL.md do host cung cấp. Một tool tải thành công skill không chứng minh đã chạy kiểm tra.

## Quyền tối thiểu

- Chỉ đọc bản gốc/tư liệu được chọn, file skill đã biết, bản cuối và cấu hình rõ ràng. Chỉ ghi bản cuối và record trong workspace đánh giá.
- Dùng read_file/write_file nếu host có; lệnh Python gọi trực tiếp checker với argv rõ. Không cần ls -R, shell pipe, curl, git, cài gói hoặc thay cài đặt.
- Host có thể cho phép riêng executable Python, đường dẫn checker và subcommand lint/diff/check/verify; kiểm mọi đường dẫn đầu vào và đầu ra dưới workspace. Allowlist phải kiểm đối số, không chỉ xem chuỗi có chữ python hay tên checker. Không cho phép shell metacharacter, script bất kỳ, mở rộng biến hay tự do chạy -c. Nếu host dùng shell, quote an toàn từng đối số và xác nhận không diễn giải thêm.
- Khi một lệnh khám phá như ls bị chặn: ghi đúng lệnh và phạm vi từ chối. Chỉ dùng checker trực tiếp nếu việc đó đã được phép độc lập và không thực hiện hành vi vừa bị cấm. Nếu chính checker bị chặn thì dừng bước đó; không chuyển sang import, exec, wrapper hoặc interpreter khác để né từ chối. Chỉ đổi python3 sang python/py khi thật sự command-not-found và host cho phép, không khi access denied.
- Không có Python: rà thủ công. Không được lưu tệp: rà nghĩa thủ công; viet_guard chưa có stdin/no-record tương đương Yomiyasu. Riêng luc_bat có thể nhận stdin để phân tích hình thức nếu host cho phép. Không tạo tệp bí mật để làm đủ số bước. Trạng thái phải phân biệt no_python, not_allowed, check_error và not_requested.

## Đánh giá thực bằng Neko

Dùng Agent, ToolRegistry, skill loader và provider thực; ghi rõ embedded hay CLI/TUI. Không sửa sản phẩm hay quyền runtime live chỉ để chạy benchmark. Cố định model yêu cầu, cấu hình, giới hạn bước, prompt, system prompt chung, schema tool và tài nguyên; không ghi khóa/token vào artifact. Dùng workspace, history và đối tượng Agent độc lập mỗi arm. Ngoài skill và chỉ dẫn kích hoạt cần thiết, giữ điều kiện ngang nhau.

Trước khi đánh giá ngôn ngữ, smoke test allowlist với lệnh checker hợp lệ và lệnh bị cấm; phải chứng minh checker thực sự chạy được và không có denial bị lách. Một lỗi gate làm mất bước kiểm là kết quả integration chưa đạt, không được diễn giải là tác dụng của kỹ thuật ngôn ngữ.

Phân biệt ba lớp: kiểm đơn vị xác định; integration có đủ tool trace và record; chất lượng văn bản từ người chấm/đánh giá độc lập. Chạy câu hỏi holdout chưa dùng để viết quy tắc, cả baseline không skill và treatment có skill. Đảo thứ tự arm giữa các mẫu; lưu phản hồi thô, chỉ số token/cache, thời gian và hash đầu vào/skill. Không tính tự chấm vào bằng chứng độc lập. Chấm mù theo nghĩa, tự nhiên, đúng đề, giọng vùng, định dạng và độ dài; lưu lý do từng đánh giá, không chỉ tổng điểm. Mẫu ít chỉ là smoke test, không phải bằng chứng cải thiện tổng quát.

Bài sunrise cũ là development regression: từng bị chặn ls rồi bỏ mọi kiểm tra, nên không được tái gắn nhãn holdout. Không gộp 12 bài sinh bằng API trước đây thành kiểm tra Neko thực. Chỉ công bố bước đã thấy trong tool trace và record verify thành công.

## Công cụ thơ và phiên bản 3

`luc_bat.py` có đầu vào UTF-8 stdin hoặc tệp thường trong cwd; không ghi record và không gửi mạng. Cùng kiểm đường dẫn với `viet_guard.py`, từ chối đường dẫn ẩn, thoát workspace, symlink thoát và tệp đặc biệt. Đây không thay sandbox và vẫn giả định không có thay symlink đồng thời. Không ép chạy kiểm tệp với tin nhắn/tác phẩm ngắn; xem SKILL.md cho điều kiện chọn kiểm toán.
