#!/usr/bin/env python3
"""
Check that all runtime dependencies are importable.
Does NOT use pip — works on Gentoo (portage), Arch (pacman),
Debian (apt), macOS (brew/macports), or any venv.

System package hints per distro are printed for missing modules.
"""
from __future__ import annotations
import sys

REQUIRED: list[tuple[str, dict[str, str]]] = [
    ("PyQt6",     {"gentoo": "dev-python/PyQt6",
                   "debian": "python3-pyqt6",
                   "arch":   "python-pyqt6",
                   "brew":   "pyqt",
                   "pip":    "PyQt6"}),
    ("numpy",     {"gentoo": "dev-python/numpy",
                   "debian": "python3-numpy",
                   "arch":   "python-numpy",
                   "brew":   "numpy",
                   "pip":    "numpy"}),
    ("scipy",     {"gentoo": "dev-python/scipy",
                   "debian": "python3-scipy",
                   "arch":   "python-scipy",
                   "brew":   "scipy",
                   "pip":    "scipy"}),
    ("pandas",    {"gentoo": "dev-python/pandas",
                   "debian": "python3-pandas",
                   "arch":   "python-pandas",
                   "brew":   "pandas",
                   "pip":    "pandas"}),
    ("matplotlib",{"gentoo": "dev-python/matplotlib",
                   "debian": "python3-matplotlib",
                   "arch":   "python-matplotlib",
                   "brew":   "matplotlib",
                   "pip":    "matplotlib"}),
    ("six",       {"gentoo": "dev-python/six",
                   "debian": "python3-six",
                   "arch":   "python-six",
                   "brew":   "six",
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

print(f"\nPython {sys.version.split()[0]}  ({sys.executable})\n")

if ok:
    print("  OK:  " + "  ".join(ok))

if missing:
    print("\n  MISSING packages:\n")
    for mod, hints in missing:
        print(f"    {mod}")
        print(f"      Gentoo:   emerge {hints['gentoo']}")
        print(f"      Debian:   apt install {hints['debian']}")
        print(f"      Arch:     pacman -S {hints['arch']}")
        print(f"      Homebrew: brew install {hints['brew']}")
        print(f"      pip:      pip install {hints['pip']}")
        print()
    sys.exit(1)
else:
    print("\n  All dependencies satisfied.\n")
