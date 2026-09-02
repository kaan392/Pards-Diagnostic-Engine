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


def diagnose_gnome_shell():
    return _info(
        "GNOME Shell çökme kayıtlarını ve oturum durumunu inceler.",
        [
            "journalctl --user -b -p err --no-pager | grep -i 'gnome-shell'",
            "journalctl --user -b --no-pager | grep -Ei 'gnome-shell|mutter'"
        ]
    )


def diagnose_gnome_session():
    return _info(
        "GNOME oturumunun çökme kayıtlarını inceler.",
        [
            "journalctl --user -b -p err --no-pager | grep -Ei 'gnome-session|session'",
            "systemctl --user --failed"
        ]
    )


def diagnose_gdm():
    return _info(
        "GDM servis durumunu ve hata kayıtlarını inceler.",
        [
            "systemctl status gdm --no-pager",
            "journalctl -u gdm -b -p err --no-pager"
        ]
    )


def diagnose_display_manager():
    return _info(
        "Display manager servislerini ve durumlarını kontrol eder.",
        [
            "systemctl status display-manager --no-pager",
            "journalctl -u display-manager -b -p err --no-pager"
        ]
    )


def diagnose_display():
    return _info(
        "DISPLAY değişkenini ve aktif görüntü oturumunu kontrol eder.",
        [
            "echo $DISPLAY",
            "loginctl list-sessions"
        ]
    )


def diagnose_display_authorization():
    return _info(
        "Display erişim yetkilendirmesini kontrol eder.",
        [
            "echo $XAUTHORITY",
            "ls -la ~/.Xauthority 2>/dev/null"
        ]
    )


def diagnose_x_connection():
    return _info(
        "X bağlantısı ve X sunucusu kayıtlarını inceler.",
        [
            "echo $DISPLAY",
            "journalctl -b --no-pager | grep -Ei 'X connection|X server'"
        ]
    )


def diagnose_xorg():
    return _info(
        "Xorg hata kayıtlarını inceler.",
        [
            "journalctl -b --no-pager | grep -Ei 'Xorg|X server'",
            "grep -Ei '\\(EE\\)|\\(WW\\)' /var/log/Xorg.0.log 2>/dev/null"
        ]
    )


def diagnose_wayland():
    return _info(
        "Wayland oturumu ve compositor hata kayıtlarını inceler.",
        [
            "echo $XDG_SESSION_TYPE",
            "journalctl --user -b --no-pager | grep -Ei 'wayland|compositor'"
        ]
    )


def diagnose_application_launch():
    return _info(
        "Uygulama başlatma hatalarını inceler.",
        [
            "journalctl --user -b -p err --no-pager",
            "systemctl --user --failed"
        ]
    )


def diagnose_application_crash():
    return _info(
        "Masaüstü uygulamalarındaki çökme kayıtlarını inceler.",
        [
            "journalctl --user -b -p err --no-pager",
            "coredumpctl --user list --no-pager"
        ]
    )


def diagnose_application():
    return _info(
        "Yanıt vermeyen uygulamalarla ilgili kullanıcı oturumu kayıtlarını inceler.",
        [
            "journalctl --user -b -p warning --no-pager",
            "ps aux --sort=-%cpu | head -n 15"
        ]
    )


def diagnose_desktop_environment():
    return _info(
        "Masaüstü ortamının ve kullanıcı oturumunun durumunu kontrol eder.",
        [
            "echo $XDG_CURRENT_DESKTOP",
            "echo $XDG_SESSION_DESKTOP",
            "loginctl session-status"
        ]
    )


def restart_desktop_panel():
    return _action(
        "GNOME masaüstü panelini yeniden başlatmayı dener.",
        "gnome-shell --replace >/dev/null 2>&1 &"
    )


def restart_window_manager():
    return _action(
        "GNOME Shell/Mutter bileşenini yeniden başlatmayı dener.",
        "gnome-shell --replace >/dev/null 2>&1 &"
    )


def diagnose_window_manager():
    return _info(
        "Pencere yöneticisi ve compositor durumunu inceler.",
        [
            "ps aux | grep -Ei 'gnome-shell|mutter' | grep -v grep",
            "journalctl --user -b --no-pager | grep -Ei 'mutter|window manager'"
        ]
    )


def diagnose_desktop_extension():
    return _info(
        "GNOME Shell eklentilerinin durumunu ve hata kayıtlarını inceler.",
        [
            "gnome-extensions list",
            "journalctl --user -b --no-pager | grep -Ei 'extension|gnome-shell'"
        ]
    )


def disable_desktop_extension():
    return _action(
        "GNOME Shell eklentilerini devre dışı bırakmayı dener.",
        "gnome-extensions disable --all"
    )


def diagnose_user_session():
    return _info(
        "Kullanıcı oturumunun başlatılma durumunu inceler.",
        [
            "loginctl session-status",
            "systemctl --user --failed"
        ]
    )


def diagnose_user_profile():
    return _info(
        "Kullanıcı profilinin ve HOME dizininin durumunu kontrol eder.",
        [
            "echo $HOME",
            "ls -ld \"$HOME\"",
            "id"
        ]
    )


def diagnose_user_directory():
    return _info(
        "Kullanıcı dizininin mount durumunu kontrol eder.",
        [
            "findmnt \"$HOME\"",
            "df -h \"$HOME\""
        ]
    )


def diagnose_screen_lock():
    return _info(
        "Ekran kilitleme bileşenlerinin durumunu inceler.",
        [
            "loginctl lock-sessions",
            "journalctl --user -b --no-pager | grep -Ei 'lock|screensaver'"
        ]
    )


def diagnose_suspend():
    return _info(
        "Askıya alma işlemiyle ilgili systemd kayıtlarını inceler.",
        [
            "systemctl status sleep.target suspend.target --no-pager",
            "journalctl -b --no-pager | grep -Ei 'suspend|sleep'"
        ]
    )


def diagnose_resume():
    return _info(
        "Uyandırma/resume işlemiyle ilgili kernel ve systemd kayıtlarını inceler.",
        [
            "journalctl -b --no-pager | grep -Ei 'resume|wake'",
            "journalctl -k -b -p err --no-pager"
        ]
    )


def diagnose_desktop():
    return _info(
        "Masaüstü ortamının genel durumunu ve hata kayıtlarını inceler.",
        [
            "echo $XDG_CURRENT_DESKTOP",
            "systemctl --user --failed",
            "journalctl --user -b -p err --no-pager"
        ]
    )
