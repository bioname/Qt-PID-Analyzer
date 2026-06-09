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


# ── Detect MSYS2 (reports win32 but uses Unix venv layout) ──────────────────────
_IS_MSYS2 = bool(os.environ.get("MSYSTEM"))   # UCRT64 / MINGW64 / CLANG64 …
_IS_WIN_NATIVE = sys.platform == "win32" and not _IS_MSYS2


# ── Figure out the venv Python executable path ─────────────────────────────────
def _venv_python() -> Path:
    # Native Windows: Scripts\python.exe
    # MSYS2 + all Unix: bin/python  (MSYS2 Python uses POSIX venv layout)
    if _IS_WIN_NATIVE:
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


# ── Are we already running inside the venv? ───────────────────────────────────
def _in_venv() -> bool:
    venv_env = os.environ.get("VIRTUAL_ENV")
    if venv_env and Path(venv_env).resolve() == VENV.resolve():
        return True
    return Path(sys.prefix).resolve() == VENV.resolve()


# ── Print distro hints when pip is not available ──────────────────────────────
def _check_missing(venv_py: Path) -> list[str]:
    """Return list of package names not importable inside venv_py."""
    code = (
        "import sys\n"
        + "".join(
            f"try:\n    import {p}\nexcept ImportError:\n    print('{p}')\n"
            for p in PACKAGES
        )
    )
    result = subprocess.run(
        [str(venv_py), "-c", code],
        capture_output=True, text=True,
    )
    return result.stdout.strip().splitlines()


def _print_no_pip_hints(missing: list[str] | None = None) -> None:
    pkgs = missing or list(_HINTS.keys())
    print("\n[run.py] ERROR: pip is not available and some packages are missing.",
          file=sys.stderr)
    print("[run.py] Install the following packages using your system package manager:\n",
          file=sys.stderr)
    for pkg in pkgs:
        hints = _HINTS.get(pkg, {})
        print(f"  {pkg}", file=sys.stderr)
        if hints.get("gentoo"):
            print(f"    Gentoo : emerge {hints['gentoo']}", file=sys.stderr)
        if hints.get("debian"):
            print(f"    Debian : apt install {hints['debian']}", file=sys.stderr)
        if hints.get("arch"):
            print(f"    Arch   : pacman -S {hints['arch']}", file=sys.stderr)
    print("\n[run.py] Then run:  python run.py  again.", file=sys.stderr)


# ── Re-execute this script with a different Python ────────────────────────────
def _reexec(venv_py: Path) -> None:
    """Replace current process with venv python (Unix) or spawn+wait (Windows/MSYS2)."""
    os.environ["VIRTUAL_ENV"] = str(VENV)
    if _IS_WIN_NATIVE or _IS_MSYS2:
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

    # 2. Check pip is available inside the venv; if not, recreate with system packages
    pip_check = subprocess.run(
        [str(venv_py), "-m", "pip", "--version"],
        capture_output=True,
    )
    if pip_check.returncode != 0:
        print("[run.py] pip not found in venv — retrying with --system-site-packages …",
              flush=True)
        import shutil
        shutil.rmtree(str(VENV), ignore_errors=True)
        subprocess.run(
            [sys.executable, "-m", "venv", "--system-site-packages", str(VENV)],
            check=True,
        )
        # Check again — if still no pip, show distro hints and exit
        pip_check2 = subprocess.run(
            [str(venv_py), "-m", "pip", "--version"],
            capture_output=True,
        )
        if pip_check2.returncode != 0:
            # At least check if all needed modules are importable from system packages
            missing = _check_missing(venv_py)
            if not missing:
                print("[run.py] All packages available via system site-packages. OK.",
                      flush=True)
                _reexec(venv_py)
                return
            _print_no_pip_hints(missing)
            sys.exit(1)

    # 3. Install / verify packages
    print("[run.py] Installing / verifying dependencies …", flush=True)
    result = subprocess.run(
        [str(venv_py), "-m", "pip", "install", "--upgrade", *PACKAGES],
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

# ── Submodule check ───────────────────────────────────────────────────────────
def _check_submodules() -> None:
    analyzer = ROOT / "vendor" / "PID-Analyzer" / "PID-Analyzer.py"
    blackbox  = ROOT / "vendor" / "blackbox-tools" / "Makefile"
    missing = []
    if not analyzer.exists():
        missing.append("vendor/PID-Analyzer")
    if not blackbox.exists():
        missing.append("vendor/blackbox-tools")
    if not missing:
        return

    # Check if this is a proper git repository
    if not (ROOT / ".git").exists():
        print("[run.py] ERROR: this does not appear to be a git repository.", file=sys.stderr)
        print("[run.py] You may have downloaded the ZIP instead of cloning.", file=sys.stderr)
        print("[run.py] Please clone with git:", file=sys.stderr)
        print("  git clone --recurse-submodules https://github.com/bioname/Qt-PID-Analyzer",
              file=sys.stderr)
        sys.exit(1)

    # Check git is available
    try:
        git_check = subprocess.run(
            ["git", "--version"],
            capture_output=True,
        )
        git_ok = git_check.returncode == 0
    except FileNotFoundError:
        git_ok = False

    if not git_ok:
        print("[run.py] ERROR: git not found on PATH.", file=sys.stderr)
        print("[run.py] Install git and re-run:", file=sys.stderr)
        print("  Debian/Ubuntu : apt install git", file=sys.stderr)
        print("  Arch          : pacman -S git", file=sys.stderr)
        print("  Gentoo        : emerge dev-vcs/git", file=sys.stderr)
        print("  MSYS2         : pacman -S git", file=sys.stderr)
        print("  macOS         : xcode-select --install", file=sys.stderr)
        print("  Windows       : https://git-scm.com/download/win", file=sys.stderr)
        sys.exit(1)

    print("[run.py] Submodules not initialised — running git submodule update …",
          flush=True)
    result = subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("[run.py] ERROR: git submodule update failed.", file=sys.stderr)
        print("[run.py] Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    # Verify again after clone
    still_missing = []
    if not analyzer.exists():
        still_missing.append("vendor/PID-Analyzer")
    if not blackbox.exists():
        still_missing.append("vendor/blackbox-tools")
    if still_missing:
        print("[run.py] ERROR: submodules still missing after update:", file=sys.stderr)
        for m in still_missing:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)
    print("[run.py] Submodules OK.", flush=True)

    bb_bin = ROOT / "bin" / ("blackbox_decode.exe" if _IS_WIN_NATIVE else "blackbox_decode")
    if not bb_bin.exists():
        print("[run.py] WARNING: blackbox_decode not built yet.", flush=True)
        print("[run.py] Building now …", flush=True)
        if _IS_WIN_NATIVE or _IS_MSYS2:
            build_script = ROOT / "scripts" / "build_blackbox.bat"
            result = subprocess.run([str(build_script)], shell=True)
        else:
            build_script = ROOT / "scripts" / "build_blackbox.sh"
            result = subprocess.run(["bash", str(build_script)])
        if result.returncode != 0:
            print("[run.py] ERROR: build failed — see output above.", file=sys.stderr)
            sys.exit(1)
        print("[run.py] blackbox_decode built OK.", flush=True)

_check_submodules()

sys.path.insert(0, str(ROOT))
from app.main import main
main()

