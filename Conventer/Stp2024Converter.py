"""Конвертер Markdown → DOCX по СТП 01-2024 (БГУИР).

Настроенная версия DocxConverter: переопределены только TEMPLATE и PRESET.
Вся логика — в DocxConverter и PostFixes.Docx.*.

Это тонкий пресет. Всё разнообразие стандарта (стили, спецзаголовки,
нумерация формул, параметры сносок) уже описано в STP2024 из presets.py.
Если нужно поменять поведение без правки Python-кода — используйте
Stp2024Configurator, который читает config.toml и делает Preset.copy().
"""

from __future__ import annotations

from pathlib import Path

from DocxConverter import DocxConverter, TemplateReference
from PostFixes.Docx import STP2024


class Stp2024Converter(DocxConverter):
    """Конвертер по СТП 01-2024. Готов к использованию без настройки."""

    TEMPLATE = TemplateReference(
        Path(__file__).resolve().parent / "templates" / "stp2024_BSUIR"
    )
    PRESET = STP2024