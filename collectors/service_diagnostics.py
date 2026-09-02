import subprocess


def get_service_diagnostics(unit):
    if not unit:
        return {
            "success": False,
            "status": "",
            "logs": "",
            "error": "Unit belirtilmedi.",
        }

    if unit.endswith(".scope"):
        return {
            "success": False,
            "status": "",
            "logs": "",
            "error": "Geçici scope unit'i artık mevcut değil.",
        }

    status_result = subprocess.run(
        ["systemctl", "status", unit, "--no-pager"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    log_result = subprocess.run(
        ["journalctl", "-u", unit, "-b", "--no-pager", "-n", "30"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    return {
        "success": status_result.returncode == 0,
        "status": status_result.stdout.strip(),
        "logs": log_result.stdout.strip(),
        "error": status_result.stderr.strip() or None,
    }