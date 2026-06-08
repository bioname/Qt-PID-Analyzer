from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "logs"


def create_session(src_bbl: Path) -> Path:
    """Copy *src_bbl* into a timestamped session folder; return that folder."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_prefix = now.strftime("%H%M%S")
    stem = src_bbl.stem
    session_name = f"{time_prefix}_{stem}"

    session_dir = DATA_DIR / date_str / session_name
    # Guard against same-second collision
    if session_dir.exists():
        i = 2
        while (DATA_DIR / date_str / f"{session_name}_{i}").exists():
            i += 1
        session_dir = DATA_DIR / date_str / f"{session_name}_{i}"

    session_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_bbl, session_dir / src_bbl.name)
    return session_dir


def scan_sessions() -> list[tuple[str, str, str, Path]]:
    """
    Scan DATA_DIR and return sorted list of
    (date_str, time_str "HH:MM:SS", stem, session_dir).
    Newest date first, newest time first within each date.
    """
    results: list[tuple[str, str, str, Path]] = []
    if not DATA_DIR.exists():
        return results

    for date_dir in sorted(DATA_DIR.iterdir(), reverse=True):
        if not date_dir.is_dir():
            continue
        for session_dir in sorted(date_dir.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue
            name = session_dir.name          # e.g. "163255_LOG001"
            parts = name.split("_", 1)
            if len(parts) == 2 and len(parts[0]) == 6 and parts[0].isdigit():
                raw, stem = parts
                time_str = f"{raw[:2]}:{raw[2:4]}:{raw[4:]}"
            else:
                time_str = ""
                stem = name
            results.append((date_dir.name, time_str, stem, session_dir))

    return results


def blackbox_bin() -> Path:
    name = "blackbox_decode.exe" if sys.platform == "win32" else "blackbox_decode"
    return PROJECT_ROOT / "bin" / name


def pid_analyzer_py() -> Path:
    return PROJECT_ROOT / "vendor" / "PID-Analyzer" / "PID-Analyzer.py"
