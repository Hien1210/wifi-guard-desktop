# WiFi Guard Desktop

Ứng dụng Desktop Windows giúp người dùng phổ thông tự kiểm tra bảo mật Wi-Fi, quét thiết bị trong mạng LAN và theo dõi trạng thái tường lửa — tất cả trong một giao diện đơn giản, dễ hiểu.

Viết bằng **Python** + **[Flet](https://flet.dev)** (dựng UI theo Flutter bằng Python thuần), không cần biết Flutter/Dart.

## Tính năng

- **Wi-Fi Scanner** — liệt kê các Wi-Fi đã lưu trên máy (`netsh wlan show profiles`), kiểm tra chuẩn xác thực/mã hóa (Open, WEP, WPA2, WPA3...) và đánh giá an toàn hay không.
- **LAN Devices** — ping sweep dải mạng hiện tại (`/24`), liệt kê IP đang online kèm hostname và MAC (đọc bảng ARP) nếu lấy được.
- **Firewall** — kiểm tra trạng thái Bật/Tắt của 3 profile Windows Firewall (Domain/Private/Public) và đưa ra đánh giá chung.

Mỗi tab có nút quét riêng, hiệu ứng loading (`ProgressRing`), và tô màu trạng thái (xanh = an toàn, đỏ = cảnh báo).

## Yêu cầu

- Windows 10/11
- Python 3.10+

## Cài đặt & chạy

```bash
pip install -r requirements.txt
python main.py
```

## Cấu trúc dự án

```
wifi-guard-desktop/
├── main.py                       # Giao diện Flet (3 tab)
├── requirements.txt
├── modules/
│   ├── wifi_checker.py           # Quét & đánh giá Wi-Fi đã lưu
│   ├── lan_scanner.py            # Ping sweep + ARP cho thiết bị LAN
│   └── firewall_inspector.py     # Trạng thái Windows Firewall
└── assets/                       # Icon/hình ảnh cho ứng dụng
```

Mỗi module trong `modules/` có thể chạy độc lập để tự kiểm tra logic, không cần giao diện:

```bash
python modules/wifi_checker.py
python modules/lan_scanner.py
python modules/firewall_inspector.py
```

## Đóng gói thành file .exe

Dự án dùng Flet nên đóng gói qua `flet pack` (tự gọi PyInstaller kèm đúng hook để nhúng client desktop của Flet — PyInstaller thuần sẽ không chạy được UI):

```bash
pip install pyinstaller
flet pack main.py -n WiFiGuardDesktop -y
```

File kết quả nằm ở `dist/WiFiGuardDesktop.exe` (single-file, tự ẩn console).

> **Lưu ý Antivirus/Windows Defender:** file `.exe` đóng gói bằng PyInstaller và một app gọi `netsh`/ping/ARP để quét mạng rất dễ bị AV heuristic nhận diện nhầm thành công cụ độc hại (false positive). Nếu phân phối rộng, nên ký code-signing (Authenticode) hoặc nộp file lên [Microsoft Defender false positive submission](https://www.microsoft.com/wdsi/filesubmission) trước khi gửi cho người dùng.

## Giới hạn hiện tại

- Chỉ tối ưu cho Windows (các lệnh dựa vào `netsh`/`ping`/`arp`).
- LAN Scanner giả định subnet `/24`; mạng dùng subnet khác sẽ cần chỉnh lại logic.
- Chưa ký code-signing cho bản `.exe` phân phối.
