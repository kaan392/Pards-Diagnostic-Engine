from . import kernel_repairs
from . import graphics_repairs
from . import storage_repairs
from . import network_repairs
from . import packages_repairs
from . import permissions_repairs
from . import desktop_repairs
from . import systemd_repairs


def safe_apt_install(package_name, reinstall=False, fallback_package=None):
    reinstall_flag = "--reinstall " if reinstall else ""
    fallback = fallback_package or ""

    if fallback:
        fallback_clause = (
            f"else echo \"Paket bulunamadı: $PKG; alternatif paket deneniyor: {fallback}\"; "
            f"apt-get install -y {reinstall_flag}{fallback}; fi"
        )
    else:
        fallback_clause = "else echo \"Paket bulunamadı: $PKG\"; exit 1; fi"

    return (
        f"sudo sh -c 'PKG=\"{package_name}\"; "
        f"if apt-cache policy \"$PKG\" >/dev/null 2>&1; then "
        f"apt-get install -y {reinstall_flag}\"$PKG\"; "
        f"{fallback_clause}'"
    )


REPAIR_MODULES = {
    "kernel": kernel_repairs,
    "graphics": graphics_repairs,
    "storage": storage_repairs,
    "network": network_repairs,
    "packages": packages_repairs,
    "permissions": permissions_repairs,
    "desktop": desktop_repairs,
    "systemd": systemd_repairs,
}


def get_repair(category, solution):
    module = REPAIR_MODULES.get(category)

    if module is None:
        return {
            "success": False,
            "error": f"Repair modülü bulunamadı: {category}"
        }

    function = getattr(module, solution, None)

    if function is None:
        return {
            "success": False,
            "error": f"Repair fonksiyonu bulunamadı: {solution}"
        }

    try:
        result = function()

        return {
            "success": True,
            "solution": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Repair çalıştırılırken hata oluştu: {e}"
        }