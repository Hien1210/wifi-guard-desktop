import asyncio

import flet as ft

from modules.firewall_inspector import evaluate_firewall_security, get_firewall_status
from modules.lan_scanner import scan_lan_devices
from modules.wifi_checker import (
    classify_security,
    get_saved_wifi_profiles,
    get_wifi_security_details,
)

_STATUS_COLORS = {
    "An toàn": ft.Colors.GREEN,
    "Cảnh báo / Kém an toàn": ft.Colors.RED,
    "Cảnh báo": ft.Colors.RED,
}

_FIREWALL_PROFILE_LABELS = {
    "Domain": "Domain Profile",
    "Private": "Private Profile",
    "Public": "Public Profile",
}
_FIREWALL_STATE_LABELS = {"ON": "Bật", "OFF": "Tắt"}
_FIREWALL_STATE_COLORS = {"ON": ft.Colors.GREEN, "OFF": ft.Colors.RED}


def build_wifi_scanner_tab(page: ft.Page) -> ft.Control:
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    scan_button = ft.Button(content="Quét mạng Wi-Fi đã lưu")

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Tên mạng (SSID)")),
            ft.DataColumn(label=ft.Text("Kiểu xác thực")),
            ft.DataColumn(label=ft.Text("Trạng thái")),
        ],
        rows=[],
    )

    async def scan_wifi(e):
        scan_button.disabled = True
        progress_ring.visible = True
        data_table.rows = []
        page.update()

        profiles = await asyncio.to_thread(get_saved_wifi_profiles)
        rows = []
        for profile in profiles:
            details = await asyncio.to_thread(get_wifi_security_details, profile)
            status = classify_security(details["authentication"])
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(profile)),
                        ft.DataCell(ft.Text(details["authentication"] or "Không rõ")),
                        ft.DataCell(
                            ft.Text(
                                status,
                                color=_STATUS_COLORS.get(status, ft.Colors.GREY),
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]
                )
            )

        if not rows:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Không tìm thấy mạng Wi-Fi đã lưu")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )

        data_table.rows = rows
        progress_ring.visible = False
        scan_button.disabled = False
        page.update()

    scan_button.on_click = scan_wifi

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(controls=[scan_button, progress_ring]),
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[data_table]),
        ],
    )


def build_lan_scanner_tab(page: ft.Page) -> ft.Control:
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    scan_button = ft.Button(content="Quét mạng LAN")

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Địa chỉ IP")),
            ft.DataColumn(label=ft.Text("Trạng thái")),
            ft.DataColumn(label=ft.Text("Hostname")),
            ft.DataColumn(label=ft.Text("MAC")),
        ],
        rows=[],
    )

    async def scan_lan(e):
        scan_button.disabled = True
        progress_ring.visible = True
        data_table.rows = []
        page.update()

        devices = await asyncio.to_thread(scan_lan_devices)
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(device["ip"])),
                    ft.DataCell(
                        ft.Text(
                            device["status"],
                            color=ft.Colors.GREEN,
                            weight=ft.FontWeight.BOLD,
                        )
                    ),
                    ft.DataCell(ft.Text(device["hostname"])),
                    ft.DataCell(ft.Text(device["mac"])),
                ]
            )
            for device in devices
        ]

        if not rows:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text("Không tìm thấy thiết bị nào (hoặc chưa có mạng)")
                        ),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )

        data_table.rows = rows
        progress_ring.visible = False
        scan_button.disabled = False
        page.update()

    scan_button.on_click = scan_lan

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(controls=[scan_button, progress_ring]),
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[data_table]),
        ],
    )


def build_firewall_tab(page: ft.Page) -> ft.Control:
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    check_button = ft.Button(content="Kiểm tra Tường lửa")
    summary_text = ft.Text("", weight=ft.FontWeight.BOLD)

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Profile")),
            ft.DataColumn(label=ft.Text("Trạng thái")),
        ],
        rows=[],
    )

    async def check_firewall(e):
        check_button.disabled = True
        progress_ring.visible = True
        data_table.rows = []
        summary_text.value = ""
        page.update()

        statuses = await asyncio.to_thread(get_firewall_status)
        data_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(_FIREWALL_PROFILE_LABELS[profile])),
                    ft.DataCell(
                        ft.Text(
                            _FIREWALL_STATE_LABELS.get(state, "Không xác định"),
                            color=_FIREWALL_STATE_COLORS.get(state, ft.Colors.GREY),
                            weight=ft.FontWeight.BOLD,
                        )
                    ),
                ]
            )
            for profile, state in statuses.items()
        ]

        verdict = evaluate_firewall_security(statuses)
        summary_text.value = f"Đánh giá chung: {verdict}"
        summary_text.color = _STATUS_COLORS.get(verdict, ft.Colors.GREY)

        progress_ring.visible = False
        check_button.disabled = False
        page.update()

    check_button.on_click = check_firewall

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(controls=[check_button, progress_ring]),
            data_table,
            summary_text,
        ],
    )


def main(page: ft.Page):
    page.title = "WiFi Guard Desktop"
    page.window.width = 900
    page.window.height = 650

    page.add(
        ft.Text("WiFi Guard Desktop", size=28, weight=ft.FontWeight.BOLD),
        ft.Tabs(
            length=3,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Wi-Fi Scanner"),
                            ft.Tab(label="LAN Devices"),
                            ft.Tab(label="Firewall"),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            build_wifi_scanner_tab(page),
                            build_lan_scanner_tab(page),
                            build_firewall_tab(page),
                        ],
                    ),
                ],
            ),
        ),
    )


if __name__ == "__main__":
    ft.run(main)
