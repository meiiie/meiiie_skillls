# Chính tả, dấu câu và dữ liệu trình bày

## Chọn chuẩn trước khi chuẩn hóa

Ưu tiên quy cách được người dùng chỉ định, tên chính thức và quy định thật sự áp dụng cho tài liệu. Quyết định 1989/QĐ-BGDĐT có phạm vi tài liệu giáo dục phổ thông; Nghị định 30/2020/NĐ-CP có phạm vi công tác văn thư/văn bản hành chính liên quan. Không trình bày chúng như một bộ luật cho mọi tiểu thuyết, tin nhắn hoặc bản ghi lời nói. Xem sources.md để biết mức xác minh.

Chính tả từ vựng cần từ điển và ngữ cảnh. Không có quy tắc hỏi/ngã, s/x, ch/tr, d/gi/r, l/n nào cho phép tự sửa an toàn mọi từ. Phát âm vùng miền không quyết định một từ viết sai. Các lựa chọn như i/y, vị trí dấu thanh trong một số tổ hợp và phiên âm tên có thể theo quy cách xuất bản khác nhau; thống nhất chỉ khi có chuẩn được chọn, không đổi tên riêng/nhãn sản phẩm/trích dẫn.

## Unicode và ranh giới được bảo vệ

NFC giúp biểu diễn chuỗi dấu tiếng Việt nhất quán nhưng không phải mọi chuỗi không-NFC đều sai nghĩa. Phát hiện trước; chỉ chuẩn hóa bản sao được phép. Bảo vệ mã, khóa định danh, đường dẫn, URL, chuỗi ký tự kiểm thử, chữ viết ngôn ngữ khác và trích dẫn cần nguyên dạng. Không xóa dấu hoặc chuyển thành ASCII để “sửa mã hóa”.

Ký tự zero-width có thể là lỗi dán văn bản nhưng cũng có vai trò trong ngôn ngữ/kỹ thuật khác. Báo vị trí và mã Unicode; không xóa hàng loạt. Phân biệt dấu cách thường, NBSP dùng giữ số–đơn vị và khoảng trắng định dạng. Không xóa hai dấu cách kết thúc dòng Markdown nếu cần ngắt dòng.

## Dấu câu: chức năng trước hình thức

- **Chấm:** kết thúc câu trần thuật độc lập. Không tách nếu làm đứt điều kiện, lý do hoặc dẫn lời. Dấu chấm còn ở số/viết tắt/tên tệp, không mặc nhiên là ranh giới câu.
- **Phẩy:** phân cách các thành phần liệt kê, vế, phụ chú hoặc trạng ngữ khi giúp xác định cấu trúc. Không đặt theo mỗi lần ngừng thở; không cấm phẩy sau đề ngữ/trạng ngữ một cách tuyệt đối. “Ăn cơm, không được nhịn!” khác “Ăn cơm không được, nhịn!”.
- **Chấm phẩy:** có thể phân tách các vế tương đối độc lập nhưng liên quan, hoặc các mục phức có phẩy. Không tự biến quan hệ cần liên từ thành một dấu chấm phẩy.
- **Hai chấm:** giới thiệu lời dẫn, giải thích hoặc liệt kê có quan hệ với phần trước. Không thêm sau mọi tiêu đề. Giữ nguyên trong URL, tỷ lệ, thời gian và cú pháp lập trình.
- **Chấm hỏi/chấm than:** giữ chức năng hỏi, ngạc nhiên, yêu cầu, cảm xúc. Tin nhắn có dấu lặp có thể là dụng ý; chỉ giảm theo giọng văn được yêu cầu, không làm đổi sức mạnh hoặc thái độ.
- **Ba chấm/dấu lửng:** có thể biểu thị bỏ lửng, ngập ngừng hoặc lược dẫn. Phân biệt lược bỏ trích dẫn với lời tác giả. Không tự bổ sung phần bị lược. Chọn “…” hay “...” theo quy cách, bảo vệ code.
- **Ngoặc tròn/vuông:** phụ chú, ký hiệu, chú giải biên tập hoặc dẫn nguồn. Không chuyển ngoại lệ trong ngoặc thành thông tin tùy chọn. Không xóa citation hay tham số.
- **Ngoặc kép:** lời dẫn trực tiếp, tên/thuật ngữ, cách dùng đặc biệt. Dấu cuối đặt theo việc dấu đó thuộc câu được trích hay câu bao ngoài và quy cách xuất bản; không mang nguyên quy ước tiếng Anh vào mọi câu Việt. Giữ nội dung trích dẫn; nêu riêng lỗi nghi có, không âm thầm “sửa tác giả”.
- **Gạch ngang/gạch nối:** phân biệt lời thoại, phụ chú, khoảng và kết nối trong tên/thuật ngữ. Không thay tất cả dấu “-” bằng “–”, không áp quy tắc một loại dấu cho cả phép trừ, CLI flags, mã và tên dân tộc.

