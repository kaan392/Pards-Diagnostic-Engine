def get_service_rule(analysis):
    problem = analysis.get("problem", "unknown")
    solution = analysis.get("solution", "manual_review")

    rules = {
        "service_start_failure": {
            "action": "diagnose_service",
            "automatic_repair": False,
            "reason": "Servis başlatma hatasının nedeni belirlenemedi."
        },

        "service_not_found": {
            "action": "ignore",
            "automatic_repair": False,
            "reason": "Servis veya unit bulunamadı."
        },

        "temporary_scope": {
            "action": "ignore",
            "automatic_repair": False,
            "reason": "Geçici scope artık mevcut değil."
        },

        "missing_kernel_headers": {
            "action": "install_kernel_headers",
            "automatic_repair": False,
            "reason": "Kernel header paketleri eksik."
        },

        "kernel_reboot_required": {
            "action": "reboot_and_reconfigure_virtualbox",
            "automatic_repair": False,
            "reason": "Yeni kernel kuruldu ama sistem yeniden başlatılmadı."
        }
    }

    if problem in rules:
        return rules[problem]

    return {
        "action": solution,
        "automatic_repair": False,
        "reason": "Knowledge Base tarafından belirlenen çözüm."
    }