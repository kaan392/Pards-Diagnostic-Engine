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


def install_kernel_headers():
    return _action(
        "Çalışan kernel için gerekli header paketlerini kurar ve ardından sistemin yeni kernel ile başlaması için yeniden başlatmayı önerir.",
        "sudo apt-get update && (apt-cache policy linux-headers-$(uname -r) >/dev/null 2>&1 && sudo apt-get install -y linux-headers-$(uname -r) || sudo apt-get install -y linux-headers-amd64 linux-image-amd64) && echo 'Yeni kernel kurulumu tamamlandı. Sistem yeniden başlatılmalı.'"
    )


def reboot_and_reconfigure_virtualbox():
    return _info(
        "Yeni kernel aktif hale gelmeden VirtualBox Guest Additions düzgün çalışmaz. Önce sistem yeniden başlatılır, sonra VirtualBox Guest Additions tekrar kurulmalıdır.",
        [
            "sudo reboot",
            "sudo /sbin/rcvboxadd setup"
        ]
    )


def diagnose_kernel_module():
    return _info(
        "Kernel modüllerini ve hata kayıtlarını inceler.",
        [
            "lsmod",
            "dmesg | grep -i module"
        ]
    )


def install_kernel_module():
    return _action(
        "Eksik kernel modülünün belirlenmesi gerekiyor.",
        "modinfo \"${MODULE}\""
    )


def diagnose_kernel_panic():
    return _info(
        "Kernel panic kayıtlarını inceler.",
        [
            "journalctl -k -b -1 -p err --no-pager",
            "dmesg -T | grep -i 'kernel panic'"
        ]
    )


def diagnose_kernel_oops():
    return _info(
        "Kernel Oops kayıtlarını inceler.",
        [
            "dmesg -T | grep -i oops",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_kernel_fault():
    return _info(
        "Kernel fault kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'general protection fault|segmentation fault'",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_kernel_taint():
    return _info(
        "Kernel taint durumunu kontrol eder.",
        [
            "cat /proc/sys/kernel/tainted",
            "dmesg -T | grep -i taint"
        ]
    )


def install_missing_firmware():
    return _info(
        "Eksik firmware kayıtlarını belirler.",
        [
            "dmesg -T | grep -i firmware",
            "apt list --upgradable 2>/dev/null"
        ]
    )


def check_firmware_configuration():
    return _info(
        "Firmware yapılandırmasını kontrol eder.",
        [
            "dmesg -T | grep -i firmware",
            "ls /lib/firmware"
        ]
    )


def diagnose_firmware():
    return _info(
        "Firmware hatalarını inceler.",
        [
            "dmesg -T | grep -Ei 'firmware|failed to execute'",
            "journalctl -k -p err --no-pager"
        ]
    )


def check_kernel_module_version():
    return _info(
        "Kernel modülünün sürüm uyumluluğunu kontrol eder.",
        [
            "uname -r",
            "modinfo \"${MODULE}\""
        ]
    )


def check_module_signature():
    return _info(
        "Kernel modülünün imza durumunu kontrol eder.",
        [
            "modinfo \"${MODULE}\" | grep -Ei 'signer|sig_key|sig_id'",
            "dmesg -T | grep -i signature"
        ]
    )


def check_kernel_module_dependencies():
    return _info(
        "Kernel modül bağımlılıklarını kontrol eder.",
        [
            "modinfo \"${MODULE}\"",
            "modprobe --show-depends \"${MODULE}\""
        ]
    )


def rebuild_kernel_module():
    return _action(
        "Kernel modül bağımlılıklarını yeniden oluşturur.",
        "sudo depmod -a"
    )


def check_loaded_modules():
    return _info(
        "Yüklü kernel modüllerini kontrol eder.",
        [
            "lsmod",
            "cat /proc/modules"
        ]
    )


def check_module_blacklist():
    return _info(
        "Kernel modül blacklist yapılandırmasını kontrol eder.",
        [
            "grep -R 'blacklist' /etc/modprobe.d/",
            "grep -R 'install.* /bin/false' /etc/modprobe.d/"
        ]
    )


def diagnose_filesystem():
    return _info(
        "Dosya sistemi hatalarını inceler.",
        [
            "findmnt",
            "dmesg -T | grep -Ei 'read-only filesystem|I/O error'"
        ]
    )


def diagnose_io_error():
    return _info(
        "Kernel I/O hatalarını inceler.",
        [
            "dmesg -T | grep -Ei 'I/O error|buffer I/O error'",
            "lsblk"
        ]
    )


def diagnose_storage_device():
    return _info(
        "Depolama cihazındaki kernel hatalarını inceler.",
        [
            "lsblk",
            "dmesg -T | grep -Ei 'buffer I/O error|I/O error'"
        ]
    )


def diagnose_kernel_watchdog():
    return _info(
        "Kernel watchdog hatalarını inceler.",
        [
            "dmesg -T | grep -i watchdog",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_kernel_lockup():
    return _info(
        "Kernel lockup kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'soft lockup|hard lockup|watchdog'",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_kernel_stall():
    return _info(
        "RCU stall kayıtlarını inceler.",
        [
            "dmesg -T | grep -i 'rcu.*stall'",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_hung_task():
    return _info(
        "Hung task kayıtlarını inceler.",
        [
            "dmesg -T | grep -i 'hung task'",
            "journalctl -k -p err --no-pager"
        ]
    )


def diagnose_process_termination():
    return _info(
        "Kernel tarafından sonlandırılan işlemleri inceler.",
        [
            "dmesg -T | grep -Ei 'killed process|out of memory|oom'",
            "journalctl -k -p err --no-pager"
        ]
    )