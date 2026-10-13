# CLAUDE.md - Hướng dẫn & Ngữ cảnh Dự án wifi-guard-desktop

## 1. Tổng quan Dự án

`wifi-guard-desktop` là ứng dụng Desktop bằng **Python** kết hợp giao diện **Flet**, hỗ trợ người dùng kiểm tra bảo mật Wi-Fi, quét thiết bị trong mạng nội bộ (LAN) và giám sát trạng thái tường lửa hệ thống (tập trung tối ưu trên Windows trước).

## 2. Công nghệ & Thư viện Sử dụng (Tech Stack)

- **Ngôn ngữ chính:** Python 3.10+
- **Giao diện (UI Framework):** Flet (Dựng UI Flutter bằng Python thuần)
- **Mạng & Bảo mật (Networking Libraries):**
  - `subprocess`: Gọi lệnh hệ thống native (như `netsh`, `ipconfig`, `arp`)
  - `scapy` / `socket`: Quét thiết bị hoạt động và kiểm tra cổng (port) trong mạng LAN
  - `ipaddress`: Xử lý dải IP và subnet
- **Đóng gói (Packaging):** PyInstaller (Xuất file `.exe` cho end-user)

## 3. Các Module & Tính năng Cốt lõi

1. **Quét & Đánh giá Mạng Wi-Fi (Wi-Fi Scanner):**
   - Liệt kê các Wi-Fi đã lưu trên máy.
   - Kiểm tra chuẩn mã hóa (Cảnh báo nếu dùng mạng Mở/Open, WEP, WPA cũ; Đánh giá an toàn với WPA2/WPA3).
2. **Quét Thiết bị Mạng LAN (LAN Device Discovery):**
   - Quét và phát hiện danh sách các IP/thiết bị đang kết nối chung mạng Wi-Fi.
   - Hiển thị địa chỉ IP, MAC và trạng thái cổng kết nối cơ bản.
3. **Giám sát Tường lửa (Firewall Inspector):**
   - Kiểm tra trạng thái Bật/Tắt của Windows Firewall (Private/Public Network).
   - Cảnh báo nếu tường lửa bị tắt hoặc có nguy cơ mất an toàn.
4. **Giao diện Dashboard Hiện đại:**
   - Giao diện Flet dạng Tab trực quan, hiển thị trạng thái màu sắc rõ ràng (Xanh = An toàn, Đỏ/Vàng = Cảnh báo).

## 4. Quy chuẩn Viết Code & Nguyên tắc Phát triển (Development Rules)

- **Xử lý Quyền Quản trị (Admin Privilege):** Các tính năng can thiệp hệ thống cần kiểm tra và bắt lỗi gracefully nếu người dùng chưa bật quyền "Run as Administrator".
- **Bắt lỗi Hệ thống (Error Handling):** Tất cả các lệnh gọi `subprocess` hoặc thao tác mạng phải được bọc trong khối `try-except` cẩn thận để tránh văng ứng dụng (crash).
- **Cấu trúc Code Tách biệt (Modular Architecture):** Code logic được chia rõ ràng vào thư mục `modules/` (ví dụ: `modules/wifi.py`, `modules/scanner.py`, `modules/firewall.py`), không viết dồn hết vào file `main.py`.
- **Trải nghiệm Người dùng (UX):** Dùng thuật ngữ dễ hiểu, thân thiện với người dùng phổ thông.
