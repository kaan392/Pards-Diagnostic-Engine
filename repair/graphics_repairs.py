
import subprocess

def _diagnostic(description, commands):
    return {
        "description": description,
        "commands": commands,
        "requires_confirmation": False
    }

def check_graphics_configuration():
    return _diagnostic(
        "Grafik sürücüsü ve sanal makine grafik yapılandırması incelenir.",
        [
            "lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'",
            "lsmod | grep -E 'vmwgfx|virtio_gpu|vboxvideo'",
            "systemd-detect-virt"
        ]
    )

def diagnose_display_configuration():
    return _diagnostic(
        "Ekran ve görüntü yapılandırması incelenir.",
        [
            "xrandr --query",
            "ls /dev/dri/",
            "lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'"
        ]
    )

def diagnose_nvidia_driver():
    return _diagnostic(
        "NVIDIA sürücüsünün durumu incelenir.",
        [
            "lspci -nnk | grep -A3 -i nvidia",
            "lsmod | grep nvidia",
            "nvidia-smi"
        ]
    )


def diagnose_amdgpu_driver():
    return _diagnostic(
        "AMD GPU sürücüsünün durumu incelenir.",
        [
            "lspci -nnk | grep -A3 -i amd",
            "lsmod | grep amdgpu",
            "dmesg | grep -i amdgpu"
        ]
    )


def diagnose_intel_graphics():
    return _diagnostic(
        "Intel grafik sürücüsünün durumu incelenir.",
        [
            "lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'",
            "lsmod | grep i915",
            "dmesg | grep -i i915"
        ]
    )


def diagnose_drm():
    return _diagnostic(
        "DRM grafik altyapısı incelenir.",
        [
            "ls -l /dev/dri/",
            "dmesg | grep -i drm",
            "lsmod | grep drm"
        ]
    )


def diagnose_gpu_hardware():
    return _diagnostic(
        "GPU donanım bağlantısı ve kernel kayıtları incelenir.",
        [
            "lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'",
            "dmesg | grep -Ei 'gpu|pcie|hardware'",
            "journalctl -k -b --no-pager | grep -Ei 'gpu|pcie'"
        ]
    )


def diagnose_gpu_reset():
    return _diagnostic(
        "GPU reset kayıtları incelenir.",
        [
            "dmesg | grep -Ei 'gpu|reset'",
            "journalctl -k -b --no-pager | grep -Ei 'gpu|reset'"
        ]
    )


def diagnose_gpu_hang():
    return _diagnostic(
        "GPU kilitlenmesiyle ilgili kernel kayıtları incelenir.",
        [
            "dmesg | grep -Ei 'gpu|hang'",
            "journalctl -k -b --no-pager | grep -Ei 'gpu|hang'"
        ]
    )


def diagnose_gpu_fault():
    return _diagnostic(
        "GPU hata kayıtları incelenir.",
        [
            "dmesg | grep -Ei 'gpu|fault'",
            "journalctl -k -b --no-pager | grep -Ei 'gpu|fault'"
        ]
    )


def diagnose_display_mode():
    return _diagnostic(
        "Ekran modu ve çözünürlük yapılandırması incelenir.",
        [
            "xrandr --query",
            "xrandr --listmonitors"
        ]
    )


def diagnose_display_server():
    return _diagnostic(
        "Görüntü sunucusunun durumu incelenir.",
        [
            "echo $DISPLAY",
            "echo $XDG_SESSION_TYPE",
            "systemctl --user status graphical-session.target --no-pager"
        ]
    )


def diagnose_xorg():
    return _diagnostic(
        "Xorg hata kayıtları incelenir.",
        [
            "journalctl -b --no-pager | grep -i xorg",
            "find /var/log -iname '*Xorg*' -type f 2>/dev/null"
        ]
    )


def diagnose_gnome_shell():
    return _diagnostic(
        "GNOME Shell ve Mutter hata kayıtları incelenir.",
        [
            "journalctl --user -b --no-pager | grep -Ei 'gnome-shell|mutter'"
        ]
    )


def diagnose_wayland():
    return _diagnostic(
        "Wayland compositor hata kayıtları incelenir.",
        [
            "echo $XDG_SESSION_TYPE",
            "journalctl --user -b --no-pager | grep -i wayland"
        ]
    )


def diagnose_gbm():
    return _diagnostic(
        "GBM grafik altyapısı incelenir.",
        [
            "ls -l /dev/dri/",
            "ldconfig -p | grep gbm"
        ]
    )


def diagnose_egl():
    return _diagnostic(
        "EGL yapılandırması incelenir.",
        [
            "eglinfo 2>/dev/null",
            "ldconfig -p | grep EGL"
        ]
    )


def diagnose_opengl():
    return _diagnostic(
        "OpenGL yapılandırması incelenir.",
        [
            "glxinfo -B 2>/dev/null",
            "eglinfo 2>/dev/null"
        ]
    )


def install_gpu_firmware():
    return {
        "description": "GPU firmware paketlerinin durumu kontrol edilir.",
        "command": "dmesg | grep -Ei 'firmware|gpu'",
        "requires_confirmation": False
    }


def diagnose_display_driver():
    return _diagnostic(
        "Görüntü sürücüsünün yüklenme durumu incelenir.",
        [
            "lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'",
            "lsmod"
        ]
    )


def diagnose_display_flickering():
    return _diagnostic(
        "Ekran titremesiyle ilgili grafik ve kernel kayıtları incelenir.",
        [
            "journalctl -b --no-pager | grep -Ei 'display|drm|gpu|flicker'",
            "dmesg | grep -Ei 'drm|gpu|display'"
        ]
    )


def diagnose_black_screen():
    return _diagnostic(
        "Siyah ekran sorununun grafik ve görüntü sunucusu kaynakları incelenir.",
        [
            "systemctl status display-manager --no-pager",
            "journalctl -b --no-pager | grep -Ei 'display|drm|gpu|xorg|wayland'",
            "ls -l /dev/dri/"
        ]
    )


def diagnose_display_connection():
    return _diagnostic(
        "Ekran bağlantısı ve algılanan monitörler incelenir.",
        [
            "xrandr --query",
            "xrandr --listmonitors"
        ]
    )
