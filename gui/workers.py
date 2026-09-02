import subprocess

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from app.collectors.system import collect_system_info
from app.collectors.hardware import collect_hardware_info
from app.collectors.logs import collect_error_logs
from app.collectors.service_diagnostics import get_service_diagnostics

from app.analyzers.log_parser import parse_log_line
from app.analyzers.log_filter import group_logs
from app.analyzers.service_analyzer import analyze_service_error
from app.analyzers.root_cause import find_root_cause

from app.rules.service_rules import get_service_rule
from app.repair.repair_engine import get_repair


class DiagnosticWorker(QObject):
    progress_changed = pyqtSignal(int, str)
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    @pyqtSlot()
    def run(self):
        try:
            self.progress_changed.emit(5, "Sistem bilgileri okunuyor...")
            system = collect_system_info()
            hardware = collect_hardware_info()

            self.progress_changed.emit(15, "Sistem günlükleri okunuyor...")
            logs = collect_error_logs()

            if not logs.get("success"):
                raise RuntimeError(logs.get("error", "Loglar alınamadı."))

            self.progress_changed.emit(30, "Günlükler analiz ediliyor...")

            parsed = []

            for line in logs.get("logs", []):
                item = parse_log_line(line)
                if item:
                    parsed.append(item)

            groups = group_logs(parsed)

            results = []
            total = max(len(groups), 1)

            for i, group in enumerate(groups):
                category = group.get("category", "unknown")
                unit = group.get("unit")

                progress = 40 + int((i / total) * 50)
                self.progress_changed.emit(
                    progress,
                    f"{category} problemi inceleniyor..."
                )

                if unit:
                    diagnostics = get_service_diagnostics(unit)
                else:
                    diagnostics = {
                        "success": False,
                        "status": "",
                        "logs": "",
                        "error": ""
                    }

                analysis = analyze_service_error(
                    group,
                    diagnostics
                )

                analysis["category"] = category

                root = find_root_cause(
                    analysis,
                    diagnostics
                )

                if root.get("cause") != "unknown":
                    analysis["problem"] = root["cause"]
                    analysis["confidence"] = root["confidence"]
                    analysis["category"] = root.get(
                        "category",
                        category
                    )

                rule = get_service_rule(analysis)
                action = rule.get("action")

                repair = None

                if action and action != "ignore":
                    repair = get_repair(
                        analysis["category"],
                        action
                    )

                results.append({
                    "group": group,
                    "analysis": analysis,
                    "root_cause": root,
                    "rule": rule,
                    "repair": repair
                })

            self.progress_changed.emit(
                100,
                "Tarama tamamlandı."
            )

            self.result_ready.emit({
                "system": system,
                "hardware": hardware,
                "results": results
            })

        except Exception as exc:
            self.error_occurred.emit(str(exc))

        finally:
            self.finished.emit()


class RepairWorker(QObject):
    progress_changed = pyqtSignal(int, str)
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, repair):
        super().__init__()
        self.repair = repair

    @pyqtSlot()
    def run(self):
        try:
            if not self.repair or not self.repair.get("success"):
                raise RuntimeError(
                    self.repair.get("error", "Onarım bulunamadı.")
                    if self.repair
                    else "Onarım bilgisi bulunamadı."
                )

            solution = self.repair.get("solution", {})
            command = solution.get("command")

            if not command:
                self.result_ready.emit({
                    "success": False,
                    "message": "Bu çözüm için çalıştırılabilir komut bulunmuyor."
                })
                return

            self.progress_changed.emit(
                20,
                "Yetkilendirme isteniyor..."
            )

            # Komutlar backend tarafından üretildiği için
            # doğrudan shell üzerinden çalıştırılır.
            #
            # sudo komutları varsa pkexec ile çalıştırılır.
            if command.strip().startswith("sudo "):
                command = command.strip()[5:]

                process = subprocess.run(
                    ["pkexec", "sh", "-c", command],
                    text=True,
                    capture_output=True
                )
            else:
                process = subprocess.run(
                    ["sh", "-c", command],
                    text=True,
                    capture_output=True
                )

            if process.returncode != 0:
                error = process.stderr.strip()

                if not error:
                    error = "Komut çalıştırılamadı."

                self.result_ready.emit({
                    "success": False,
                    "message": error,
                    "returncode": process.returncode
                })
                return

            self.progress_changed.emit(
                100,
                "Onarım başarıyla tamamlandı."
            )

            self.result_ready.emit({
                "success": True,
                "message": process.stdout.strip()
                or "Onarım başarıyla tamamlandı."
            })

        except Exception as exc:
            self.error_occurred.emit(str(exc))

        finally:
            self.finished.emit()


class BulkRepairWorker(QObject):
    """Birden fazla onarımı background thread'de çalıştır"""
    progress_changed = pyqtSignal(int, str)
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, repairs, reboot_needed=False):
        super().__init__()
        self.repairs = repairs
        self.reboot_needed = reboot_needed

    @pyqtSlot()
    def run(self):
        try:
            successful = 0
            failed = 0

            for i, repair in enumerate(self.repairs):
                progress = int((i / max(len(self.repairs), 1)) * 80)
                command = repair.get("solution", {}).get("command")

                if not command:
                    failed += 1
                    continue

                self.progress_changed.emit(
                    progress,
                    f"[{i+1}/{len(self.repairs)}] Komut çalıştırılıyor..."
                )

                shell_command = command.strip()
                if shell_command.startswith("sudo "):
                    shell_command = shell_command[5:]
                    process = subprocess.run(
                        ["pkexec", "sh", "-c", shell_command],
                        text=True,
                        capture_output=True,
                        timeout=300
                    )
                else:
                    process = subprocess.run(
                        ["sh", "-c", shell_command],
                        text=True,
                        capture_output=True,
                        timeout=300
                    )

                if process.returncode == 0:
                    successful += 1
                    self.progress_changed.emit(progress, f"✓ {i+1} başarılı")
                else:
                    failed += 1
                    error_msg = process.stderr.strip() or process.stdout.strip() or "Bilinmeyen hata"
                    self.progress_changed.emit(progress, f"✗ {i+1} hata: {error_msg[:50]}")

            # Reboot gerekirse
            if self.reboot_needed:
                self.progress_changed.emit(
                    90,
                    "Sistem yeniden başlatılıyor..."
                )
                subprocess.run(
                    ["sudo", "reboot"],
                    capture_output=True,
                    timeout=10
                )

            self.progress_changed.emit(100, "Tamamlandı")

            self.result_ready.emit({
                "success": True,
                "successful": successful,
                "failed": failed,
                "reboot_needed": self.reboot_needed
            })

        except Exception as exc:
            self.error_occurred.emit(str(exc))

        finally:
            self.finished.emit()