import json
import os

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QLineEdit,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)

from app.gui.workers import DiagnosticWorker, BulkRepairWorker
from app.collectors.system import collect_system_info
from app.collectors.hardware import collect_hardware_info
from app.analyzers.issue_details import build_issue_details


class AppWindow(QMainWindow):
    @staticmethod
    def normalize_severity(severity, category, action, has_automatic_fix):
        value = (severity or "low").upper()
        os_related = (category or "").lower() in {"kernel", "systemd", "storage", "permissions", "desktop", "graphics", "network", "packages"}

        if value == "CRITICAL":
            return "CRITICAL" if os_related else "HIGH"
        if value == "HIGH":
            return "HIGH" if os_related else "MEDIUM"
        if value == "MEDIUM":
            return "MEDIUM" if os_related else "INFO"
        return "INFO"

    @staticmethod
    def build_issue_summary(detail):
        return detail.get("explanation", "Sorun açıklaması mevcut değil.")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pardus Diagnostic Engine")
        self.resize(1000, 700)
        self.setMinimumSize(800, 500)

        self.diagnostic_thread = None
        self.diagnostic_worker = None
        self.diagnostic_results = []
        self.knowledge_items = []
        self.issue_details = []

        self.repair_thread = None
        self.repair_worker = None

        self.build_ui()
        self.load_knowledge()
        self.refresh_summary()

        # Sistem monitörü: her 2 saniyede bir sadece sistem bilgilerini güncelle
        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.update_system_info_only)
        self.system_timer.start(2000)

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        self.title = QLabel("Pardus Diagnostic Engine")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold; color: #dfe7ff;")
        header.addWidget(self.title)
        header.addStretch()

        self.scan_btn = QPushButton("Sistemi Tara")
        self.scan_btn.setStyleSheet(
            "QPushButton { background: #7c9cff; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; } "
            "QPushButton:hover { background: #5d7df0; }"
        )
        self.scan_btn.clicked.connect(self.start_diagnostic)
        header.addWidget(self.scan_btn)

        self.bulk_repair_btn = QPushButton("Tümünü Onar")
        self.bulk_repair_btn.setEnabled(False)
        self.bulk_repair_btn.clicked.connect(self.start_bulk_repair)
        self.bulk_repair_btn.setStyleSheet(
            "QPushButton { background: #44c78b; color: #0b1b14; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; } "
            "QPushButton:hover { background: #39b77f; }"
        )
        header.addWidget(self.bulk_repair_btn)

        layout.addLayout(header)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setMaximumHeight(140)
        self.summary.setStyleSheet(
            "QTextEdit { background: #1f2430; color: #dfe7ff; border: 1px solid #3c445c; border-radius: 8px; }"
        )
        layout.addWidget(self.summary)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(180)
        self.log.setStyleSheet(
            "QTextEdit { background: #101722; color: #8ae7a2; border: 1px solid #2e3749; border-radius: 8px; }"
        )
        layout.addWidget(self.log)

        bottom = QHBoxLayout()

        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setStyleSheet(
            "QTextEdit { background: #171d2a; color: #dfe7ff; border: 1px solid #38415d; border-radius: 8px; }"
        )
        self.results_box.setMinimumHeight(250)

        self.knowledge_box = QListWidget()
        self.knowledge_box.setStyleSheet(
            "QListWidget { background: #171d2a; color: #dfe7ff; border: 1px solid #38415d; border-radius: 8px; }"
        )
        self.knowledge_box.setMinimumWidth(320)

        self.detail_box = QTextEdit()
        self.detail_box.setReadOnly(True)
        self.detail_box.setPlaceholderText("Sorun seçin; detay açıklama burada görünecek.")
        self.detail_box.setStyleSheet(
            "QTextEdit { background: #171d2a; color: #dfe7ff; border: 1px solid #38415d; border-radius: 8px; }"
        )
        self.detail_box.setMinimumHeight(180)

        issue_panel = QWidget()
        issue_layout = QVBoxLayout(issue_panel)
        issue_layout.setContentsMargins(0, 0, 0, 0)
        issue_layout.setSpacing(8)
        issue_layout.addWidget(self.knowledge_box)
        issue_layout.addWidget(self.detail_box)

        bottom.addWidget(self.results_box, 2)
        bottom.addWidget(issue_panel, 1)
        layout.addLayout(bottom)

        self.knowledge_box.itemClicked.connect(self.show_issue_detail)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Bilgi tabanında ara...")
        self.search.textChanged.connect(self.filter_knowledge)
        layout.addWidget(self.search)

        self.setStyleSheet(
            "QMainWindow, QWidget { background: #111827; color: #dfe7ff; }"
            "QLabel { color: #dfe7ff; }"
            "QPushButton { border-radius: 8px; }"
        )

    def refresh_summary(self):
        try:
            system = collect_system_info()
            hardware = collect_hardware_info()
            text = (
                f"İşletim Sistemi: {system.get('os', '-')}\n"
                f"Kernel: {system.get('kernel', '-')}\n"
                f"Mimari: {system.get('architecture', '-')}\n"
                f"CPU: {hardware.get('cpu_usage_percent', '-')}% | RAM: {hardware.get('ram_used_percent', '-')}% | Disk: {hardware.get('disk_used_percent', '-')}%"
            )
            self.summary.setPlainText(text)
        except Exception as exc:
            self.summary.setPlainText(f"Sistem bilgileri alınamadı: {exc}")

    def update_system_info_only(self):
        """Sadece sistem bilgilerini güncelle - hafif operasyon"""
        try:
            system = collect_system_info()
            hardware = collect_hardware_info()
            text = (
                f"İşletim Sistemi: {system.get('os', '-')}\n"
                f"Kernel: {system.get('kernel', '-')}\n"
                f"Mimari: {system.get('architecture', '-')}\n"
                f"CPU: {hardware.get('cpu_usage_percent', '-')}% | RAM: {hardware.get('ram_used_percent', '-')}% | Disk: {hardware.get('disk_used_percent', '-')}%"
            )
            self.summary.setPlainText(text)
        except Exception:
            pass

    def start_diagnostic(self):
        if self.diagnostic_thread:
            return

        self.scan_btn.setEnabled(False)
        self.progress.setValue(0)
        self.log.clear()
        self.results_box.clear()
        self.log.append("Sistem taraması başlatılıyor...")

        self.diagnostic_thread = QThread()
        self.diagnostic_worker = DiagnosticWorker()
        self.diagnostic_worker.moveToThread(self.diagnostic_thread)

        self.diagnostic_thread.started.connect(self.diagnostic_worker.run)
        self.diagnostic_worker.progress_changed.connect(self.update_progress)
        self.diagnostic_worker.result_ready.connect(self.diagnostic_finished)
        self.diagnostic_worker.error_occurred.connect(self.worker_error)
        self.diagnostic_worker.finished.connect(self.diagnostic_thread.quit)
        self.diagnostic_worker.finished.connect(self.diagnostic_worker.deleteLater)
        self.diagnostic_thread.finished.connect(self.diagnostic_thread.deleteLater)
        self.diagnostic_thread.finished.connect(self.diagnostic_thread_done)

        self.diagnostic_thread.start()

    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.log.append(f"[{value:03d}%] {message}")

    def diagnostic_finished(self, data):
        self.diagnostic_results = data.get("results", [])
        self.bulk_repair_btn.setEnabled(
            any(
                result.get("repair")
                and result.get("repair", {}).get("success")
                and result.get("rule", {}).get("action") != "ignore"
                for result in self.diagnostic_results
            )
        )
        self.render_results()

    def diagnostic_thread_done(self):
        self.diagnostic_thread = None
        self.diagnostic_worker = None
        self.scan_btn.setEnabled(True)

    def render_results(self):
        if not self.diagnostic_results:
            self.results_box.setPlainText("Sorun bulunamadı.")
            self.knowledge_box.clear()
            self.detail_box.setPlainText("Sorun seçin; detay açıklama burada görünecek.")
            return

        self.knowledge_box.clear()
        self.issue_details = []
        lines = []

        for result in self.diagnostic_results:
            analysis = result.get("analysis", {})
            root = result.get("root_cause", {})
            rule = result.get("rule", {})
            repair = result.get("repair")

            category = analysis.get("category", "unknown").upper()
            problem = analysis.get("problem", "unknown")
            raw_severity = (analysis.get("severity", "low") or "low").upper()
            category = analysis.get("category", "unknown")
            has_fix = bool(repair and repair.get("success") and rule.get("action") not in {"ignore", "manual_review", "review_required", "diagnose_service", "no_action"})
            severity = self.normalize_severity(raw_severity, category, rule.get("action", "manual_review"), has_fix)
            confidence = int(float(analysis.get("confidence", 0)) * 100)
            explanation = root.get("explanation", "")
            action = rule.get("action", "manual_review")
            issue_details = build_issue_details(
                category.lower(),
                problem,
                analysis.get("message", ""),
                action,
            )

            if severity == "HIGH":
                color = "🔴"
            elif severity == "MEDIUM":
                color = "🟡"
            else:
                color = "🔵"

            lines.append(f"{color} [{category}] {problem}")
            lines.append(f"   Seviye: {severity} | Güven: {confidence}%")
            lines.append("")

            detail = {
                "category": category,
                "problem": problem,
                "severity": severity,
                "confidence": confidence,
                "explanation": issue_details["explanation"],
                "action": issue_details["action"],
            }
            self.issue_details.append(detail)

            item = QListWidgetItem(f"{color} {problem}  |  {severity}")
            item.setData(Qt.UserRole, detail)
            self.knowledge_box.addItem(item)

        self.results_box.setPlainText("\n".join(lines))

        if self.knowledge_box.count() > 0:
            self.knowledge_box.setCurrentRow(0)
            self.show_issue_detail(self.knowledge_box.currentItem())
        else:
            self.detail_box.setPlainText("Sorun seçin; detay açıklama burada görünecek.")

    def show_issue_detail(self, item):
        if item is None:
            self.detail_box.setPlainText("Sorun seçin; detay açıklama burada görünecek.")
            return

        detail = item.data(Qt.UserRole)
        if not detail:
            self.detail_box.setPlainText("Detay bilgisi yok.")
            return

        summary = self.build_issue_summary(detail)
        text = (
            f"[ {detail.get('category', 'UNKNOWN')} ] {detail.get('problem', 'Bilinmeyen sorun')}\n\n"
            f"Seviye: {detail.get('severity', 'LOW')}\n"
            f"Güven: {detail.get('confidence', 0)}%\n\n"
            f"Açıklama:\n{summary}\n\n"
            f"Önerilen eylem: {detail.get('action', 'Manuel kontrol önerilir.')}"
        )
        self.detail_box.setPlainText(text)

    def load_knowledge(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))
        self.knowledge_items = []

        if not os.path.isdir(base):
            return

        for filename in sorted(os.listdir(base)):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(base, filename)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, list):
                    for item in data:
                        entry = dict(item)
                        entry["category"] = filename[:-5]
                        self.knowledge_items.append(entry)
            except Exception:
                pass

        self.filter_knowledge("")

    def filter_knowledge(self, text):
        text = text.lower().strip()
        self.knowledge_box.clear()

        for item in self.knowledge_items:
            searchable = " ".join(str(v) for v in item.values()).lower()
            if text and text not in searchable:
                continue
            label = item.get("problem", "Bilinmeyen problem")
            self.knowledge_box.addItem(QListWidgetItem(f"{label} [{item.get('category', '-')}]"))

    def start_bulk_repair(self):
        # Çözebilinecek tüm sorunları topla (ignore değil)
        repairs = []
        reboot_needed = False

        for result in self.diagnostic_results:
            rule = result.get("rule", {})
            action = rule.get("action", "")

            # ignore olmayan ve bir eylem olan sorunları al
            if action and action != "ignore":
                repair = result.get("repair")
                
                # Eğer repair varsa ve başarılı şekilde oluşturulduysa ekle
                if repair and repair.get("success"):
                    solution = repair.get("solution", {})
                    if solution.get("command"):
                        repairs.append(repair)
                
                # Reboot gerekli sorunları işaretle
                if action == "reboot_and_reconfigure_virtualbox":
                    reboot_needed = True

        if not repairs and not reboot_needed:
            QMessageBox.information(
                self,
                "Onarım",
                "Uygulanabilir otomatik çözüm bulunmuyor."
            )
            return

        # Bildiri oluştur
        msg = f"Bulduğum sorunlar:\n"
        if reboot_needed:
            msg += "• Sistem yeniden başlatılması gerekiyor\n"
        if repairs:
            msg += f"• {len(repairs)} otomatik onarım uygulanacak\n"
        msg += "\nDevam etmek istiyor musunuz?"

        answer = QMessageBox.question(
            self,
            "Çözüm Önerileri",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        # Onarımları background thread'de çalıştır
        if hasattr(self, 'repair_thread') and self.repair_thread:
            return

        self.repair_thread = QThread()
        self.repair_worker = BulkRepairWorker(repairs, reboot_needed)
        self.repair_worker.moveToThread(self.repair_thread)

        self.repair_thread.started.connect(self.repair_worker.run)
        self.repair_worker.progress_changed.connect(self.repair_progress_update)
        self.repair_worker.result_ready.connect(self.bulk_repair_finished)
        self.repair_worker.error_occurred.connect(self.worker_error)
        self.repair_worker.finished.connect(self.repair_thread.quit)
        self.repair_worker.finished.connect(self.repair_worker.deleteLater)
        self.repair_thread.finished.connect(self.repair_thread.deleteLater)
        self.repair_thread.finished.connect(self.repair_thread_done)

        self.scan_btn.setEnabled(False)
        self.bulk_repair_btn.setEnabled(False)
        self.repair_thread.start()

    def repair_progress_update(self, value, message):
        self.progress.setValue(value)
        self.log.append(f"[{value:03d}%] {message}")

    def bulk_repair_finished(self, data):
        if data.get("success"):
            QMessageBox.information(
                self,
                "Tamamlandı",
                f"Başarılı: {data.get('successful', 0)}, Başarısız: {data.get('failed', 0)}"
            )
        else:
            QMessageBox.warning(
                self,
                "Hata",
                data.get("message", "Onarım işlemi başarısız oldu.")
            )

    def repair_thread_done(self):
        self.repair_thread = None
        self.repair_worker = None
        self.scan_btn.setEnabled(True)
        self.bulk_repair_btn.setEnabled(True)

    def worker_error(self, message):
        self.log.append(f"[HATA] {message}")
        QMessageBox.warning(self, "Hata", message)


if __name__ == "__main__":
    app = QApplication([])
    window = AppWindow()
    window.show()
    app.exec_()
