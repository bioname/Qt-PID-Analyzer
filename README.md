# Qt-PID-Analyzer

> [English version → README.en.md](README.en.md)

![Qt-PID-Analyzer screenshot](images/screenshot.png)

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


## Структура репозиторію

```raw
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


## Вимоги

- **Python 3.8+** — єдина обов'язкова залежність
- **gcc / make** — тільки для macOS і Linux (збірка `blackbox_decode`)
  - macOS: `xcode-select --install`
  - Linux: `gcc make` (є в будь-якому дистрибутиві)
- **Windows**: gcc не потрібен — `run.py` завантажує готовий `blackbox_decode.exe` автоматично
- **git**: не обов'язковий — можна просто завантажити ZIP з GitHub


## Встановлення та запуск

### Варіант А — через ZIP (найпростіший, git не потрібен)

1. Натисніть **Code → Download ZIP** на [сторінці репозиторію](https://github.com/bioname/Qt-PID-Analyzer)
2. Розпакуйте архів
3. Запустіть:

```bash
python3 run.py          # macOS / Linux
python  run.py          # Windows
```

### Варіант Б — через git

```bash
git clone --recurse-submodules https://github.com/bioname/Qt-PID-Analyzer
cd Qt-PID-Analyzer
python3 run.py
```

---

При **першому запуску** `run.py` автоматично:
- Створює `.venv/` і встановлює всі Python-залежності
- Завантажує `vendor/PID-Analyzer` і `vendor/blackbox-tools` (якщо не клоновано через git)
- **Windows**: завантажує готовий `blackbox_decode.exe` з GitHub Releases
- **macOS / Linux**: збирає `blackbox_decode` з сорців (`gcc` потрібен)
- Перезапускає себе з venv-Python і відкриває вікно

**Кожен наступний** запуск — вікно відкривається одразу.


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


## Використання

| Дія | Результат |
|---|---|
| Drag & drop `.BBL` на ліву панель | Запускає аналіз |
| Клік на сесію в дереві | Відкриває її результати |

| Правий клік на сесію → Delete | Видаляє сесію та файли |```

GPLv3 — успадковано від `blackbox-tools` та оригінального `PID-Analyzer`.



## Субмодулі## Ліцензія



| Субмодуль | Репозиторій | Призначення |

|---|---|---|| `vendor/blackbox-tools` | [cleanflight/blackbox-tools](https://github.com/cleanflight/blackbox-tools) | Декодер `.BBL` → `.CSV` |
| `vendor/PID-Analyzer` | [bioname/PID-Analyzer](https://github.com/bioname/PID-Analyzer) | Python-аналізатор |