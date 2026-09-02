
def _info(description, commands):
    return {
        "description": description,
        "commands": commands,
        "requires_confirmation": False
    }


def _action(description, command):
    return {
        "description": description,
        "command": command,
        "requires_confirmation": True
    }


def diagnose_network_route():
    return _info(
        "Ağ yönlendirme tablosunu ve varsayılan rotayı kontrol eder.",
        [
            "ip route",
            "ip -br addr"
        ]
    )


def diagnose_network_connectivity():
    return _info(
        "Ağ bağlantısının temel durumunu kontrol eder.",
        [
            "ip -br addr",
            "ip route",
            "ping -c 3 127.0.0.1"
        ]
    )


def diagnose_connection_refused():
    return _info(
        "Bağlantının reddedilmesine neden olabilecek servis ve port durumunu inceler.",
        [
            "ss -tuln",
            "systemctl --failed"
        ]
    )


def diagnose_connection_timeout():
    return _info(
        "Bağlantı zaman aşımını ve ağ rotasını inceler.",
        [
            "ip route",
            "ss -tuln",
            "ping -c 3 1.1.1.1"
        ]
    )


def diagnose_connection_reset():
    return _info(
        "Bağlantı sıfırlama hatalarını inceler.",
        [
            "ss -s",
            "journalctl -b --no-pager | grep -Ei 'reset|connection'"
        ]
    )


def diagnose_dns():
    return _info(
        "DNS yapılandırmasını ve isim çözümlemesini kontrol eder.",
        [
            "resolvectl status",
            "resolvectl query example.com"
        ]
    )


def diagnose_dhcp():
    return _info(
        "DHCP durumunu ve IP yapılandırmasını kontrol eder.",
        [
            "ip -br addr",
            "networkctl status --no-pager"
        ]
    )


def renew_dhcp_lease():
    return _action(
        "DHCP kiralamasını yenilemeyi dener.",
        "sudo dhclient -r && sudo dhclient"
    )


def check_dhcp_status():
    return _info(
        "DHCP tarafından alınan IP yapılandırmasını kontrol eder.",
        [
            "ip -br addr",
            "ip route"
        ]
    )


def diagnose_network_interface():
    return _info(
        "Ağ arayüzlerinin link ve bağlantı durumunu kontrol eder.",
        [
            "ip -br link",
            "ip -br addr"
        ]
    )


def diagnose_package_dns():
    return _info(
        "Paket yöneticisinin DNS çözümleme durumunu ve ağ çözümleme yapılandırmasını kontrol eder.",
        [
            "resolvectl status",
            "resolvectl query deb.debian.org",
            "cat /etc/resolv.conf"
        ]
    )


def check_network_interface():
    return _info(
        "Ağ arayüzlerinin mevcut durumunu kontrol eder.",
        [
            "ip -br link",
            "ip link"
        ]
    )


def restart_network_manager():
    return _action(
        "NetworkManager servisini yeniden başlatır.",
        "sudo systemctl restart NetworkManager"
    )


def diagnose_network_manager():
    return _info(
        "NetworkManager servis durumunu ve hata kayıtlarını inceler.",
        [
            "systemctl status NetworkManager --no-pager",
            "journalctl -u NetworkManager -b -p err --no-pager"
        ]
    )


def diagnose_wifi_authentication():
    return _info(
        "Wi-Fi kimlik doğrulama servislerini inceler.",
        [
            "systemctl status wpa_supplicant --no-pager",
            "journalctl -u wpa_supplicant -b -p err --no-pager"
        ]
    )


def diagnose_wifi_connection():
    return _info(
        "Wi-Fi bağlantısı ve kablosuz arayüz durumunu inceler.",
        [
            "iw dev",
            "nmcli device status",
            "journalctl -b --no-pager | grep -Ei 'deauth|association|wifi'"
        ]
    )


def diagnose_network_configuration():
    return _info(
        "Ağ yapılandırmasını ve bağlantı profillerini kontrol eder.",
        [
            "ip -br addr",
            "ip route",
            "nmcli connection show"
        ]
    )


def diagnose_ip_configuration():
    return _info(
        "IP yapılandırmasının durumunu kontrol eder.",
        [
            "ip -br addr",
            "ip route",
            "nmcli device show"
        ]
    )


def diagnose_network_service():
    return _info(
        "Ağ servislerinin durumunu inceler.",
        [
            "systemctl status NetworkManager --no-pager",
            "systemctl status systemd-networkd --no-pager"
        ]
    )
