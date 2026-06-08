from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QWidget,
)

from app.log_tree import LogTree
from app.plot_viewer import PlotViewer
from app.storage import (
    blackbox_bin,
    create_session,
    pid_analyzer_py,
    scan_sessions,
)
from app.worker import AnalysisWorker

_WIN_STYLE = """
QMainWindow, QWidget#central {
    background: #0d1520;
}
QSplitter::handle {
    background: #1f2c3b;
    width: 2px;
}
QStatusBar {
    background: #121b25;
    color: #5a7a9a;
    font-size: 12px;
    border-top: 1px solid #1f2c3b;
}
QProgressBar {
    background: #1a2738;
    border: none;
    border-radius: 3px;
    height: 4px;
    max-width: 140px;
}
QProgressBar::chunk {
    background: #4d8fc4;
    border-radius: 3px;
}
QMessageBox {
    background: #121b25;
    color: #aebdcb;
}
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Qt-PID-Analyzer")
        self.resize(1280, 800)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(_WIN_STYLE)

        self._worker: AnalysisWorker | None = None
        self._is_busy: bool = False

        # ── Widgets ───────────────────────────────────────────────────
        self._tree = LogTree()
        self._tree.setMinimumWidth(180)
        self._tree.setMaximumWidth(300)

        self._viewer = PlotViewer()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._tree)
        splitter.addWidget(self._viewer)
        splitter.setSizes([220, 1060])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setChildrenCollapsible(False)

        central = QWidget()
        central.setObjectName("central")
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        # ── Status bar ────────────────────────────────────────────────
        self._status_label = QLabel("Ready — drop a .BBL / .BFL log onto the left panel")
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)   # indeterminate
        self._progress.setVisible(False)

        sb: QStatusBar = self.statusBar()
        sb.addWidget(self._status_label, 1)
        sb.addPermanentWidget(self._progress)

        # ── Signals ───────────────────────────────────────────────────
        self._tree.file_dropped.connect(self._on_file_dropped)
        self._tree.session_selected.connect(self._viewer.load_session)
        self._tree.session_deleted.connect(self._on_session_deleted)

        # ── Load existing sessions ────────────────────────────────────
        self._tree.load_sessions(scan_sessions())

    # ── Slots ─────────────────────────────────────────────────────────

    def _on_file_dropped(self, bbl_path: Path) -> None:
        if self._is_busy:
            QMessageBox.warning(
                self, "Busy",
                "An analysis is already running.\nPlease wait for it to finish."
            )
            return
        self._is_busy = True

        session_dir = create_session(bbl_path)
        bbl_copy = session_dir / bbl_path.name

        self._worker = AnalysisWorker(
            bbl_copy,
            session_dir,
            blackbox_bin(),
            pid_analyzer_py(),
        )
        self._worker.progress.connect(self._set_status)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_worker_finished)

        self._progress.setVisible(True)
        self._set_status(f"Analyzing  {bbl_path.name} …")
        self._worker.start()

    def _on_done(self, session_dir: Path) -> None:
        # Parse date / time / stem back out of the session folder name
        date_str = session_dir.parent.name
        parts = session_dir.name.split("_", 1)
        raw = parts[0] if parts else ""
        stem = parts[1] if len(parts) > 1 else session_dir.name
        time_str = f"{raw[:2]}:{raw[2:4]}:{raw[4:]}" if len(raw) == 6 else raw

        self._tree.add_session(date_str, time_str, stem, session_dir)
        self._viewer.load_session(session_dir)
        self._set_status(f"Done — {stem}")

    def _on_worker_finished(self) -> None:
        self._is_busy = False
        self._progress.setVisible(False)

    def _on_error(self, msg: str) -> None:
        self._set_status("Error — see details")
        QMessageBox.critical(self, "Analysis Error", msg)

    def _on_session_deleted(self, _: Path) -> None:
        self._viewer.show_placeholder()

    def _set_status(self, text: str) -> None:
        self._status_label.setText(text)
