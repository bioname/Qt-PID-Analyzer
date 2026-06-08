# Qt-PID-Analyzer

> [English version → README.en.md](README.en.md)

Qt-додаток для аналізу Betaflight blackbox-логів. Обгортка над
[PID-Analyzer](https://github.com/bioname/PID-Analyzer) з графічним інтерфейсом,
деревом попередніх сесій та вбудованим переглядачем результатів.

---

## Що робить програма

1. Ви кидаєте `.BBL` / `.BFL` файл на ліву панель (drag & drop).
2. Програма копіює лог у власне сховище (`data/logs/YYYY-MM-DD/HHMMSS_<ім'я>/`).
3. У фоні запускається `blackbox_decode` → `PID-Analyzer.py`.
4. Результати з'являються на трьох вкладках праворуч:
   - **Noise** — графік шуму
   - **Step Response** — графік відгуку ПІД-регулятора
   - **Log** — текстовий вивід аналізатора

---

## Структура репозиторію

```
Qt-PID-Analyzer/
├── app/
│   ├── main.py          # QApplication + темна палітра
│   ├── mainwindow.py    # головне вікно, splitter
│   ├── log_tree.py      # дерево логів (drag & drop, правий клік → Delete)
│   ├── plot_viewer.py   # три вкладки з результатами
│   ├── worker.py        # QThread — фоновий аналіз
│   └── storage.py       # керування папками сесій
├── vendor/
│   ├── PID-Analyzer/    # git submodule
│   └── blackbox-tools/  # git submodule
├── data/logs/           # сховище результатів (не в git)
├── bin/                 # скомпільований blackbox_decode (не в git)
├── scripts/
│   ├── build_blackbox.sh   # збірка для macOS / Linux
│   ├── build_blackbox.bat  # збірка для Windows (MinGW)
│   └── check_deps.py       # перевірка залежностей без pip
├── run.py               # точка входу
├── requirements.txt
└── pyproject.toml
```

---

## Вимоги

- **Python 3.8+**
- **gcc / make** — для збірки `blackbox_decode` (одноразово)
  - macOS: Xcode Command Line Tools (`xcode-select --install`)
  - Linux: `gcc make` (пакети є в будь-якому дистрибутиві)
  - Windows: MinGW через [MSYS2](https://www.msys2.org/)
- Python-пакети встановлюються автоматично при першому запуску

---

## Встановлення та запуск

```bash
# 1. Клонуємо з субмодулями
git clone --recurse-submodules https://github.com/bioname/Qt-PID-Analyzer
cd Qt-PID-Analyzer

# 2. Збираємо blackbox_decode (одноразово)
./scripts/build_blackbox.sh        # macOS / Linux
# або
scripts\build_blackbox.bat         # Windows (MSYS2 shell)

# 3. Запускаємо
python3 run.py
```

При **першому запуску** `run.py` автоматично:
- Створює `.venv/`
- Встановлює всі залежності через pip
- Перезапускає себе з venv-Python

**Кожен наступний** запуск — вікно відкривається одразу.

---

## Gentoo (без pip)

```bash
# Встановлюємо через portage
emerge dev-python/PyQt6 dev-python/numpy dev-python/scipy \
       dev-python/pandas dev-python/matplotlib dev-python/six

# Запускаємо — bootstrap знайде пакети через system-site-packages
python3 run.py
```

Або перевірте залежності вручну:
```bash
python3 scripts/check_deps.py
```

---

## Використання

| Дія | Результат |
|---|---|
| Drag & drop `.BBL` на ліву панель | Запускає аналіз |
| Клік на сесію в дереві | Відкриває її результати |
| Правий клік на сесію → Delete | Видаляє сесію та файли |

---

## Субмодулі

| Субмодуль | Репозиторій | Призначення |
|---|---|---|
| `vendor/PID-Analyzer` | [bioname/PID-Analyzer](https://github.com/bioname/PID-Analyzer) | Python-аналізатор |
| `vendor/blackbox-tools` | [cleanflight/blackbox-tools](https://github.com/cleanflight/blackbox-tools) | Декодер `.BBL` → `.CSV` |

---

## Ліцензія

GPLv3 — успадковано від `blackbox-tools` та оригінального `PID-Analyzer`.
