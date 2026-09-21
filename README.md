# ai-dimon

Монорепозиторий для инструментов подготовки документов.

Сейчас реализован один проект — **Conventer**. Остальные части
(MCP-сервер, workflow) — в планах.

## Conventer

Конвертер Markdown → DOCX по стандартам оформления (СТП 01-2024,
ГОСТ 7.32). Собирает `.docx` с правильно оформленными стилями,
заголовками, нумерацией разделов, подписями рисунков и таблиц,
формулами, перечислениями, сносками, номерами страниц и оглавлением.

- [Описание проекта](Conventer/Conventer.md)
- [Инструкция по установке](Conventer/INSTALL.md)
- [CLI](Conventer/Conventer.md#cli)

## Установка

Требуется Python 3.11+ и [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/sha-rdy/ai-dimon.git
cd ai-dimon
uv sync
```

Для работы Conventer дополнительно нужен Pandoc.

macOS:

```bash
brew install pandoc
```

Windows:

```powershell
winget install --id=JohnMacFarlane.Pandoc -e
```

## Использование

Из корня репозитория:

```bash
cd Conventer
uv run python -m cli convert report.md report.docx
```

## Структура

```
ai-dimon/
└── Conventer/        — конвертер Markdown → DOCX
```

## Лицензия

MIT — см. [LICENSE](LICENSE).