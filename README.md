# CutCut – Auto Video Builder cho CapCut 🎬

**CutCut** là một công cụ hỗ trợ tự động hóa việc ghép video từ file âm thanh (MP3), phụ đề (SRT) và hình ảnh. Công cụ này sinh ra một dự án (Project) chuẩn định dạng của phần mềm **CapCut Desktop**, giúp bạn tự động dàn trải hình ảnh khớp nối hoàn hảo đến từng mili-giây với đoạn âm thanh và phụ đề tương ứng. 

> ✨ **Phát triển bởi:** Lê Ngọc Châu UTH

---

## 🚀 Tính Năng Chính
- **Tự động đồng bộ:** Tự động sắp xếp và kéo dài hình ảnh dựa trên thời gian bắt đầu và kết thúc của từng câu phụ đề trong file SRT.
- **Tương thích hoàn toàn CapCut Desktop:** Không render ra MP4 làm giảm chất lượng. Tool chỉ đóng vai trò "người vận chuyển" tài nguyên và sắp xếp timeline. Sau khi tạo xong, bạn có thể mở ngay trên CapCut Desktop để tiếp tục tinh chỉnh, thêm hiệu ứng, chữ, hoặc màu sắc tùy ý.
- **Tối ưu hóa dung lượng:** Hỗ trợ tính năng tự dọn rác, không lưu trữ file tạm trên ổ cứng sau khi đã xuất thành dự án CapCut.
- **Giao diện web trực quan:** Giao diện tối màu (Dark Theme) hiện đại, kéo thả file dễ dàng, hiển thị trước (preview) kết quả ánh xạ hình ảnh với phụ đề.

---

## 📥 Hướng Dẫn Sử Dụng

### 1. Chuẩn Bị
Bạn cần chuẩn bị 3 thành phần chính:
1. **File Âm Thanh (Audio):** Một file `.mp3`, `.wav`, hoặc `.m4a` chứa giọng đọc/nhạc của bạn.
2. **File Phụ Đề (SRT):** File `.srt` chứa nội dung và thời gian của từng đoạn.
3. **Thư Mục Ảnh:** Một thư mục chứa các file ảnh (`.jpg`, `.png`, v.v...). Các ảnh này nên được đặt tên theo thứ tự (ví dụ: `[1]-anh.jpg`, `[2]-anh.jpg`,...) để tool nhận diện và sắp xếp cho đúng với thứ tự câu trong SRT.

### 2. Cài Đặt & Chạy Tool
1. Đảm bảo máy tính của bạn đã cài đặt **Python** (phiên bản 3.9 trở lên).
2. Tải toàn bộ mã nguồn của dự án này về máy.
3. Bấm đúp vào file `start.bat`. Hệ thống sẽ tự động khởi chạy máy chủ backend và mở giao diện web trên trình duyệt của bạn (tại địa chỉ `http://localhost:5000`).

### 3. Tạo Video (Project)
1. **Upload:** Kéo thả lần lượt File Âm Thanh, File SRT và Thư mục Ảnh vào các ô tương ứng trên giao diện web.
2. **Preview:** Sau khi upload, màn hình Preview sẽ hiển thị bảng ánh xạ thời gian (mapping) để bạn kiểm tra xem hình ảnh đã khớp với câu chữ hay chưa.
3. **Build:** Đặt tên cho Project của bạn và nhấn **"Tạo Project CapCut"**.
4. **Mở CapCut:** Mở phần mềm CapCut Desktop trên máy tính. Bạn sẽ thấy dự án mới của mình nằm ngay ở phần **Drafts (Bản nháp)**. Mở lên và tùy chỉnh thêm nếu muốn!

---

## ⚠️ Khuyến Cáo & Đóng Góp

Dự án này là sản phẩm cá nhân do sinh viên viết trong quá trình tự học và nghiên cứu, vì thế khó tránh khỏi những sai sót hoặc lỗi chưa lường trước (bugs) trong quá trình vận hành. 

Rất mong nhận được sự thông cảm và mọi ý kiến đóng góp, báo lỗi, hoặc góp ý cải thiện từ cộng đồng để công cụ ngày một hoàn thiện hơn.

**Liên hệ & Ủng hộ tác giả tại:**
- 📧 **Email:** [lengocchau1072006@gmail.com](mailto:lengocchau1072006@gmail.com)
- 🔴 **YouTube:** [NixPaint](https://www.youtube.com/@NixPaint)
- 🐙 **GitHub:** [LeNgocChau9](https://github.com/LeNgocChau9)

> *Nếu bạn thấy tool này hữu ích, đừng ngần ngại cho tác giả 1 Sao (Star) trên GitHub và đăng ký kênh YouTube nhé. Cảm ơn các bạn rất nhiều!* 💖
