import json
import re
from functools import lru_cache
from pathlib import Path


KNOWLEDGE_BASE = Path(__file__).parent.parent / "knowledge_base"

_CATEGORY_NAMES = {
    "desktop": "masaüstü",
    "graphics": "grafik",
    "kernel": "kernel",
    "network": "ağ",
    "packages": "paket yönetimi",
    "permissions": "izin",
    "storage": "depolama",
    "systemd": "sistem servisi",
}

_TERM_NAMES = {
    "ata": "ATA/SATA",
    "btrfs": "BTRFS",
    "buffer": "tampon",
    "block": "blok aygıtı",
    "device": "aygıt",
    "disk": "disk",
    "error": "hatası",
    "failed": "başarısız",
    "filesystem": "dosya sistemi",
    "firmware": "ürün yazılımı",
    "gpu": "GPU",
    "header": "header",
    "io": "I/O",
    "journal": "journal",
    "kernel": "kernel",
    "link": "bağlantı",
    "mount": "bağlama",
    "network": "ağ",
    "package": "paket",
    "permission": "izin",
    "repository": "depo",
    "service": "servis",
    "storage": "depolama",
    "superblock": "superblock",
    "systemd": "systemd",
    "timeout": "zaman aşımı",
    "warning": "uyarısı",
    "xfs": "XFS",
}


@lru_cache(maxsize=1)
def _scenario_by_problem():
    scenarios = {}
    for path in KNOWLEDGE_BASE.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in data:
            scenarios[item.get("problem")] = (path.stem, item)
    return scenarios


def _humanize_problem(problem):
    problem = problem.replace("block_device", "block")
    words = re.sub(r"[^a-zA-Z0-9]+", " ", problem).split()
    return " ".join(_TERM_NAMES.get(word.lower(), word) for word in words)


def _action_text(category, solution):
    area = _CATEGORY_NAMES.get(category, "ilgili sistem bileşeni")
    words = solution.split("_", 1)
    operation = {
        "check": "kontrol",
        "diagnose": "inceleme",
        "install": "kurulum kontrolü",
        "repair": "onarım öncesi inceleme",
        "restart": "yeniden başlatma kontrolü",
        "reboot": "yeniden başlatma kontrolü",
        "run": "kontrol çalıştırılması",
        "clear": "temizlik kontrolü",
        "reset": "sıfırlama kontrolü",
    }.get(words[0], "inceleme")
    if solution.startswith("ignore"):
        return "Kayıt geçici veya etkisiz olabilir; tekrar oluşup oluşmadığı izlenmeli."
    return f"Önerilen ilk adım, {area} için {operation} yapılmasıdır; işlemden önce mevcut durum doğrulanmalı."


def build_issue_details(category, problem, message, solution):
    scenario = _scenario_by_problem().get(problem, (category, {}))[1]
    pattern = scenario.get("pattern") or message or problem
    label = _humanize_problem(problem)
    area = _CATEGORY_NAMES.get(category, "sistem")
    explanation = (
        f"{area.capitalize()} alanında {label} algılandı. "
        f"Bu uyarı, sistem kayıtlarında '{pattern}' ifadesinin görülmesine dayanıyor. "
        "Tek seferlik bir kayıt olabilir; tekrarlanması durumunda ilgili bileşenin durumu ve son değişiklikler kontrol edilmeli."
    )
    return {
        "explanation": explanation,
        "action": _action_text(category, solution),
    }