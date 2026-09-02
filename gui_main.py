import os
import sys

# Development mode: doğrudan dosyadan çalışma
if __package__ in (None, ""):
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from app.gui.simple_app_window import AppWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pardus Diagnostic Engine")

    window = AppWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()