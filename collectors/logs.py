import subprocess


def collect_error_logs(limit=30):
    command = [
        "journalctl",
        "-p", "err",
        "-b",
        "--no-pager",
        "-n", str(limit),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip(),
            "logs": [],
        }

    logs = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    return {
        "success": True,
        "error": None,
        "logs": logs,
    }