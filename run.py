#!/usr/bin/env python3
"""
Top-level launcher — run from the project root: python run.py

On first run:
  1. Creates .venv/ next to this file (if absent)
  2. Installs all required packages into it
  3. Re-executes this script using the venv Python
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"

# ── Packages required by the app ─────────────────────────────────────────────
PACKAGES = [
    "PyQt6",
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "six",
]

# ── Figure out the venv Python executable path ───────────────────────────────
def _venv_python() -> Path:
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


# ── Are we already running inside the venv? ───────────────────────────────────
def _in_venv() -> bool:
    # VIRTUAL_ENV is set by the venv activation AND by re-execv into venv python
    venv_env = os.environ.get("VIRTUAL_ENV")
    if venv_env and Path(venv_env).resolve() == VENV.resolve():
        return True
    # Fallback: compare sys.prefix
    return Path(sys.prefix).resolve() == VENV.resolve()


# ── Bootstrap: create venv + install deps, then re-exec ──────────────────────
def _bootstrap() -> None:
    venv_py = _venv_python()

    if not venv_py.exists():
        print("[run.py] Creating virtual environment in .venv/ …", flush=True)
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV)],
            check=True,
        )
        print("[run.py] Virtual environment created.", flush=True)

    # Always make sure packages are installed (idempotent)
    print("[run.py] Installing / verifying dependencies …", flush=True)
    subprocess.run(
        [str(venv_py), "-m", "pip", "install", "--quiet", "--upgrade", *PACKAGES],
        check=True,
    )
    print("[run.py] Dependencies OK.", flush=True)

    # Re-exec this script with venv Python (set VIRTUAL_ENV so _in_venv() detects it)
    os.environ["VIRTUAL_ENV"] = str(VENV)
    os.execv(str(venv_py), [str(venv_py), __file__] + sys.argv[1:])


# ── Main entry point ──────────────────────────────────────────────────────────
if not _in_venv():
    _bootstrap()
    sys.exit(0)   # unreachable after execv, but satisfies linters

sys.path.insert(0, str(ROOT))
from app.main import main
main()


