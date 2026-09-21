# Conventer

Конвертер Markdown → DOCX по стандартам оформления (СТП 01-2024, ГОСТ 7.32, …)
на базе [Pandoc](https://pandoc.org/) и python-docx.

Проект собирает из `.md` готовый `.docx` с правильно оформленными:

- стилями абзацев (шрифт, отступы, межстрочный);
- заголовками и нумерацией разделов;
- подписями рисунков и таблиц;
- нумерацией формул;
- перечислениями;
- сносками;
- номерами страниц;
- оглавлением (обновляется в Word).

---

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Структура проекта](#структура-проекта)
- [Как это работает](#как-это-работает)
- [CLI](#cli)
- [Шаблоны](#шаблоны)
- [Добавление нового стандарта](#добавление-нового-стандарта)
- [Разработка](#разработка)
- [Установка](#установка)

---

## Быстрый старт

Проект использует [`uv`](https://docs.astral.sh/uv/) — менеджер пакетов
и окружений от Astral. Он заменяет `pip`, `venv` и `poetry` и сам
ставит нужную версию Python.

### Требования

- **Python 3.11+** — `uv` установит автоматически.
- **uv** — менеджер пакетов и окружений.
- **Pandoc** — внешний конвертер, ставится отдельно (это не Python-пакет).

Подробная установка с командами для macOS и Windows — в [INSTALL.md](INSTALL.md).

Кратко:

macOS:

```bash
brew install uv pandoc
```

Windows (PowerShell + winget):

```powershell
winget install --id=astral-sh.uv -e
winget install --id=JohnMacFarlane.Pandoc -e
```

### Синхронизация окружения

Из корня проекта:

```bash
uv sync
```

`uv` создаст `.venv/`, поставит нужную версию Python и все зависимости
из `pyproject.toml` и `uv.lock`.

### Конвертация

```bash
uv run python -m cli convert report.md report.docx
```

Если в проекте ровно один шаблон — он подхватится сам. Если несколько —
укажите явно:

```bash
uv run python -m cli convert report.md report.docx --template stp2024_BSUIR
```

### Проверка окружения

Список шаблонов:

```bash
uv run python -m cli list
```

Детали активного шаблона:

```bash
uv run python -m cli info
```

`uv run` подхватывает виртуальное окружение проекта автоматически.
Активировать `.venv` вручную не нужно.

---

## Структура проекта

```
Conventer/
├── cli.py                      ← CLI конвертера
├── DocxConverter.py            ← универсальный конвертер
├── DocxConfigurator.py         ← настройка конвертера из config.toml
├── Stp2024Converter.py         ← тонкий наследник под СТП 01-2024
├── Stp2024Configurator.py      ← удобная фабрика для СТП
├── IConverter.py               ← интерфейс конвертера
├── pyproject.toml              ← зависимости и метаданные проекта
├── uv.lock                     ← lock-файл uv
│
├── DocumentTypes/              ← типы документов
│   ├── BaseDoc.py
│   ├── MarkdownDoc.py
│   └── DocxDoc.py
│
├── PostFixes/                  ← постобработка DOCX
│   └── Docx/
│       ├── base.py             ← DocxFix, PackageFix, FixContext, FixResult
│       ├── pipeline.py         ← прогон фиксеров за один open/save
│       ├── preset.py           ← тип Preset
│       ├── special_headings.py ← смена стиля спецзаголовков
│       ├── tables.py           ← autofit таблиц
│       ├── lists.py            ← маркеры перечислений
│       ├── equations.py        ← нумерация формул
│       ├── page_numbers.py     ← номера страниц
│       ├── footnotes.py        ← скобка после знака сноски
│       ├── field_updates.py    ← автообновление полей
│       ├── _ooxml.py           ← OOXML-хелперы
│       ├── _tracker.py         ← SectionTracker
│       └── _zip.py             ← DocxZipWorkspace
│
└── templates/                  ← шаблоны стандартов
    ├── _core/                  ← ядро: типы, генератор, чекер, Template
    ├── cli.py                  ← CLI шаблонов
    └── stp2024_BSUIR/
        ├── __init__.py         ← STP2024 = Template(...)
        ├── spec.py             ← стили reference.docx
        ├── preset.py           ← фиксеры и FixContext
        ├── config.toml         ← параметры постобработки
        ├── filters_src/        ← шаблоны Lua-фильтров с $placeholder
        ├── filters/            ← генерируется
        └── reference.docx      ← генерируется
```

---

## Как это работает

```
Markdown ──► Pandoc ──► DOCX ──► PostFixes ──► Готовый DOCX
              │           │         │
              │           │         └─ python-docx: стили, таблицы, формулы,
              │           │            списки, номера страниц
              │           │
              │           └─ Lua-фильтры: нумерация разделов, подписи
              │              рисунков и таблиц, ПРОПИСНЫЕ H1
              │
              └─ reference.docx: стили абзацев и поля страницы
```

### Три источника правды

1. **`templates/<standard>/spec.py`** — стили и поля страницы.
   Из него генерируется `reference.docx`.
2. **`templates/<standard>/config.toml`** — параметры постобработки
   и семантика (список спецразделов, префикс приложений).
3. **`templates/<standard>/filters_src/*.lua`** — шаблоны Lua-фильтров.
   Из них генерируются `filters/*.lua` с подставленными значениями
   из `config.toml`.

### Пайплайн постобработки

```
DocxPipeline.run(path):

  ┌─ DocxFix-ы (python-docx) ──────────────────────┐
  │  1. Document(path)                    open     │
  │  2. FixSpecialHeadings                         │
  │  3. FixTables                                  │
  │  4. FixLists                                   │
  │  5. FixEquationNumbers                         │
  │  6. FixPageNumbers                             │
  │  7. Document.save(path)               save     │
  └────────────────────────────────────────────────┘

  ┌─ PackageFix-ы (zip) ───────────────────────────┐
  │  8. open_docx_zip(path)              unpack    │
  │  9. FixFootnoteMarks                           │
  │ 10. FixFieldUpdates                            │
  │ 11. __exit__: repack только если mark_dirty()  │
  └────────────────────────────────────────────────┘
```

- Один **open** и один **save** на всю python-docx-фазу.
- Один **unpack** и один **repack** на всю zip-фазу.
- Если ни один фикс не пометил workspace грязным — файл не перепаковывается.
- Если падение — оригинал не тронут (атомарная запись через `os.replace`).

---

## CLI

### Команды

Список шаблонов:

```bash
uv run python -m cli list
```

Детали шаблона:

```bash
uv run python -m cli info stp2024_BSUIR
```

Конвертация:

```bash
uv run python -m cli convert in.md out.docx
```

### Параметры `convert`

| Параметр | Значение |
|---|---|
| `input` | входной Markdown-файл |
| `output` | выходной DOCX-файл |
| `--template`, `-t` | имя шаблона (если их несколько) |
| `--config`, `-c` | путь к `config.toml` |
| `--no-config` | не применять `config.toml` (дефолты пресета) |
| `--toc` | включить оглавление |
| `--no-toc` | выключить оглавление |
| `--toc-depth N` | глубина оглавления |
| `--toc-title S` | заголовок оглавления |
| `-v`, `--verbose` | печатать работу каждого фиксера |
| `-q`, `--quiet` | не печатать ничего, кроме ошибок |

### Примеры

Простой прогон:

```bash
uv run python -m cli convert report.md report.docx
```

С подробным логом:

```bash
uv run python -m cli convert report.md report.docx -v
```

Без оглавления:

```bash
uv run python -m cli convert report.md report.docx --no-toc
```

С кастомным config.toml:

```bash
uv run python -m cli convert report.md report.docx --config /tmp/custom.toml
```

Дефолты пресета, игнорируя config.toml:

```bash
uv run python -m cli convert report.md report.docx --no-config
```

---

## Шаблоны

Шаблон — это папка `templates/<name>/`, описывающая всё о стандарте.

### CLI шаблонов

Список всех найденных шаблонов:

```bash
uv run python -m templates.cli list
```

Детали конкретного шаблона:

```bash
uv run python -m templates.cli info stp2024_BSUIR
```

Сгенерировать reference.docx и Lua-фильтры для всех шаблонов:

```bash
uv run python -m templates.cli generate
```

Для одного шаблона:

```bash
uv run python -m templates.cli generate stp2024_BSUIR
```

Только reference.docx, без фильтров:

```bash
uv run python -m templates.cli generate --no-filters
```

Проверка reference.docx:

```bash
uv run python -m templates.cli check stp2024_BSUIR
```

### Что генерируется

- **`reference.docx`** — из `spec.py` через `TemplateGenerator`.
  Содержит стили (Normal, Heading1-3, Caption, …) и параметры секции.
- **`filters/*.lua`** — из `filters_src/*.lua` через `generate_filters`.
  В шаблоны подставляются значения из `config.toml`.

### Что проверяется

`TemplateChecker` сверяет `reference.docx` с `spec.py`:
поля страницы, наличие стилей, шрифты, отступы, межстрочные.
Полезно в CI — ловит рассинхрон между кодом и файлом.

---

## Добавление нового стандарта

Пошагово на примере ГОСТ 7.32.

### 1. Создать папку

macOS:

```bash
mkdir -p templates/gost732/filters_src
```

Windows:

```powershell
mkdir templates\gost732\filters_src
```

### 2. Написать `spec.py`

```python
from templates._core import Align, SectionSpec, StyleSpec, TemplateSpec

GOST732_SPEC = TemplateSpec(
    name="ГОСТ 7.32-2017",
    section=SectionSpec(margin_top_mm=20.0, margin_left_mm=30.0, ...),
)

GOST732_SPEC.add(StyleSpec(name="Normal", ...))
GOST732_SPEC.add(StyleSpec(name="Heading1", ...))
# ...
```

### 3. Написать `preset.py`

```python
from PostFixes.Docx import (
    FixContext, FixSpecialHeadings, FixTables, ..., Preset,
)

GOST732_PRESET = Preset(
    name="ГОСТ 7.32-2017",
    ctx=FixContext(special_texts=frozenset({...}), ...),
    docx_fixes=[FixSpecialHeadings(), ...],
    package_fixes=[FixFootnoteMarks(), FixFieldUpdates()],
)
```

### 4. Написать `config.toml`

```toml
[meta]
name = "ГОСТ 7.32-2017"

[headings]
special = ["содержание", "введение", "заключение"]
appendix_prefix = "приложение"
app_letters = "АБВГД..."

[equations]
tab_cm = 16.5

# ... [page_numbers], [toc], [features]
```

### 5. Написать `filters_src/*.lua`

Скопировать из соседнего шаблона и подправить под стандарт.
`$special_lua_table`, `$app_letters_lua_table`, `$appendix_prefix`
подставятся автоматически.

### 6. Создать `__init__.py`

```python
from pathlib import Path
from templates._core import Template
from .preset import GOST732_PRESET
from .spec import GOST732_SPEC

GOST732 = Template(
    name="ГОСТ 7.32-2017",
    directory=Path(__file__).resolve().parent,
    spec=GOST732_SPEC,
    preset=GOST732_PRESET,
)
```

### 7. Сгенерировать артефакты

```bash
uv run python -m templates.cli generate gost732
```

Готово. CLI конвертера подхватит шаблон автоматически.

---

## Разработка

### Тесты

```bash
uv run python scratch/test_convert.py
```

Проверяет:
- наличие `reference.docx`;
- прогон Markdown → DOCX;
- побайтовую идемпотентность постобработки.

### Идемпотентность

Второй прогон pipeline на уже обработанном файле **не меняет** его:

- `DocxFix`-и не пишут `doc.save()`, если `changes == 0`;
- `PackageFix`-ы не пишут в файл, если никто не позвал `ws.mark_dirty()`.

Проверяется через `sha256` до/после.

### Структура PostFixes

- **`DocxFix`** — работает с `python-docx.Document`.
  Реализует `apply(doc, ctx) -> FixResult`.
- **`PackageFix`** — работает с `DocxZipWorkspace`.
  Реализует `apply(ws, ctx) -> FixResult`.
- Все `DocxFix` идут одним блоком (один open/save), затем все
  `PackageFix` — тоже одним блоком (один unpack/repack).
- Порядок фиксеров важен: `FixSpecialHeadings` **до** `FixEquationNumbers`
  (второй распознаёт `SpecialHeading` как H1).

### Расширение

Чтобы добавить свой фикс:

1. Наследуй `DocxFix` или `PackageFix`.
2. Реализуй `apply(...) -> FixResult`, установи `name`.
3. Добавь в `docx_fixes` / `package_fixes` нужного пресета.
4. Не забудь про идемпотентность: перед правкой проверь,
   что она ещё не сделана.

### Добавление зависимостей

Добавить пакет:

```bash
uv add pypandoc python-docx lxml tomli
```

Удалить:

```bash
uv remove lxml
```

Обновить все пакеты:

```bash
uv lock --upgrade
uv sync
```

Обновить один:

```bash
uv lock --upgrade-package python-docx
uv sync
```

### Ключевые инварианты

- **Порядок `pPr`/`rPr`** — через `ppr_insert`/`rpr_insert`. Word не примет файл с нарушением.
- **Атомарность** — `os.replace` в `_zip.py`. Падение не портит оригинал.
- **Идемпотентность** — повторный прогон не меняет файл.
- **Изоляция** — `Preset.copy()` клонирует `ctx.enabled` и списки фиксеров.
  Configurator работает на экземпляре, класс-уровень не трогает.

---

## Установка

Подробная инструкция для macOS и Windows — в [INSTALL.md](INSTALL.md).

Кратко:

macOS:

```bash
brew install uv pandoc
uv sync
```

Windows:

```powershell
winget install --id=astral-sh.uv -e
winget install --id=JohnMacFarlane.Pandoc -e
uv sync
```

---

## Лицензия

См. LICENSE.