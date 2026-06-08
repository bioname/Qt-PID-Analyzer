# Qt-PID-Analyzer

> [Ukrainian version → README.md](README.md)

A Qt desktop application for analysing Betaflight blackbox logs.
A graphical wrapper around [PID-Analyzer](https://github.com/bioname/PID-Analyzer)
with a session tree, drag-and-drop input and a built-in result viewer.

---

## What it does

1. Drop a `.BBL` / `.BFL` log file onto the left panel.
2. The app copies it into its own storage (`data/logs/YYYY-MM-DD/HHMMSS_<name>/`).
3. `blackbox_decode` and `PID-Analyzer.py` run in a background thread.
4. Results appear in three tabs on the right:
   - **Noise** — noise plot
   - **Step Response** — PID step-response plot
   - **Log** — plain-text analyser output

---

## Repository layout

```
Qt-PID-Analyzer/
├── app/
│   ├── main.py          # QApplication + dark palette
│   ├── mainwindow.py    # main window, splitter
│   ├── log_tree.py      # session tree (drag & drop, right-click Delete)
│   ├── plot_viewer.py   # three-tab result viewer
│   ├── worker.py        # QThread background analysis
│   └── storage.py       # session folder management
├── vendor/
│   ├── PID-Analyzer/    # git submodule
│   └── blackbox-tools/  # git submodule
├── data/logs/           # session storage (not tracked by git)
├── bin/                 # compiled blackbox_decode (not tracked by git)
├── scripts/
│   ├── build_blackbox.sh   # build for macOS / Linux
│   ├── build_blackbox.bat  # build for Windows (MinGW)
│   └── check_deps.py       # pip-free dependency checker
├── run.py               # entry point
├── requirements.txt
└── pyproject.toml
```

---

## Requirements

- **Python 3.8+**
- **gcc / make** — to compile `blackbox_decode` (one-time)
  - macOS: Xcode Command Line Tools (`xcode-select --install`)
  - Linux: `gcc make` (available in any distro)
  - Windows: MinGW via [MSYS2](https://www.msys2.org/)
- Python packages are installed automatically on the first run

---

## Installation & running

```bash
# 1. Clone with submodules
git clone --recurse-submodules https://github.com/bioname/Qt-PID-Analyzer
cd Qt-PID-Analyzer

# 2. Build blackbox_decode (one-time)
./scripts/build_blackbox.sh        # macOS / Linux
# or
scripts\build_blackbox.bat         # Windows (MSYS2 shell)

# 3. Launch
python3 run.py
```

On the **first launch** `run.py` automatically:
- Creates `.venv/`
- Installs all dependencies via pip
- Re-executes itself under the venv Python

Every **subsequent** launch opens the window immediately.

---

## Gentoo (no pip)

```bash
# Install via portage
emerge dev-python/PyQt6 dev-python/numpy dev-python/scipy \
       dev-python/pandas dev-python/matplotlib dev-python/six

# Launch — bootstrap finds packages through system-site-packages
python3 run.py
```

Or check dependencies manually:
```bash
python3 scripts/check_deps.py
```

---

## Usage

| Action | Result |
|---|---|
| Drag & drop `.BBL` onto the left panel | Starts analysis |
| Click a session in the tree | Opens its results |
| Right-click a session → Delete | Removes session and its files |

---

## Submodules

| Submodule | Repository | Purpose |
|---|---|---|
| `vendor/PID-Analyzer` | [bioname/PID-Analyzer](https://github.com/bioname/PID-Analyzer) | Python analyser |
| `vendor/blackbox-tools` | [cleanflight/blackbox-tools](https://github.com/cleanflight/blackbox-tools) | `.BBL` to `.CSV` decoder |

---

## License

GPLv3 — inherited from `blackbox-tools` and the original `PID-Analyzer`.
