def find_root_cause(analysis, diagnostics=None):
    diagnostics = diagnostics or {}

    problem = analysis.get("problem", "unknown")
    unit = analysis.get("unit")

    diagnostic_error = (
        diagnostics.get("error") or ""
    ).lower()

    diagnostic_logs = (
        diagnostics.get("logs") or ""
    ).lower()

    # Kernel header eksikliği
    if (
        unit == "vboxadd.service"
        and "kernel headers not found" in diagnostic_logs
    ):
        # Gerçek Linux durumunda, bu hata çoğu zaman yeni kernel kurulumundan
        # sonra sistemin yeniden başlatılmaması nedeniyle oluşur.
        if "target kernel" in diagnostic_logs:
            return {
                "cause": "kernel_reboot_required",
                "explanation": "Yeni kernel kurulmuş ama sistem hâlâ eski kernel ile çalışıyor. Yeniden başlatıp VirtualBox Guest Additions kurulmalıdır.",
                "confidence": 0.99,
                "category": "kernel"
            }

        return {
            "cause": "missing_kernel_headers",
            "explanation": "Çalışan kernel için gerekli kernel header paketleri bulunamadı.",
            "confidence": 0.99,
            "category": "kernel"
        }

    # Servis bulunamadı
    if "could not be found" in diagnostic_error:
        return {
            "cause": "service_not_found",
            "explanation": "İlgili systemd unit'i sistemde bulunamadı.",
            "confidence": 0.99,
            "category": "systemd"
        }

    # Geçici scope
    if "geçici scope" in diagnostic_error:
        return {
            "cause": "temporary_scope",
            "explanation": "Bu scope geçici olarak oluşturulduğu için artık mevcut değil.",
            "confidence": 0.99,
            "category": "systemd"
        }

    # vmwgfx
    if "unsupported hypervisor" in diagnostic_logs:
        return {
            "cause": "vmwgfx_hypervisor_incompatible",
            "explanation": "vmwgfx sürücüsü mevcut sanallaştırma grafik yapılandırmasıyla uyumsuz.",
            "confidence": 0.98,
            "category": "graphics"
        }

    # Analiz zaten problemi bulduysa
    if problem != "unknown":
        category = analysis.get("category", "unknown")

        # Problem adına göre doğru kategori
        if problem.startswith("kernel_") or problem in {
            "missing_kernel_headers",
            "firmware_load_failed"
        }:
            category = "kernel"

        elif problem.startswith("vmwgfx_") or problem.startswith("gpu_"):
            category = "graphics"

        elif problem.startswith("storage_"):
            category = "storage"

        return {
            "cause": problem,
            "explanation": analysis.get(
                "message",
                "Kök neden analiz sonucundan belirlendi."
            ),
            "confidence": analysis.get("confidence", 0.50),
            "category": category
        }

    return {
        "cause": "unknown",
        "explanation": "Kök neden mevcut bilgilerle belirlenemedi.",
        "confidence": 0.30,
        "category": analysis.get("category", "unknown")
    }