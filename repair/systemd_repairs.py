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


def diagnose_service():
    return _info(
        "Servisin durumunu, son hata kayıtlarını ve bağımlılıklarını inceler.",
        [
            "systemctl status \"${SERVICE}\" --no-pager",
            "journalctl -u \"${SERVICE}\" -b -p err --no-pager",
            "systemctl list-dependencies \"${SERVICE}\" --no-pager"
        ]
    )


def diagnose_service_timeout():
    return _info(
        "Servisin zaman aşımı kayıtlarını inceler.",
        [
            "systemctl status \"${SERVICE}\" --no-pager",
            "journalctl -u \"${SERVICE}\" -b --no-pager | grep -Ei 'timeout|timed out'",
            "systemctl show \"${SERVICE}\" --property=TimeoutStartUSec,TimeoutStopUSec"
        ]
    )


def check_service_unit():
    return _info(
        "Servis unit dosyasının ve servis tanımının mevcut olup olmadığını kontrol eder.",
        [
            "systemctl cat \"${SERVICE}\" --no-pager",
            "systemctl show \"${SERVICE}\" --property=FragmentPath,LoadState,UnitFileState"
        ]
    )


def diagnose_service_dependencies():
    return _info(
        "Servisin bağımlılıklarını ve başarısız bağımlılıkları inceler.",
        [
            "systemctl list-dependencies \"${SERVICE}\" --no-pager",
            "systemctl list-dependencies \"${SERVICE}\" --failed --no-pager",
            "systemctl status \"${SERVICE}\" --no-pager"
        ]
    )


def diagnose_systemd_job():
    return _info(
        "Systemd job durumunu ve başarısız job kayıtlarını inceler.",
        [
            "systemctl list-jobs",
            "systemctl --failed --no-pager",
            "journalctl -b -p err --no-pager"
        ]
    )


def check_systemd_jobs():
    return _info(
        "Çalışan systemd job'larını kontrol eder.",
        [
            "systemctl list-jobs",
            "systemctl list-units --state=activating --no-pager"
        ]
    )


def diagnose_device_timeout():
    return _info(
        "Cihaz bekleme zaman aşımının nedenini inceler.",
        [
            "systemctl list-jobs",
            "systemctl --failed --no-pager",
            "journalctl -b -p err --no-pager | grep -Ei 'timed out|device'"
        ]
    )


def diagnose_systemd_timeout():
    return _info(
        "Systemd bekleme zaman aşımının nedenini inceler.",
        [
            "systemctl list-jobs",
            "journalctl -b -p err --no-pager | grep -Ei 'timeout|timed out'",
            "systemctl --failed --no-pager"
        ]
    )


def check_service_permissions():
    return _info(
        "Servis unit dosyasının ve çalıştırdığı dosyaların izin durumunu kontrol eder.",
        [
            "systemctl show \"${SERVICE}\" --property=FragmentPath,User,Group",
            "systemctl cat \"${SERVICE}\" --no-pager",
            "namei -l \"${SERVICE_PATH}\""
        ]
    )


def check_service_configuration():
    return _info(
        "Servis yapılandırmasının geçerli olup olmadığını kontrol eder.",
        [
            "systemctl cat \"${SERVICE}\" --no-pager",
            "systemd-analyze verify \"${SERVICE}\"",
            "systemctl show \"${SERVICE}\" --no-pager"
        ]
    )


def diagnose_systemd_bus():
    return _info(
        "Systemd D-Bus bağlantısının ve PID 1 durumunun çalışıp çalışmadığını inceler.",
        [
            "systemctl is-system-running",
            "systemctl status dbus --no-pager",
            "journalctl -b -p err --no-pager | grep -Ei 'bus|dbus|systemd'"
        ]
    )


def diagnose_systemd_socket():
    return _info(
        "Systemd socket ve dinleme hatalarını inceler.",
        [
            "systemctl list-sockets --all",
            "ss -lntup",
            "journalctl -b -p err --no-pager | grep -Ei 'listen|socket'"
        ]
    )


def diagnose_service_port():
    return _info(
        "Kullanılmakta olan portu ve ilgili işlemi belirler.",
        [
            "ss -lntup",
            "ss -lunp",
            "systemctl --failed --no-pager"
        ]
    )


def diagnose_service_watchdog():
    return _info(
        "Servis watchdog zaman aşımı kayıtlarını inceler.",
        [
            "systemctl status \"${SERVICE}\" --no-pager",
            "journalctl -u \"${SERVICE}\" -b --no-pager | grep -i watchdog",
            "systemctl show \"${SERVICE}\" --property=WatchdogUSec"
        ]
    )


def diagnose_service_memory():
    return _info(
        "Servisin bellek kullanımını ve OOM kayıtlarını inceler.",
        [
            "systemctl status \"${SERVICE}\" --no-pager",
            "journalctl -u \"${SERVICE}\" -b --no-pager | grep -Ei 'oom|out of memory|killed'",
            "systemctl show \"${SERVICE}\" --property=MemoryCurrent,MemoryMax"
        ]
    )