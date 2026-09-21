"""Конвертер Markdown → DOCX по СТП 01-2024 (БГУИР).

Тонкий наследник DocxConverter. Всё знание о стандарте собрано
в templates.stp2024_BSUIR.STP2024.

    STP2024 — DEFAULT_TEMPLATE этого класса.

По умолчанию экземпляр берёт STP2024, но можно передать другой
Template в конструктор:

    conv = Stp2024Converter()
    conv = Stp2024Converter(other_template)
"""

from __future__ import annotations

from DocxConverter import DocxConverter
from templates.stp2024_BSUIR import STP2024


class Stp2024Converter(DocxConverter):
    """Конвертер по СТП 01-2024."""

    DEFAULT_TEMPLATE = STP2024