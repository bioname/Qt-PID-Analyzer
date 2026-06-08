#!/usr/bin/env python3
"""
Check that all runtime dependencies are importable.
Does NOT use pip — works on Gentoo (portage), Arch (pacman),
Debian (apt), macOS (brew/macports), MSYS2/UCRT64, or any venv.

System package hints per distro are printed for missing modules.
"""
from __future__ import annotations
import os
import sys


def _detect_platform() -> str:
    """Return a short platform tag: win32, msys2, darwin, gentoo, arch, debian, linux."""
    if sys.platform == "win32":
        return "win32"
    # MSYS2 sets MSYSTEM env var (UCRT64, MINGW64, CLANG64, …)
    if os.environ.get("MSYSTEM"):
        return "msys2"
    if sys.platform == "darwin":
        return "darwin"
    # Linux — try to detect distro
    try:
        txt = open("/etc/os-release").read().lower()
        if "gentoo" in txt:
            return "gentoo"
        if "arch" in txt or "manjaro" in txt:
            return "arch"
        if "debian" in txt or "ubuntu" in txt or "mint" in txt:
            return "debian"
    except OSError:
        pass
    return "linux"


PLATFORM = _detect_platform()

# MSYS2 UCRT64 package names (pacman -S <name>)
_MSYS2_UCRT = {
    "PyQt6":      "mingw-w64-ucrt-x86_64-python-pyqt6",
    "numpy":      "mingw-w64-ucrt-x86_64-python-numpy",
    "scipy":      "mingw-w64-ucrt-x86_64-python-scipy",
    "pandas":     "mingw-w64-ucrt-x86_64-python-pandas",
    "matplotlib": "mingw-w64-ucrt-x86_64-python-matplotlib",
    "six":        "mingw-w64-ucrt-x86_64-python-six",
}

REQUIRED: list[tuple[str, dict[str, str]]] = [
    ("PyQt6",      {"gentoo": "dev-python/PyQt6",      "debian": "python3-pyqt6",
                    "arch":   "python-pyqt6",           "brew":   "pyqt",
                    "pip":    "PyQt6"}),
    ("numpy",      {"gentoo": "dev-python/numpy",      "debian": "python3-numpy",
                    "arch":   "python-numpy",           "brew":   "numpy",
                    "pip":    "numpy"}),
    ("scipy",      {"gentoo": "dev-python/scipy",      "debian": "python3-scipy",
                    "arch":   "python-scipy",           "brew":   "scipy",
                    "pip":    "scipy"}),
    ("pandas",     {"gentoo": "dev-python/pandas",     "debian": "python3-pandas",
                    "arch":   "python-pandas",          "brew":   "pandas",
                    "pip":    "pandas"}),
    ("matplotlib", {"gentoo": "dev-python/matplotlib", "debian": "python3-matplotlib",
                    "arch":   "python-matplotlib",      "brew":   "matplotlib",
                    "pip":    "matplotlib"}),
    ("six",        {"gentoo": "dev-python/six",        "debian": "python3-six",
                    "arch":   "python-six",             "brew":   "six",
                    "pip":    "six"}),
]

ok: list[str] = []
missing: list[tuple[str, dict[str, str]]] = []

for mod, hints in REQUIRED:
    try:
        __import__(mod)
        ok.append(mod)
    except ImportError:
        missing.append((mod, hints))

print(f"\nPython {sys.version.split()[0]}  ({sys.executable})  [{PLATFORM}]\n")

if ok:
    print("  OK:  " + "  ".join(ok))

if missing:
    print("\n  MISSING packages:\n")
    for mod, hints in missing:
        print(f"    {mod}")
        if PLATFORM == "msys2":
            pkg = _MSYS2_UCRT.get(mod, f"mingw-w64-ucrt-x86_64-python-{mod.lower()}")
            print(f"      MSYS2/UCRT64: pacman -S {pkg}")
        elif PLATFORM in ("win32",):
            print(f"      Windows (pip): pip install {hints['pip']}")
        else:
            if PLATFORM == "gentoo":
                print(f"      Gentoo:   emerge {hints['gentoo']}")
            if PLATFORM in ("debian", "linux"):
                print(f"      Debian:   apt install {hints['debian']}")
            if PLATFORM in ("arch", "linux"):
                print(f"      Arch:     pacman -S {hints['arch']}")
            if PLATFORM == "darwin":
                print(f"      Homebrew: brew install {hints['brew']}")
            print(f"      pip:      pip install {hints['pip']}")
        print()
    sys.exit(1)
else:
    print("\n  All dependencies satisfied.\n")
