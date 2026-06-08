from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal


class AnalysisWorker(QThread):
    progress = pyqtSignal(str)   # status message
    done = pyqtSignal(Path)      # session_dir on success
    error = pyqtSignal(str)      # error message on failure

    def __init__(
        self,
        bbl_path: Path,
        session_dir: Path,
        blackbox_bin: Path,
        analyzer_py: Path,
    ) -> None:
        super().__init__()
        self._bbl = bbl_path
        self._session = session_dir
        self._blackbox = blackbox_bin
        self._analyzer = analyzer_py

    # ------------------------------------------------------------------
    def run(self) -> None:
        log_file = self._session / "analyzer.log"

        # ── Pre-flight checks ──────────────────────────────────────────
        if not self._bbl.exists():
            self.error.emit(f"Log file not found: {self._bbl}")
            return

        if not self._blackbox.exists():
            self.error.emit(
                f"blackbox_decode not found at:\n{self._blackbox}\n\n"
                f"Run first:\n  scripts/build_blackbox.sh  (macOS/Linux)\n"
                f"  scripts\\build_blackbox.bat  (Windows)"
            )
            return

        if not self._analyzer.exists():
            self.error.emit(
                f"PID-Analyzer.py not found at:\n{self._analyzer}\n\n"
                f"Run:  git submodule update --init --recursive"
            )
            return

        # ── Build environment: prepend our bin/ to PATH ────────────────
        env = os.environ.copy()
        env["PATH"] = str(self._blackbox.parent) + os.pathsep + env.get("PATH", "")

        # ── Run PID-Analyzer (it calls blackbox_decode internally) ─────
        cmd = [
            sys.executable,
            str(self._analyzer),
            "--log", str(self._bbl),
            "--name", "result",
            "--blackbox_decode", str(self._blackbox),
            "--show", "N",
        ]

        self.progress.emit(f"Analyzing {self._bbl.name}…")

        try:
            with log_file.open("w", encoding="utf-8") as lf:
                proc = subprocess.run(
                    cmd,
                    cwd=str(self._session),
                    env=env,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    timeout=300,
                )
        except subprocess.TimeoutExpired:
            self.error.emit("Analysis timed out after 5 minutes.")
            return
        except Exception as exc:
            self.error.emit(f"Failed to start analysis:\n{exc}")
            return

        if proc.returncode != 0:
            self.error.emit(
                f"PID-Analyzer exited with code {proc.returncode}.\n"
                f"See Log tab for details."
            )
            # Still emit done so the Log tab shows the error output
            self.done.emit(self._session)
            return

        self.progress.emit("Done.")
        self.done.emit(self._session)
