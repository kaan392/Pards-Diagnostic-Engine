import re


def normalize_message(message):
    message = re.sub(r"\d+", "<N>", message)
    message = re.sub(r"x[0-9a-fA-F]+", "<HEX>", message)
    return message.strip()


def is_diagnostic_log(log):
    category = log.get("category", "unknown")

    # Classifier bir problem bulduysa diagnostik olarak kabul et
    if category != "unknown":
        return True

    # Classifier bulamadıysa sadece gerçek systemd servislerini kabul et
    service = log.get("service")
    unit = log.get("unit")

    if service == "systemd" and unit:
        if unit.endswith(".scope"):
            return False

        return True

    return False


def group_logs(logs):
    groups = {}

    for log in logs:

        if not is_diagnostic_log(log):
            continue

        key = (
            log.get("category", "unknown"),
            log.get("problem", "unknown"),
            log.get("service"),
            log.get("unit"),
            normalize_message(log.get("message", ""))
        )

        if key not in groups:
            groups[key] = {
                "category": log.get("category", "unknown"),
                "problem": log.get("problem", "unknown"),
                "solution": log.get("solution", "manual_review"),
                "severity": log.get("severity", "low"),
                "confidence": log.get("confidence", 0.30),
                "service": log.get("service"),
                "unit": log.get("unit"),
                "message": log.get("message"),
                "count": 0,
            }

        groups[key]["count"] += 1

    return list(groups.values())