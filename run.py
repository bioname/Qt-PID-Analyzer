#!/usr/bin/env python3
"""
Top-level launcher — run from the project root: python run.py

On first run:
  1. Creates .venv/ next to this file (if absent)
  2. Installs all required packages into it via pip
     If pip is unavailable (e.g. Gentoo without ensurepip), prints
     per-distro install hints and exits gracefully.
  3. Re-executes this script using the venv Python
     On Windows: uses subprocess instead of os.execv (no execv on Win32).
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

# Per-package install hints for systems without pip
_HINTS: dict[str, dict[str, str]] = {
    "PyQt6":      {"gentoo": "dev-python/PyQt6",      "debian": "python3-pyqt6",      "arch": "python-pyqt6"},
    "numpy":      {"gentoo": "dev-python/numpy",      "debian": "python3-numpy",      "arch": "python-numpy"},
    "scipy":      {"gentoo": "dev-python/scipy",      "debian": "python3-scipy",      "arch": "python-scipy"},
    "pandas":     {"gentoo": "dev-python/pandas",     "debian": "python3-pandas",     "arch": "python-pandas"},
    "matplotlib": {"gentoo": "dev-python/matplotlib", "debian": "python3-matplotlib", "arch": "python-matplotlib"},
    "six":        {"gentoo": "dev-python/six",        "debian": "python3-six",        "arch": "python-six"},
}


# ── Figure out the venv Python / pip executable paths ────────────────────────
def _venv_python() -> Path:
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"

def _venv_pip() -> Path:
    if sys.platform == "win32":
        return VENV / "Scripts" / "pip.exe"
    return VENV / "bin" / "pip"


# ── Are we already running inside the venv? ───────────────────────────────────
def _in_venv() -> bool:
    venv_env = os.environ.get("VIRTUAL_ENV")
    if venv_env and Path(venv_env).resolve() == VENV.resolve():
        return True
    return Path(sys.prefix).resolve() == VENV.resolve()


# ── Print distro hints when pip is not available ──────────────────────────────
def _print_no_pip_hints() -> None:
    print("\n[run.py] ERROR: pip is not available in the virtual environment.", file=sys.stderr)
    print("[run.py] Install the following packages using your system package manager:\n",
          file=sys.stderr)
    for pkg, hints in _HINTS.items():
        print(f"  {pkg}", file=sys.stderr)
        print(f"    Gentoo : emerge {hints['gentoo']}", file=sys.stderr)
        print(f"    Debian : apt install {hints['debian']}", file=sys.stderr)
        print(f"    Arch   : pacman -S {hints['arch']}", file=sys.stderr)
    print("\n[run.py] Then run:  python run.py  again.", file=sys.stderr)


# ── Re-execute this script with a different Python ────────────────────────────
def _reexec(venv_py: Path) -> None:
    """Replace current process with venv python (Unix) or spawn+wait (Windows)."""
    os.environ["VIRTUAL_ENV"] = str(VENV)
    if sys.platform == "win32":
        # os.execv works on Windows but does not replace the process cleanly in
        # all shell environments; subprocess + sys.exit is more reliable there.
        result = subprocess.run(
            [str(venv_py), __file__] + sys.argv[1:],
            env=os.environ,
        )
        sys.exit(result.returncode)
    else:
        os.execv(str(venv_py), [str(venv_py), __file__] + sys.argv[1:])


# ── Bootstrap: create venv + install deps, then re-exec ──────────────────────
def _bootstrap() -> None:
    venv_py = _venv_python()

    # 1. Create venv if absent
    if not venv_py.exists():
        print("[run.py] Creating virtual environment in .venv/ …", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        print("[run.py] Virtual environment created.", flush=True)

    # 2. Check pip is available inside the venv
    pip_check = subprocess.run(
        [str(venv_py), "-m", "pip", "--version"],
        capture_output=True,
    )
    if pip_check.returncode != 0:
        _print_no_pip_hints()
        sys.exit(1)

    # 3. Install / verify packages
    print("[run.py] Installing / verifying dependencies …", flush=True)
    result = subprocess.run(
        [str(venv_py), "-m", "pip", "install", "--quiet", "--upgrade", *PACKAGES],
    )
    if result.returncode != 0:
        print("[run.py] ERROR: pip install failed. Check your internet connection.",
              file=sys.stderr)
        sys.exit(result.returncode)
    print("[run.py] Dependencies OK.", flush=True)

    # 4. Re-exec into venv
    _reexec(venv_py)


# ── Main entry point ──────────────────────────────────────────────────────────
if not _in_venv():
    _bootstrap()
    sys.exit(0)   # unreachable after execv/reexec, satisfies linters

sys.path.insert(0, str(ROOT))
from app.main import main
main()

from app.main import main
main()


