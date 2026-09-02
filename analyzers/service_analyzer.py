def analyze_service_error(log, diagnostics=None):
    diagnostics = diagnostics or {}

    return {
        "category": log.get("category", "unknown"),
        "problem": log.get("problem", "unknown"),
        "service": log.get("service"),
        "unit": log.get("unit"),
        "severity": log.get("severity", "low"),
        "confidence": log.get("confidence", 0.30),
        "solution": log.get("solution", "manual_review"),
        "message": log.get(
            "message",
            "Sorun türü belirlenemedi."
        ),
    }

