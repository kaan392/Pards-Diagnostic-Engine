import json
from pathlib import Path


KNOWLEDGE_BASE = Path(__file__).parent.parent / "knowledge_base"


def load_rules():
    rules = []

    for file in KNOWLEDGE_BASE.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for rule in data:
                rule["category"] = file.stem
                rules.append(rule)

        except (json.JSONDecodeError, OSError):
            continue

    return rules


def classify_log(log):
    message = log.get("message", "").lower()

    best_match = None
    best_score = 0

    for rule in load_rules():
        pattern = rule.get("pattern", "").lower()

        if not pattern:
            continue

        if pattern in message:
            score = len(pattern)

            if score > best_score:
                best_score = score
                best_match = rule

    if best_match is None:
        return {
            "category": "unknown",
            "problem": "unknown",
            "severity": "low",
            "solution": "manual_review",
            "confidence": 0.30
        }

    return {
        "category": best_match["category"],
        "problem": best_match["problem"],
        "severity": best_match["severity"],
        "solution": best_match["solution"],
        "confidence": min(0.95, 0.50 + (best_score / 100))
    }