Trong văn xuôi thông thường, không để khoảng trắng trước dấu phẩy/chấm/chấm phẩy/hai chấm/dấu hỏi/dấu than; thường có khoảng trắng sau khi còn từ tiếp theo. Đây là quy cách trình bày cần ngữ cảnh, không bộ máy ngữ pháp: số thập phân, giờ, URL, tên miền, viết tắt, tài liệu song ngữ có ngoại lệ. Công cụ chỉ báo một tập ứng viên nhỏ, không tự sửa.

## Số, đơn vị, ngày và tỷ lệ

- “1.500” và “1,500” có thể là dấu nhóm hàng nghìn hoặc thập phân tùy locale. “12,5%” là cách trình bày quen thuộc trong nhiều tài liệu Việt, không tự chuyển toàn tài liệu sang quy ước khác. Giữ nguyên khi nguồn chưa rõ.
- “03/04/2026” chưa đủ để suy chắc ngày/tháng nếu nguồn có thể dùng chuẩn khác. Ghi rõ quy ước nếu chuyển thành chữ; không đoán địa phương từ ngôn ngữ văn bản.
- Bảo toàn dấu âm, dấu ±, cận, khoảng, số mũ, mã phiên bản và số thứ tự. “Tối đa 5” không bằng “dưới 5”. “10–12” có thể là khoảng, tỷ số hoặc ngày tùy ngữ cảnh.
- Giữ đơn vị và phân biệt đại lượng: kW/kWh, MB/Mb, tấn/tạ, triệu/tỷ. Nếu cần đổi, tính rõ và chỉ đổi trong phạm vi được giao. Dùng tài liệu SI cho ngữ cảnh khoa học, không tự sửa mọi thiết kế bảng hay UI theo một kiểu. Theo BIPM (§5.4.3–5.4.4, §5.4.7; nguồn 13), viết khoảng cách giữa số và đơn vị như “25 °C”; ký hiệu góc phẳng như “30°” là ngoại lệ. SI dùng khoảng cách trước “%”; không vì thế tự sửa cách viết “12,5%” trong mọi tin nhắn hoặc dữ liệu máy.
- Với tiền, giữ tiền tệ, dấu, thuế/phí và mốc giá. Không làm tròn hoặc đổi tỷ giá để câu gọn.
- Với thời gian, giữ múi giờ và ngày; không tự bổ sung “giờ Việt Nam” nếu chưa được xác định. Chuyển ngày tương đối cần biết ngày phát ngôn, không chỉ ngày hiện tại.

## Viết hoa và tên

Đầu câu, tên người, địa danh, cơ quan, chức danh, nhan đề và chữ viết tắt có những quy tắc khác nhau theo thể loại. Kiểm tra tên chính thức của cơ quan/sản phẩm thay vì suy từ kiểu viết hoa. Không viết hoa mọi từ có vẻ quan trọng. Không áp title case tiếng Anh lên mọi tiêu đề Việt.

Giữ cách tự gọi của cá nhân/cộng đồng nếu đã được cung cấp; tên dân tộc có thể có các hệ phiên chuyển và quy ước hành chính khác nhau. Phân biệt tên riêng, tên ngôn ngữ và từ miêu tả. Tra nguồn ở regional-and-community.md trước khi “chuẩn hóa” dấu nháy hoặc gạch nối trong tên.

## Kiểm tra cuối

Đọc lại một lượt không nhìn bản nguồn để phát hiện nhịp/độ rõ; sau đó đọc song song để kiểm nghĩa. Kiểm tra cặp dấu, danh sách và tham chiếu; không suy số lượng từ lời mở đầu nếu thực tế nguồn thiếu mục. Giữ mọi điểm chưa xác định ngoài bản văn, trong phần cần xác nhận.
