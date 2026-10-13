"""Kiểm tra trạng thái Windows Firewall (netsh advfirewall)."""

import subprocess

# netsh luôn in theo đúng thứ tự này bất kể ngôn ngữ Windows, nên dùng thứ tự
# xuất hiện của "ON"/"OFF" (không bị dịch) để ánh xạ, thay vì dò tên nhãn.
_PROFILE_ORDER = ["Domain", "Private", "Public"]


def _run_netsh(args):
    """Chạy một lệnh netsh, trả về output đã decode hoặc "" nếu lỗi."""
    try:
        result = subprocess.run(["netsh", *args], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.decode("utf-8", errors="replace")


def _extract_states(output):
    """Lấy danh sách ON/OFF theo thứ tự xuất hiện (giá trị cuối mỗi dòng)."""
    states = []
    for line in output.splitlines():
        tokens = line.split()
        if tokens and tokens[-1].upper() in ("ON", "OFF"):
            states.append(tokens[-1].upper())
    return states


def get_firewall_status():
    """Lấy trạng thái Bật/Tắt của 3 profile tường lửa (Domain/Private/Public).

    Trả về dict {"Domain": "ON"|"OFF"|None, "Private": ..., "Public": ...}.
    Giá trị `None` nghĩa là không đọc được trạng thái (ví dụ chưa có quyền,
    hoặc lệnh netsh lỗi).
    """
    output = _run_netsh(["advfirewall", "show", "allprofiles", "state"])
    states = _extract_states(output)

    return {
        profile: (states[i] if i < len(states) else None)
        for i, profile in enumerate(_PROFILE_ORDER)
    }


def evaluate_firewall_security(statuses):
    """Đánh giá an toàn: "An toàn" nếu mọi profile đều ON, ngược lại "Cảnh báo".

    Trả về "Không xác định" nếu có profile không đọc được trạng thái.
    """
    values = statuses.values()
    if any(status is None for status in values):
        return "Không xác định"
    if all(status == "ON" for status in values):
        return "An toàn"
    return "Cảnh báo"


def _self_check():
    sample_output = (
        "Domain Profile Settings: \n"
        "----------------------------------------------------------------------\n"
        "State                                 ON\n\n"
        "Private Profile Settings: \n"
        "----------------------------------------------------------------------\n"
        "State                                 OFF\n\n"
        "Public Profile Settings: \n"
        "----------------------------------------------------------------------\n"
        "State                                 ON\n"
        "Ok.\n"
    )
    statuses = dict(zip(_PROFILE_ORDER, _extract_states(sample_output)))
    assert statuses == {"Domain": "ON", "Private": "OFF", "Public": "ON"}
    assert evaluate_firewall_security(statuses) == "Cảnh báo"
    assert evaluate_firewall_security(
        {"Domain": "ON", "Private": "ON", "Public": "ON"}
    ) == "An toàn"
    assert evaluate_firewall_security({"Domain": None}) == "Không xác định"

    print("firewall_inspector self-check OK")


if __name__ == "__main__":
    _self_check()
