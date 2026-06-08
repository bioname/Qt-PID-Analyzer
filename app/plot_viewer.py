from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

_TAB_STYLE = """
QTabWidget::pane {
    border: none;
    background: #0d1520;
}
QTabBar::tab {
    background: #121b25;
    color: #7a93aa;
    padding: 7px 22px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}
QTabBar::tab:selected {
    color: #e6edf4;
    border-bottom: 2px solid #4d8fc4;
    background: #0d1520;
}
QTabBar::tab:hover:!selected {
    color: #aebdcb;
    background: #1a2738;
}
"""


class _ScaledImageLabel(QLabel):
    """QLabel that scales its pixmap to fit, keeping aspect ratio."""

    def __init__(self) -> None:
        super().__init__()
        self._source: QPixmap | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: #0d1520; color: #3a5570;")
        self.setText("No data — drop a .BBL log to begin")
        self.setMinimumSize(1, 1)

    def set_source(self, pix: QPixmap) -> None:
        self._source = pix
        self.setText("")
        self._refresh()

    def clear_image(self, msg: str = "") -> None:
        self._source = None
        super().clear()
        self.setText(msg)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if self._source and not self._source.isNull():
            scaled = self._source.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)


def _image_tab() -> tuple[QWidget, _ScaledImageLabel]:
    label = _ScaledImageLabel()
    container = QWidget()
    container.setStyleSheet("background: #0d1520;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(label)
    return container, label


class PlotViewer(QTabWidget):
    """
    Three tabs:
      0 — PID Response  (PNG scaled to fit)
      1 — Noise         (PNG scaled to fit)
      2 — Log           (plain text, monospace)
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(_TAB_STYLE)
        self.setDocumentMode(True)

        container_noise, self._lbl_noise = _image_tab()
        container_response, self._lbl_response = _image_tab()

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setPlaceholderText("Analyzer log will appear here after processing…")
        self._log_view.setStyleSheet(
            "QPlainTextEdit {"
            "  background: #0d1520;"
            "  color: #8bb8d4;"
            "  font-family: 'Menlo', 'Consolas', monospace;"
            "  font-size: 12px;"
            "  border: none;"
            "  padding: 8px;"
            "}"
        )

        self.addTab(container_noise,    "Noise")
        self.addTab(container_response, "Step Response")
        self.addTab(self._log_view,     "Log")

    # ── Public API ────────────────────────────────────────────────────

    def load_session(self, session_dir: Path) -> None:
        """Load all outputs for the given session folder."""
        pngs = list(session_dir.rglob("*.png"))
        noise_png    = next((p for p in pngs if p.name.endswith("_noise.png")),    None)
        response_png = next((p for p in pngs if p.name.endswith("_response.png")), None)
        self._load_png(self._lbl_noise,    noise_png)
        self._load_png(self._lbl_response, response_png)
        self._load_log(session_dir / "analyzer.log")

    def show_placeholder(self) -> None:
        self._lbl_noise.clear_image("No data — drop a .BBL log to begin")
        self._lbl_response.clear_image("No data — drop a .BBL log to begin")
        self._log_view.clear()

    # ── Internals ─────────────────────────────────────────────────────

    def _load_png(self, label: _ScaledImageLabel, path: Path | None) -> None:
        if path is None or not path.exists():
            label.clear_image("Image not found")
            return
        pix = QPixmap(str(path))
        if pix.isNull():
            label.clear_image(f"Cannot load: {path.name}")
            return
        label.set_source(pix)

    def _load_log(self, path: Path) -> None:
        if path.exists():
            self._log_view.setPlainText(
                path.read_text(encoding="utf-8", errors="replace")
            )
        else:
            self._log_view.setPlainText("No log file found.")
