import json
import os
import subprocess

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QProgressBar,
    QTextEdit,
    QLineEdit,
    QMessageBox,
    QFrame,
    QScrollArea
)

from app.gui.workers import DiagnosticWorker, RepairWorker
from app.collectors.system import collect_system_info
from app.collectors.hardware import collect_hardware_info


class AppWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pardus Diagnostic Engine")
        self.resize(1200, 760)
        self.setMinimumSize(950, 620)

        self.diagnostic_thread = None
        self.diagnostic_worker = None

        self.repair_thread = None
        self.repair_worker = None

        self.diagnostic_results = []
        self.knowledge_items = []

        self.setStyleSheet(self.style())

        self.build_ui()
        self.load_knowledge()

        # Dashboard her 500 ms güncellenir.
        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.update_dashboard)
        self.system_timer.start(500)

        self.update_dashboard()

    # =========================================================
    # ANA UI
    # =========================================================

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main = QHBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        sidebar = self.build_sidebar()
        main.addWidget(sidebar)

        self.pages = QStackedWidget()

        self.pages.addWidget(self.dashboard_page())
        self.pages.addWidget(self.diagnostic_page())
        self.pages.addWidget(self.repair_page())
        self.pages.addWidget(self.knowledge_page())

        main.addWidget(self.pages)

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(215)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 18)
        layout.setSpacing(8)

        logo = QLabel("PARDUS\nDIAGNOSTIC")
        logo.setObjectName("logo")
        layout.addWidget(logo)

        layout.addSpacing(25)

        buttons = [
            ("Genel Bakış", 0),
            ("Teşhis", 1),
            ("Onarım Merkezi", 2),
            ("Bilgi Tabanı", 3)
        ]

        for text, index in buttons:
            button = QPushButton(text)
            button.setObjectName("nav")
            button.clicked.connect(
                lambda checked=False, i=index:
                self.pages.setCurrentIndex(i)
            )
            layout.addWidget(button)

        layout.addStretch()

        footer = QLabel("Pardus Diagnostic Engine")
        footer.setObjectName("muted")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        return sidebar

    # =========================================================
    # DASHBOARD
    # =========================================================

    def dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(18)

        title = QLabel("Genel Bakış")
        title.setObjectName("title")

        subtitle = QLabel(
            "Sisteminizin mevcut durumu."
        )
        subtitle.setObjectName("muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        cards = QHBoxLayout()
        cards.setSpacing(15)

        self.cpu_card = self.card("CPU", "--")
        self.ram_card = self.card("RAM", "--")
        self.disk_card = self.card("Disk", "--")
        self.kernel_card = self.card("Kernel", "--")

        cards.addWidget(self.cpu_card)
        cards.addWidget(self.ram_card)
        cards.addWidget(self.disk_card)
        cards.addWidget(self.kernel_card)

        layout.addLayout(cards)

        layout.addSpacing(20)

        status = QFrame()
        status.setObjectName("infoCard")

        status_layout = QVBoxLayout(status)

        status_title = QLabel("Sistem Durumu")
        status_title.setObjectName("sectionTitle")

        self.dashboard_status = QLabel(
            "Sistem bilgileri okunuyor..."
        )

        status_layout.addWidget(status_title)
        status_layout.addWidget(self.dashboard_status)

        layout.addWidget(status)

        layout.addStretch()

        return page

    def card(self, title, value):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        name = QLabel(title)
        name.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(name)
        layout.addWidget(value_label)

        card.value = value_label

        return card

    def update_dashboard(self):
        try:
            system = collect_system_info()
            hardware = collect_hardware_info()

            self.cpu_card.value.setText(
                f"{hardware.get('cpu_usage_percent', '--')}%"
            )

            self.ram_card.value.setText(
                f"{hardware.get('ram_used_percent', '--')}%"
            )

            self.disk_card.value.setText(
                f"{hardware.get('disk_used_percent', '--')}%"
            )

            self.kernel_card.value.setText(
                str(system.get("kernel", "--"))
            )

            self.dashboard_status.setText(
                f"İşletim sistemi: {system.get('os', '--')}   |   "
                f"Mimari: {system.get('architecture', '--')}   |   "
                f"CPU çekirdeği: {system.get('cpu_count', '--')}"
            )

        except Exception as exc:
            self.dashboard_status.setText(
                f"Sistem bilgileri alınamadı: {exc}"
            )

    # =========================================================
    # TEŞHİS
    # =========================================================

    def diagnostic_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(14)

        title = QLabel("Teşhis ve Analiz")
        title.setObjectName("title")

        layout.addWidget(title)

        top = QHBoxLayout()

        self.scan_button = QPushButton("Sistemi Tara")
        self.scan_button.setObjectName("primary")
        self.scan_button.clicked.connect(self.start_diagnostic)

        top.addWidget(self.scan_button)
        top.addStretch()

        layout.addLayout(top)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.live_log = QTextEdit()
        self.live_log.setReadOnly(True)
        self.live_log.setObjectName("terminal")
        self.live_log.setMaximumHeight(130)

        layout.addWidget(self.live_log)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QFrame.NoFrame)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(
            self.results_container
        )
        self.results_layout.setAlignment(Qt.AlignTop)

        self.results_scroll.setWidget(
            self.results_container
        )

        layout.addWidget(self.results_scroll)

        next_button = QPushButton("Sonraki Adım →")
        next_button.setObjectName("secondary")
        next_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )

        layout.addWidget(next_button)

        return page

    def start_diagnostic(self):
        if self.diagnostic_thread:
            return

        self.scan_button.setEnabled(False)
        self.progress.setValue(0)
        self.live_log.clear()
        self.clear_layout(self.results_layout)

        self.live_log.append(
            "Sistem taraması başlatılıyor..."
        )

        self.diagnostic_thread = QThread()
        self.diagnostic_worker = DiagnosticWorker()

        self.diagnostic_worker.moveToThread(
            self.diagnostic_thread
        )

        self.diagnostic_thread.started.connect(
            self.diagnostic_worker.run
        )

        self.diagnostic_worker.progress_changed.connect(
            self.update_progress
        )

        self.diagnostic_worker.result_ready.connect(
            self.diagnostic_finished
        )

        self.diagnostic_worker.error_occurred.connect(
            self.worker_error
        )

        self.diagnostic_worker.finished.connect(
            self.diagnostic_thread.quit
        )

        self.diagnostic_worker.finished.connect(
            self.diagnostic_worker.deleteLater
        )

        self.diagnostic_thread.finished.connect(
            self.diagnostic_thread.deleteLater
        )

        self.diagnostic_thread.finished.connect(
            self.diagnostic_thread_done
        )

        self.diagnostic_thread.start()

    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.live_log.append(
            f"[{value:03d}%] {message}"
        )

    def diagnostic_finished(self, data):
        self.diagnostic_results = data.get(
            "results",
            []
        )

        self.show_results()
        self.rebuild_repairs()

        self.live_log.append(
            "Tarama tamamlandı."
        )

    def diagnostic_thread_done(self):
        self.diagnostic_thread = None
        self.diagnostic_worker = None
        self.scan_button.setEnabled(True)

    def show_results(self):
        self.clear_layout(self.results_layout)

        if not self.diagnostic_results:
            label = QLabel("Sorun bulunamadı.")
            label.setObjectName("success")
            self.results_layout.addWidget(label)
            return

        for result in self.diagnostic_results:
            analysis = result["analysis"]
            root = result["root_cause"]
            rule = result["rule"]

            problem = analysis.get(
                "problem",
                "Bilinmeyen sorun"
            )

            category = analysis.get(
                "category",
                "unknown"
            )

            severity = analysis.get(
                "severity",
                "low"
            ).upper()

            confidence = int(
                float(
                    analysis.get(
                        "confidence",
                        0
                    )
                ) * 100
            )

            explanation = root.get(
                "explanation",
                ""
            )

            action = rule.get(
                "action",
                "-"
            )

            card = QFrame()
            card.setObjectName("resultCard")

            box = QVBoxLayout(card)
            box.setContentsMargins(18, 15, 18, 15)
            box.setSpacing(6)

            header = QHBoxLayout()

            problem_label = QLabel(problem)
            problem_label.setObjectName("problem")

            severity_label = QLabel(severity)
            severity_label.setObjectName(
                "severity_" + severity.lower()
            )

            header.addWidget(problem_label)
            header.addStretch()
            header.addWidget(severity_label)

            box.addLayout(header)

            info = QLabel(
                f"Kategori: {category}   •   "
                f"Güven: {confidence}%   •   "
                f"Eylem: {action}"
            )
            info.setObjectName("muted")

            box.addWidget(info)

            if explanation:
                description = QLabel(explanation)
                description.setWordWrap(True)
                box.addWidget(description)

            self.results_layout.addWidget(card)

    # =========================================================
    # ONARIM
    # =========================================================

    def repair_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(16)

        title = QLabel("Onarım Merkezi")
        title.setObjectName("title")

        subtitle = QLabel(
            "Teşhis sonucunda uygulanabilecek onarımlar."
        )
        subtitle.setObjectName("muted")

        self.bulk_repair_button = QPushButton("Tümünü Onar")
        self.bulk_repair_button.setObjectName("primary")
        self.bulk_repair_button.clicked.connect(self.start_bulk_repair)
        self.bulk_repair_button.setEnabled(False)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.bulk_repair_button)

        self.repair_scroll = QScrollArea()
        self.repair_scroll.setWidgetResizable(True)
        self.repair_scroll.setFrameShape(QFrame.NoFrame)

        self.repair_container = QWidget()

        self.repair_layout = QVBoxLayout(
            self.repair_container
        )

        self.repair_layout.setAlignment(Qt.AlignTop)
        self.repair_layout.setSpacing(10)

        self.repair_scroll.setWidget(
            self.repair_container
        )

        layout.addWidget(self.repair_scroll)

        return page

    def rebuild_repairs(self):
        self.clear_layout(self.repair_layout)

        repair_count = 0

        for result in self.diagnostic_results:
            repair = result.get("repair")
            analysis = result["analysis"]
            rule = result["rule"]

            problem = analysis.get(
                "problem",
                "Bilinmeyen sorun"
            )

            action = rule.get("action")

            card = QFrame()
            card.setObjectName("repairCard")

            box = QVBoxLayout(card)
            box.setContentsMargins(18, 14, 18, 14)

            title = QLabel(problem)
            title.setObjectName("problem")
            box.addWidget(title)

            category = QLabel(
                f"{analysis.get('category', '-')}"
                f"  •  {analysis.get('severity', 'low').upper()}"
            )
            category.setObjectName("muted")
            box.addWidget(category)

            if action == "ignore":
                label = QLabel("Gerekli değil")
                label.setObjectName("muted")
                box.addWidget(label)

            elif not repair:
                label = QLabel(
                    "Bu sorun için onarım tanımlanmamış."
                )
                label.setObjectName("muted")
                box.addWidget(label)

            elif not repair.get("success"):
                label = QLabel(
                    "Onarım hazırlanamadı: "
                    + repair.get("error", "Bilinmeyen hata")
                )
                label.setWordWrap(True)
                label.setObjectName("error")
                box.addWidget(label)

            else:
                solution = repair.get(
                    "solution",
                    {}
                )

                description = QLabel(
                    solution.get(
                        "description",
                        "Onarım uygulanabilir."
                    )
                )
                description.setWordWrap(True)
                box.addWidget(description)

                command = solution.get("command")

                if command:
                    repair_count += 1

                    button = QPushButton("Onar")
                    button.setObjectName("repair")
                    button.clicked.connect(
                        lambda checked=False,
                        r=repair:
                        self.start_repair(r)
                    )

                    box.addWidget(
                        button,
                        alignment=Qt.AlignRight
                    )
                else:
                    label = QLabel("Bilgi amaçlı çözüm")
                    label.setObjectName("muted")
                    box.addWidget(label)

            self.repair_layout.addWidget(card)

        if repair_count == 0:
            label = QLabel(
                "Uygulanabilir otomatik onarım bulunmuyor."
            )
            label.setObjectName("muted")
            self.repair_layout.addWidget(label)

        self.bulk_repair_button.setEnabled(repair_count > 0)

    def start_bulk_repair(self):
        repairs = []

        for result in self.diagnostic_results:
            repair = result.get("repair")
            if not repair or not repair.get("success"):
                continue

            rule = result.get("rule", {})
            if rule.get("action") == "ignore":
                continue

            solution = repair.get("solution", {})
            if solution.get("command"):
                repairs.append(repair)

        if not repairs:
            QMessageBox.information(
                self,
                "Onarım",
                "Uygulanabilir otomatik onarım bulunmuyor."
            )
            return

        answer = QMessageBox.question(
            self,
            "Toplu Onarım",
            f"{len(repairs)} adet otomatik onarım uygulanacak.\n\nDevam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        successful = 0
        failed = 0

        for repair in repairs:
            solution = repair.get("solution", {})
            command = solution.get("command", "")

            if not command:
                failed += 1
                continue

            self.live_log.append(f"[TOPLU ONARIM] Komut çalıştırılıyor: {command[:80]}")

            shell_command = command.strip()
            if shell_command.startswith("sudo "):
                shell_command = shell_command[5:]
                process = subprocess.run(
                    ["pkexec", "sh", "-c", shell_command],
                    text=True,
                    capture_output=True,
                )
            else:
                process = subprocess.run(
                    ["sh", "-c", shell_command],
                    text=True,
                    capture_output=True,
                )

            if process.returncode == 0:
                successful += 1
                self.live_log.append("[TOPLU ONARIM] Başarılı.")
            else:
                failed += 1
                self.live_log.append(
                    f"[TOPLU ONARIM] Hata: {process.stderr.strip() or process.stdout.strip() or 'Bilinmeyen hata'}"
                )

        QMessageBox.information(
            self,
            "Toplu Onarım",
            f"İşlem tamamlandı. Başarılı: {successful}, Başarısız: {failed}."
        )

    def start_repair(self, repair):
        solution = repair.get("solution", {})
        command = solution.get("command")

        if not command:
            return

        answer = QMessageBox.question(
            self,
            "Onarım Onayı",
            "Bu işlem sisteminizde değişiklik yapabilir.\n\n"
            "Onarımı başlatmak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        if self.repair_thread:
            return

        self.repair_thread = QThread()
        self.repair_worker = RepairWorker(repair)

        self.repair_worker.moveToThread(
            self.repair_thread
        )

        self.repair_thread.started.connect(
            self.repair_worker.run
        )

        self.repair_worker.progress_changed.connect(
            lambda value, text:
            self.live_log.append(
                f"[ONARIM {value:03d}%] {text}"
            )
        )

        self.repair_worker.result_ready.connect(
            self.repair_finished
        )

        self.repair_worker.error_occurred.connect(
            self.worker_error
        )

        self.repair_worker.finished.connect(
            self.repair_thread.quit
        )

        self.repair_worker.finished.connect(
            self.repair_worker.deleteLater
        )

        self.repair_thread.finished.connect(
            self.repair_thread.deleteLater
        )

        self.repair_thread.finished.connect(
            self.repair_thread_done
        )

        self.repair_thread.start()

    def repair_finished(self, data):
        if data.get("success"):
            QMessageBox.information(
                self,
                "Onarım",
                data.get(
                    "message",
                    "Onarım başarıyla tamamlandı."
                )
            )
        else:
            QMessageBox.warning(
                self,
                "Onarım Başarısız",
                data.get(
                    "message",
                    "Onarım çalıştırılamadı."
                )
            )

    def repair_thread_done(self):
        self.repair_thread = None
        self.repair_worker = None

    # =========================================================
    # BİLGİ TABANI
    # =========================================================

    def knowledge_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(15)

        title = QLabel("Bilgi Tabanı")
        title.setObjectName("title")

        subtitle = QLabel(
            f"Kayıtlı çözüm senaryoları: "
            f"{len(self.knowledge_items)}"
        )
        subtitle.setObjectName("muted")
        self.knowledge_count = subtitle

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Problem, kategori, çözüm veya desen ara..."
        )
        self.search.textChanged.connect(
            self.filter_knowledge
        )

        layout.addWidget(self.search)

        self.knowledge_scroll = QScrollArea()
        self.knowledge_scroll.setWidgetResizable(True)
        self.knowledge_scroll.setFrameShape(QFrame.NoFrame)

        self.knowledge_container = QWidget()

        self.knowledge_layout = QVBoxLayout(
            self.knowledge_container
        )

        self.knowledge_layout.setAlignment(
            Qt.AlignTop
        )

        self.knowledge_scroll.setWidget(
            self.knowledge_container
        )

        layout.addWidget(
            self.knowledge_scroll
        )

        return page

    def load_knowledge(self):
        base = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "knowledge_base"
            )
        )

        if not os.path.isdir(base):
            return

        for filename in sorted(
            os.listdir(base)
        ):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(
                base,
                filename
            )

            try:
                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    data = json.load(file)

                category = filename[:-5]

                if isinstance(data, list):
                    for item in data:
                        entry = dict(item)
                        entry["category"] = category
                        self.knowledge_items.append(entry)

            except Exception:
                pass

        if hasattr(self, "knowledge_count"):
            self.knowledge_count.setText(
                f"Kayıtlı çözüm senaryoları: "
                f"{len(self.knowledge_items)}"
            )

        if hasattr(self, "knowledge_layout"):
            self.filter_knowledge("")

    def filter_knowledge(self, text):
        self.clear_layout(
            self.knowledge_layout
        )

        text = text.lower().strip()

        for entry in self.knowledge_items:
            searchable = " ".join(
                str(v)
                for v in entry.values()
            ).lower()

            if text and text not in searchable:
                continue

            card = QFrame()
            card.setObjectName("knowledgeCard")

            box = QVBoxLayout(card)
            box.setContentsMargins(16, 12, 16, 12)
            box.setSpacing(4)

            problem = QLabel(
                entry.get(
                    "problem",
                    "Bilinmeyen problem"
                )
            )
            problem.setObjectName("problem")

            box.addWidget(problem)

            info = QLabel(
                f"{entry.get('category', '-')}"
                f"  •  "
                f"{entry.get('severity', 'info').upper()}"
            )
            info.setObjectName("muted")
            box.addWidget(info)

            pattern = QLabel(
                f"Desen: {entry.get('pattern', '-')}"
            )
            pattern.setWordWrap(True)
            box.addWidget(pattern)

            solution = QLabel(
                f"Çözüm: {entry.get('solution', '-')}"
            )
            solution.setWordWrap(True)
            box.addWidget(solution)

            self.knowledge_layout.addWidget(card)

    # =========================================================
    # YARDIMCI
    # =========================================================

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def worker_error(self, message):
        self.live_log.append(
            f"[HATA] {message}"
        )

        QMessageBox.warning(
            self,
            "Hata",
            message
        )

    # =========================================================
    # QSS
    # =========================================================

    def style(self):
        return """
        * {
            color: #cdd6f4;
            font-family: "Noto Sans";
        }

        QMainWindow,
        QWidget {
            background: #1e1e2e;
        }

        #sidebar {
            background: #181825;
            border-right: 1px solid #313244;
        }

        #logo {
            color: #cba6f7;
            font-size: 21px;
            font-weight: bold;
        }

        #nav {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px;
            text-align: left;
            color: #bac2de;
            font-size: 14px;
        }

        #nav:hover {
            background: #313244;
            color: #cdd6f4;
        }

        #title {
            color: #cdd6f4;
            font-size: 28px;
            font-weight: bold;
        }

        #sectionTitle {
            color: #cdd6f4;
            font-size: 16px;
            font-weight: bold;
        }

        #muted {
            color: #a6adc8;
        }

        #card,
        #infoCard,
        #resultCard,
        #repairCard,
        #knowledgeCard {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #303548, stop:1 #242a3d);
            border: 1px solid #4d5677;
            border-radius: 12px;
        }

        #knowledgeCard:hover {
            border: 1px solid #cba6f7;
        }

        #card {
            min-height: 105px;
        }

        #cardTitle {
            color: #a6adc8;
            font-size: 13px;
        }

        #cardValue {
            color: #cba6f7;
            font-size: 22px;
            font-weight: bold;
        }

        #primary {
            background: #cba6f7;
            color: #1e1e2e;
            border: none;
            border-radius: 8px;
            padding: 11px 22px;
            font-weight: bold;
        }

        #primary:hover {
            background: #b4befe;
        }

        #secondary {
            background: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 10px 18px;
        }

        #secondary:hover {
            background: #45475a;
        }

        #repair {
            background: #a6e3a1;
            color: #1e1e2e;
            border: none;
            border-radius: 7px;
            padding: 9px 20px;
            font-weight: bold;
        }

        #repair:hover {
            background: #94e2d5;
        }

        #problem {
            color: #cdd6f4;
            font-size: 15px;
            font-weight: bold;
        }

        #severity_critical {
            color: #f38ba8;
            font-weight: bold;
        }

        #severity_high {
            color: #fab387;
            font-weight: bold;
        }

        #severity_medium {
            color: #f9e2af;
            font-weight: bold;
        }

        #severity_low {
            color: #a6e3a1;
            font-weight: bold;
        }

        #terminal {
            background: #11111b;
            color: #a6e3a1;
            border: 1px solid #313244;
            border-radius: 8px;
            font-family: monospace;
        }

        QLineEdit {
            background: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 10px;
        }

        QLineEdit:focus {
            border: 1px solid #cba6f7;
        }

        QProgressBar {
            background: #313244;
            border: none;
            border-radius: 5px;
            height: 9px;
            text-align: center;
        }

        QProgressBar::chunk {
            background: #cba6f7;
            border-radius: 5px;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }

        #success {
            color: #a6e3a1;
            font-size: 16px;
            font-weight: bold;
        }

        #error {
            color: #f38ba8;
        }

        QMessageBox {
            background: #1e1e2e;
        }
        """