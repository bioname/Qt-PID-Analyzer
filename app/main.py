from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from app.mainwindow import MainWindow


def _dark_palette() -> QPalette:
    p = QPalette()
    c = QColor
    p.setColor(QPalette.ColorRole.Window,          c(13,  21,  32))
    p.setColor(QPalette.ColorRole.WindowText,      c(230, 237, 244))
    p.setColor(QPalette.ColorRole.Base,            c(18,  27,  37))
    p.setColor(QPalette.ColorRole.AlternateBase,   c(13,  21,  32))
    p.setColor(QPalette.ColorRole.Text,            c(174, 189, 203))
    p.setColor(QPalette.ColorRole.BrightText,      c(230, 237, 244))
    p.setColor(QPalette.ColorRole.Button,          c(18,  27,  37))
    p.setColor(QPalette.ColorRole.ButtonText,      c(174, 189, 203))
    p.setColor(QPalette.ColorRole.Highlight,       c(77,  143, 196))
    p.setColor(QPalette.ColorRole.HighlightedText, c(13,  21,  32))
    p.setColor(QPalette.ColorRole.Link,            c(77,  143, 196))
    p.setColor(QPalette.ColorRole.Mid,             c(31,  44,  59))
    p.setColor(QPalette.ColorRole.Dark,            c(9,   14,  22))
    p.setColor(QPalette.ColorRole.Shadow,          c(4,   7,   11))
    # Disabled
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       c(80, 100, 120))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, c(80, 100, 120))
    return p


def main() -> None:
    # High-DPI handled automatically in Qt6
    app = QApplication(sys.argv)
    app.setApplicationName("Qt-PID-Analyzer")
    app.setOrganizationName("bioname")
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # Allow running as:  python app/main.py  (from project root)
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
