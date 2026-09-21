# Установка Conventer

Инструкция для macOS и Windows. Используется `uv` — быстрый менеджер
пакетов и окружений от Astral, заменяющий `pip`, `venv` и `poetry`.

---

## Содержание

- [Требования](#требования)
- [macOS](#macos)
- [Windows](#windows)
- [Проверка установки](#проверка-установки)
- [Повседневная работа](#повседневная-работа)
- [Управление зависимостями](#управление-зависимостями)
- [Возможные проблемы](#возможные-проблемы)

---

## Требования

- **Python 3.11+** — `uv` установит автоматически.
- **uv** — менеджер пакетов и окружений.
- **Pandoc** — внешний конвертер, ставится отдельно (это не Python-пакет).

`uv` управляет только Python-зависимостями. Pandoc — самостоятельная
программа, её надо поставить руками.

---

## macOS

### 1. Установить `uv`

Через официальный установщик:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Или через Homebrew:

```bash
brew install uv
```

Проверка:

```bash
uv --version
```

Если команда не находится — перезапусти терминал или выполни
`source ~/.zshrc`. Установщик `uv` прописывает PATH в шелл-конфиг.

### 2. Установить Pandoc

```bash
brew install pandoc
```

Если Homebrew нет — скачай `.pkg` с [pandoc.org/installing](https://pandoc.org/installing.html)
и запусти. Или поставь Homebrew: [brew.sh](https://brew.sh/).

Проверка:

```bash
pandoc --version
```

### 3. Синхронизировать окружение проекта

Из корня проекта:

```bash
uv sync
```

`uv` сам:

- поставит нужную версию Python, если её нет;
- создаст `.venv/` в корне проекта;
- установит все зависимости из `pyproject.toml` и `uv.lock`.

### 4. Проверить

```bash
uv run python -m cli list
```

Ожидаемый вывод:

```
Найдено шаблонов: 1

  [stp2024_BSUIR]  СТП 01-2024 (БГУИР)
     reference: ✅   filters: ✅   config: ✅
```

Если вывелось — установка завершена.

---

## Windows

### 1. Установить `uv`

PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Альтернативы:

Через winget:

```cmd
winget install --id=astral-sh.uv -e
```

Через Scoop:

```cmd
scoop install uv
```

Проверка (в **новом** терминале):

```cmd
uv --version
```

Если команда не находится — открой новый PowerShell/CMD. Установщик
обновляет PATH в пользовательских переменных, но текущая сессия
этого не видит.

### 2. Установить Pandoc

Скачай `.msi` с [pandoc.org/installing](https://pandoc.org/installing.html)
и запусти установщик. Он сам пропишет `pandoc` в PATH.

Через winget:

```cmd
winget install --id=JohnMacFarlane.Pandoc -e
```

Через Chocolatey:

```cmd
choco install pandoc
```

Проверка (в **новом** терминале):

```cmd
pandoc --version
```

Если не находит — перезагрузи терминал или компьютер. Pandoc обычно
ставится в `%LOCALAPPDATA%\Pandoc\` и добавляет эту папку в PATH.

### 3. Синхронизировать окружение проекта

Из корня проекта:

```cmd
uv sync
```

Что делает — то же, что и на macOS.

### 4. Проверить

```cmd
uv run python -m cli list
```

Ожидаемый вывод — список найденных шаблонов.

---

## Проверка установки

Три команды, чтобы убедиться, что всё работает:

Список шаблонов:

```bash
uv run python -m cli list
```

Детали шаблона:

```bash
uv run python -m cli info stp2024_BSUIR
```

Конвертация тестового файла:

```bash
uv run python -m cli convert scratch/test.md scratch/out.docx
```

Ожидаемый вывод последней команды — сводка активных фич и
`✅ Готово: .../out.docx`.

---

## Повседневная работа

`uv run` подхватывает виртуальное окружение проекта автоматически.
Активировать `.venv` вручную не нужно.

Конвертация:

```bash
uv run python -m cli convert in.md out.docx
```

Помощь по команде:

```bash
uv run python -m cli convert --help
```

Регенерация `reference.docx` и Lua-фильтров:

```bash
uv run python -m templates.cli generate
```

Проверка `reference.docx` против `spec.py`:

```bash
uv run python -m templates.cli check
```

Тест:

```bash
uv run python scratch/test_convert.py
```

Если всё же хочется активировать окружение вручную:

macOS:

```bash
source .venv/bin/activate
```

Windows:

```cmd
.venv\Scripts\activate
```

Но это не обязательно — `uv run` избавляет от этой привычки.

---

## Управление зависимостями

### Добавить пакет

```bash
uv add pypandoc python-docx lxml tomli
```

`uv` добавит их в `pyproject.toml`, обновит `uv.lock`, синхронизирует
`.venv`. Отдельный `pip install` не нужен.

### Удалить пакет

```bash
uv remove lxml
```

### Обновить всё

```bash
uv lock --upgrade
uv sync
```

### Обновить один пакет

```bash
uv lock --upgrade-package python-docx
uv sync
```

### Dev-зависимости

Если в `pyproject.toml` есть `[dependency-groups]` с группой `dev`:

```bash
uv sync --dev
```

Поставит и runtime, и dev-пакеты (pytest, ruff, mypy и прочее).

### Структура `pyproject.toml`

Ожидаемый вид:

```toml
[project]
name = "conventer"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pypandoc>=1.13",
    "python-docx>=1.1",
    "lxml>=5.0",
    "tomli>=2.0 ; python_version < '3.11'",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

Маркер `; python_version < '3.11'` — PEP 508 environment marker.
`uv` понимает его и ставит `tomli` только когда действительно нужно
(на Python 3.10 и ниже, где `tomllib` ещё нет в стандартной библиотеке).

---

## Возможные проблемы

### `uv: command not found`

macOS:

```bash
source ~/.zshrc
```

Или перезапусти терминал.

Windows: открой **новый** PowerShell или CMD. Установщик обновляет
PATH, но текущая сессия об этом не знает.

### `pandoc not found`

macOS:

Проверь установку:

```bash
which pandoc
```

Если пусто — установи через `brew install pandoc`.

Windows:

```cmd
where pandoc
```

Если пусто — установи `.msi` с pandoc.org и **перезапусти терминал**.
Pandoc не находится в PATH сразу после установки в текущей сессии.

### `Python 3.11+ not found` при `uv sync`

`uv` не нашёл подходящую версию. Форсируй установку:

```bash
uv python install 3.12
```

Затем:

```bash
uv sync
```

### `No solution found when resolving dependencies`

Конфликт версий между пакетами. Что делать:

1. Посмотри в выводе `uv`, какой пакет не разрешается.
2. Ослабь ограничение на него в `pyproject.toml`.
3. Попробуй `uv lock --upgrade` — иногда свежие версии конфликтов не имеют.

### Кириллица в консоли Windows

Если вывод CLI показывает «крякозябры» вместо кириллицы, установи
кодировку:

```cmd
chcp 65001
```

Или запускай через Python-флаг:

```cmd
uv run python -X utf8 -m cli convert scratch/test.md scratch/out.docx
```

На Windows 11 это обычно не нужно — там UTF-8 по умолчанию.

### `PermissionError: [Errno 13]` при `uv sync`

Скорее всего `.venv/` создан с правами другого пользователя (например,
до этого запускался от администратора). Удали и пересоздай:

macOS:

```bash
rm -rf .venv
uv sync
```

Windows:

```cmd
rmdir /s /q .venv
uv sync
```

### Кэш `uv` занимает много места

`uv` кэширует все скачанные пакеты и версии Python. Размер может
достигать нескольких гигабайт. Очистить:

```bash
uv cache clean
```

Проверить размер:

```bash
uv cache dir
```

---

## Краткая шпаргалка

macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
brew install pandoc
cd /путь/к/Conventer
uv sync
uv run python -m cli list
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
winget install --id=JohnMacFarlane.Pandoc -e
cd C:\путь\к\Conventer
uv sync
uv run python -m cli list
```

Дальше — `uv run python -m cli convert ...` для конвертации,
`uv run python -m templates.cli generate` для регенерации шаблона.