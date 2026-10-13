"""Quét các thiết bị đang hoạt động trong mạng LAN (ping sweep + bảng ARP)."""

import concurrent.futures
import ipaddress
import re
import socket
import subprocess

_PING_TIMEOUT_MS = 500
_MAX_WORKERS = 32
_MAC_RE = re.compile(r"\s*(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F-]{17})")


def get_local_subnet():
    """Lấy IP cục bộ và dải mạng /24 tương ứng (ví dụ 192.168.1.0/24).

    Trả về (None, None) nếu máy không có kết nối mạng nào.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except OSError:
        return None, None

    return local_ip, ipaddress.ip_network(f"{local_ip}/24", strict=False)


def _ping(ip):
    """Ping một địa chỉ IP, trả về True nếu có hồi đáp."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(_PING_TIMEOUT_MS), str(ip)],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _get_hostname(ip):
    """Lấy hostname của một IP, trả về None nếu không xác định được."""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except (socket.herror, socket.gaierror, OSError):
        return None


def _parse_arp_output(output):
    """Tách bảng ARP (output của `arp -a`) thành dict {ip: mac}."""
    arp_table = {}
    for line in output.splitlines():
        match = _MAC_RE.match(line)
        if match:
            arp_table[match.group(1)] = match.group(2).upper()
    return arp_table


def _get_arp_table():
    """Đọc bảng ARP hệ thống, trả về dict {ip: mac} ("" nếu lệnh lỗi)."""
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return {}
    return _parse_arp_output(result.stdout.decode("utf-8", errors="replace"))


def scan_lan_devices():
    """Quét các thiết bị đang hoạt động trong cùng mạng LAN.

    Trả về list[dict] với các khóa ip/status/hostname/mac. Hostname/MAC
    là "Không rõ" khi không lấy được (ví dụ do thiết bị chặn DNS ngược
    hoặc đã rời khỏi bảng ARP).
    """
    _, network = get_local_subnet()
    if network is None:
        return []

    hosts = [str(ip) for ip in network.hosts()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        online_flags = list(executor.map(_ping, hosts))

    online_ips = [ip for ip, online in zip(hosts, online_flags) if online]
    arp_table = _get_arp_table()

    return [
        {
            "ip": ip,
            "status": "Online",
            "hostname": _get_hostname(ip) or "Không rõ",
            "mac": arp_table.get(ip, "Không rõ"),
        }
        for ip in online_ips
    ]


def _self_check():
    sample_arp_output = (
        "Interface: 192.168.1.5 --- 0x4\n"
        "  Internet Address      Physical Address      Type\n"
        "  192.168.1.1           aa-bb-cc-dd-ee-ff      dynamic\n"
        "  192.168.1.255         ff-ff-ff-ff-ff-ff      static\n"
    )
    assert _parse_arp_output(sample_arp_output) == {
        "192.168.1.1": "AA-BB-CC-DD-EE-FF",
        "192.168.1.255": "FF-FF-FF-FF-FF-FF",
    }

    assert isinstance(_ping("127.0.0.1"), bool)

    local_ip, network = get_local_subnet()
    assert local_ip is None or isinstance(network, ipaddress.IPv4Network)

    print("lan_scanner self-check OK")


if __name__ == "__main__":
    _self_check()
