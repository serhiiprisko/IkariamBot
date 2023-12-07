import sys

from PyQt6.QtWidgets import QApplication

from widget import Widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.showMaximized()
    sys.exit(app.exec())
