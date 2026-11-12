# Báo cáo kiểm chứng v1.0.0

Ngày thực hiện: 11-11-2026. Phiên bản skill 1.0.0; phiên bản CLI 1.1.1. Đây là đánh giá gói hiện tại, không phải chứng nhận thông thạo mọi biến thể tiếng Việt.

## Các lớp đã thực hiện

- Validator của skill-creator: `Skill is valid!` (frontmatter/tên/scaffold).
- Bộ `unittest` của CLI: **69/69 đạt**, chạy lại toàn bộ sau sửa cuối; log đầy đủ ở `unit-tests.log`.
- Python compilation: đạt.
- Kiểm tra liên kết Markdown nội bộ: không thấy đích thiếu tại thời điểm đóng gói.
- Rà độc lập code và tài liệu: phát hiện 2 vấn đề mức thấp, đã khắc phục: mô tả JSON không đúng với lỗi argparse; unified diff xử lý sai U+2028. Hồi quy LF/CRLF/không newline đã bổ sung.
- Hồ sơ nguồn: 13 nhóm nguồn tham chiếu học thuật/kỹ thuật/chính sách, cộng nguồn danh mục 54 dân tộc. Mỗi nguồn có phạm vi và mức đã đọc; không tính metadata sách thành đã đọc toàn văn.

## Bằng chứng kiểm thử trước khi triển khai

Các lượt red được giữ ngoài gói sản phẩm trong bộ bằng chứng xây dựng. Kết quả thực tế:

1. Trước script: 41 test, 30 failures và 4 errors vì triển khai chưa có. Đây là red cấu trúc, không bằng chứng chất lượng ngôn ngữ.
2. Kiểm tra schema: tái hiện nhầm boolean/integer, sửa kiểm soát record và chạy lại.
3. Ranh giới tệp: 61 test, 10 failures trước khi thêm bảo vệ cwd/dotpath/symlink; sau đó 61 đạt.
4. Unified diff/NFC: 66 test, 2 failures và 2 errors trước tính năng; sau đó 66 đạt.
5. Unicode line separator: tái hiện sai line count/marker; sau sửa cùng hồi quy CRLF/no-newline, 69 đạt.

Không gọi các lỗi công cụ này là lỗi của mô hình biên tập.

## Phần đánh giá AI

`baseline-output.md` lưu một lượt không dùng skill và vấn đề phạm vi quan sát được. `evaluation-design.md` là **34 trường hợp được thiết kế**, không phải 34 kết quả đã đạt. Kết quả thực chạy với skill được ghi riêng ở `model-evaluation.md`: 12 trường hợp, 12 đầu ra do AI viết, 12 workflow lint/diff/check/verify thực chạy. Tự rà của AI không thấy vi phạm bất biến ở 12/12; verify khớp 12/12. Đây là smoke test một lượt, cùng AI chọn đề và tự chấm, không đánh giá độc lập.

Chưa thực hiện A/B mù với cùng model/settings trên 30+ prompt và nhiều lần lặp; chưa có hai người đọc Việt độc lập chấm mù. Không có bằng chứng thống kê rằng skill tăng chất lượng nói chung. Baseline đã giữ tốt nhiều bất biến, nên không dùng một ví dụ làm tuyên bố vượt trội.

## Giới hạn còn lại

- Grammar/dialect references là bộ hướng dẫn biên tập có nguồn và phản ví dụ, không từ điển hay parser hoàn chỉnh.
- Danh mục 54 dân tộc là sổ phạm vi, không 54 bộ ngữ pháp; tên dân tộc không đồng nhất tên ngôn ngữ.
- Heuristic diff không phát hiện hết đổi chủ thể/phạm vi; unified diff giúp reviewer nhìn thay đổi nhưng không hiểu nghĩa.
- Record không chữ ký/xác thực; danh tính và nhận xét reviewer tự khai. Hash khớp không chứng minh người đã đọc hoặc người dùng đã phê duyệt.
- Safe-path guard không thay sandbox; không bảo vệ toàn diện khỏi tiến trình cùng máy thay symlink đồng thời.
- Chưa kiểm thử tích hợp mọi host, automatic selection hoặc hooks. Không tự cài vào tài khoản người dùng.

Các hạn chế này là ranh giới phát hành, không được bỏ khi trình bày kết quả.

## Phạm vi bảo vệ Markdown

Bộ nhận diện code fence/backtick/URL của CLI không thay một parser Markdown/CommonMark hoàn chỉnh. YAML front matter, HTML, đích liên kết tương đối, bảng và một số code block lồng sâu chưa có parser riêng. Hướng dẫn AI vẫn yêu cầu giữ chúng nguyên dạng và reviewer phải xem unified diff. Không tuyên bố toàn bộ 34 fixtures thiết kế về Markdown đã được công cụ bao phủ.
