# Conventer

Конвертер Markdown → DOCX по стандартам оформления (СТП 01-2024, ГОСТ 7.32).

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![uv](https://img.shields.io/badge/managed%20by-uv-purple)](https://docs.astral.sh/uv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

## Что это

Готовит из Markdown-файла `.docx` с правильно оформленными:
стилями, заголовками, нумерацией разделов, подписями рисунков
и таблиц, формулами, перечислениями, сносками, номерами страниц
и оглавлением.

## Установка

Из корня монорепо (после `uv sync`):

macOS:

```bash
brew install pandoc
```

Windows:

```powershell
winget install --id=JohnMacFarlane.Pandoc -e
```

Подробнее — [INSTALL.md](INSTALL.md).

## Использование

```bash
uv run python -m cli convert report.md report.docx
```

Параметры, генерация шаблонов, добавление нового стандарта —
в [полном описании](Conventer.md).

## Документация

- [Conventer.md](Conventer.md) — что это, как работает, CLI, шаблоны
- [INSTALL.md](INSTALL.md) — установка на macOS и Windows

## Лицензия

MIT — см. [../LICENSE](../LICENSE).