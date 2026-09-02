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


def update_package_lists():
    return _action(
        "Paket listelerini günceller.",
        "sudo apt update"
    )


def diagnose_package_lock():
    return _info(
        "APT ve dpkg kilit durumunu kontrol eder.",
        [
            "ps aux | grep -E 'apt|dpkg'",
            "ls -l /var/lib/dpkg/lock* /var/cache/apt/archives/lock 2>/dev/null"
        ]
    )


def configure_dpkg():
    return _action(
        "Yarım kalmış dpkg yapılandırmalarını tamamlar.",
        "sudo dpkg --configure -a"
    )


def diagnose_dpkg():
    return _info(
        "dpkg hata durumunu ve yarım kalmış paketleri inceler.",
        [
            "dpkg --audit",
            "dpkg --configure -a --no-act"
        ]
    )


def fix_broken_dependencies():
    return _action(
        "Bozuk paket bağımlılıklarını düzeltmeyi dener.",
        "sudo apt --fix-broken install"
    )


def check_package_repositories():
    return _info(
        "APT depo yapılandırmasını kontrol eder.",
        [
            "grep -Rhv '^#' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null",
            "apt-cache policy"
        ]
    )


def diagnose_package_download():
    return _info(
        "Paket indirme hatalarını ve ağ bağlantısını inceler.",
        [
            "apt-get update",
            "resolvectl status"
        ]
    )


def diagnose_package_dns():
    return _info(
        "Paket yöneticisinin DNS çözümleme durumunu ve resolv yapılandırmasını kontrol eder.",
        [
            "resolvectl status",
            "resolvectl query deb.debian.org",
            "cat /etc/resolv.conf"
        ]
    )


def refresh_package_lists():
    return _action(
        "APT paket listelerini temizleyip yeniden oluşturur.",
        "sudo rm -rf /var/lib/apt/lists/* && sudo apt update"
    )


def check_repository_signature():
    return _info(
        "APT depo imza doğrulama durumunu inceler.",
        [
            "apt-get update",
            "apt-key list 2>/dev/null || true"
        ]
    )


def repair_repository_key():
    return _info(
        "Eksik depo GPG anahtarının belirlenmesine yardımcı olur.",
        [
            "apt-get update",
            "apt-key list 2>/dev/null || true"
        ]
    )


def diagnose_repository_gpg():
    return _info(
        "APT GPG ve depo imza hatalarını inceler.",
        [
            "apt-get update",
            "apt-cache policy"
        ]
    )


def refresh_repository_metadata():
    return _action(
        "APT depo metadata bilgisini yeniler.",
        "sudo apt update"
    )


def repair_repository_sources():
    return _info(
        "APT depo kaynaklarının yapılandırmasını kontrol eder.",
        [
            "grep -Rhv '^#' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null",
            "apt-get update"
        ]
    )


def check_package_status():
    return _info(
        "Paketin mevcut kurulum ve güncelleme durumunu kontrol eder.",
        [
            "apt list --upgradable 2>/dev/null",
            "dpkg --audit"
        ]
    )


def check_package_removal():
    return _info(
        "Paket kaldırma işlemlerinin durumunu kontrol eder.",
        [
            "dpkg --audit",
            "apt list --installed 2>/dev/null"
        ]
    )


def diagnose_apt():
    return _info(
        "APT iç hatalarını ve paket yöneticisi durumunu inceler.",
        [
            "apt-get check",
            "dpkg --audit"
        ]
    )


def reinstall_package():
    return _action(
        "Eksik veya bozuk paket dosyalarının yeniden kurulmasını sağlar.",
        "sudo sh -c 'PKG=\"${PACKAGE}\"; if apt-cache policy \"$PKG\" >/dev/null 2>&1; then apt-get install -y --reinstall \"$PKG\"; else echo \"Paket bulunamadı: $PKG\"; exit 1; fi'"
    )


def install_required_package():
    return _action(
        "Gerekli paketin kurulmasını sağlar.",
        "sudo sh -c 'PKG=\"${PACKAGE}\"; if apt-cache policy \"$PKG\" >/dev/null 2>&1; then apt-get install -y \"$PKG\"; else echo \"Paket bulunamadı: $PKG\"; exit 1; fi'"
    )


def check_package_configuration():
    return _info(
        "Paket yapılandırma durumunu kontrol eder.",
        [
            "dpkg --audit",
            "dpkg -l"
        ]
    )