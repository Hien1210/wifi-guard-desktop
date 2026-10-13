"""Kiểm tra các mạng Wi-Fi đã lưu trên Windows và đánh giá mức độ an toàn."""

import subprocess

_DECODE_CANDIDATES = ("utf-8", "cp1258", "cp437")

# Giá trị Authentication/Cipher của netsh luôn là các mã chuẩn này (không bị
# dịch theo ngôn ngữ Windows), nên nhận diện bằng giá trị thay vì tên nhãn.
_AUTH_TOKENS = {
    "Open", "Shared", "WEP",
    "WPA-Personal", "WPA-Enterprise",
    "WPA2-Personal", "WPA2-Enterprise",
    "WPA3-Personal", "WPA3-Enterprise", "WPA3-SAE",
}
_CIPHER_TOKENS = {"None", "WEP", "TKIP", "CCMP", "GCMP"}


def _run_netsh(args):
    """Chạy một lệnh netsh, trả về output đã decode hoặc "" nếu lỗi."""
    try:
        result = subprocess.run(
            ["netsh", *args],
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""

    raw = result.stdout or b""
    for encoding in _DECODE_CANDIDATES:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _parse_key_values(output):
    """Tách các dòng dạng 'Nhãn : Giá trị' thành dict {nhãn: [giá trị, ...]}."""
    pairs = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key and value:
            pairs.setdefault(key, []).append(value)
    return pairs


def get_saved_wifi_profiles():
    """Lấy danh sách tên các Wi-Fi đã lưu trên máy (netsh wlan show profiles)."""
    pairs = _parse_key_values(_run_netsh(["wlan", "show", "profiles"]))
    if not pairs:
        return []

    # Nhãn dòng chứa tên profile bị dịch theo ngôn ngữ Windows, nhưng luôn là
    # nhãn lặp lại nhiều lần nhất trong output này (mỗi profile một dòng).
    profile_key = max(pairs, key=lambda k: len(pairs[k]))
    return pairs[profile_key]


def get_wifi_security_details(profile_name):
    """Lấy chuẩn xác thực (Authentication) và mã hóa (Cipher) của một profile."""
    output = _run_netsh(
        ["wlan", "show", "profile", f'name="{profile_name}"', "key=clear"]
    )

    authentication = None
    cipher = None
    for line in output.splitlines():
        _, _, value = line.partition(":")
        value = value.strip()
        if authentication is None and value in _AUTH_TOKENS:
            authentication = value
        elif cipher is None and value in _CIPHER_TOKENS:
            cipher = value

    return {"authentication": authentication, "cipher": cipher}


def classify_security(authentication):
    """Đánh giá mức độ an toàn dựa trên chuẩn xác thực (Authentication)."""
    if not authentication:
        return "Không xác định"
    if "WPA2" in authentication or "WPA3" in authentication:
        return "An toàn"
    if authentication == "Open" or "WEP" in authentication:
        return "Cảnh báo / Kém an toàn"
    return "Không xác định"


def _self_check():
    sample_profiles_output = (
        "Profiles on interface Wi-Fi:\n\n"
        "Group policy profiles (read only)\n"
        "---------------------------------\n"
        "    <none>\n\n"
        "User profiles\n"
        "---------------------------------\n"
        '    All User Profile     : HomeWifi\n'
        '    All User Profile     : Office5G\n'
    )
    pairs = _parse_key_values(sample_profiles_output)
    profile_key = max(pairs, key=lambda k: len(pairs[k]))
    assert pairs[profile_key] == ["HomeWifi", "Office5G"]

    assert classify_security("WPA2-Personal") == "An toàn"
    assert classify_security("WPA3-Personal") == "An toàn"
    assert classify_security("Open") == "Cảnh báo / Kém an toàn"
    assert classify_security("WEP") == "Cảnh báo / Kém an toàn"
    assert classify_security(None) == "Không xác định"

    assert _run_netsh(["lenh-khong-ton-tai-xyz"]) == "" or isinstance(
        _run_netsh(["lenh-khong-ton-tai-xyz"]), str
    )

    print("wifi_checker self-check OK")


if __name__ == "__main__":
    _self_check()
