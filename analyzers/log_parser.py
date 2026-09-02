import re

from .classifier import classify_log


def parse_log_line(line):

    parts = line.split(None, 4)

    if len(parts) < 5:
        parsed = {
            "timestamp": None,
            "hostname": None,
            "service": None,
            "unit": None,
            "severity": "error",
            "message": line,
        }

        classification = classify_log(parsed)

        parsed.update(classification)

        return parsed

    timestamp = " ".join(parts[:3])
    hostname = parts[3]
    source = parts[4]

    if ":" in source:
        source_name, message = source.split(":", 1)
    else:
        source_name = source
        message = ""

    source_name = source_name.strip()
    message = message.strip()

    # PID bilgisini temizle
    service = re.sub(r"\[\d+\]$", "", source_name)

    # GDM gibi [ ] hatalı ayrılmış durumları düzelt
    service = service.rstrip("]").strip()

    unit = None

    match = re.search(
        r"Failed to start\s+([^\s]+)",
        message,
        re.IGNORECASE
    )

    if match:
        unit = match.group(1).rstrip(".,:")

    # Sadece systemd servis hatalarında unit kabul et
    if service != "systemd":
        unit = None

    parsed = {
        "timestamp": timestamp,
        "hostname": hostname,
        "service": service,
        "unit": unit,
        "severity": "error",
        "message": message,
    }

    # Logu bilgi tabanındaki 240 senaryo ile eşleştir
    classification = classify_log(parsed)

    # Classification bilgilerini loga ekle
    parsed.update(classification)

    return parsed