"""Конвертер Markdown → DOCX по СТП 01-2024 (БГУИР).

Тонкий наследник DocxConverter. Всё знание о стандарте собрано
в templates.stp2024_BSUIR.STP2024:

    reference.docx, filters/, config.toml  — через Template.directory
    preset                                 — через Template.preset

DocxConverter.__init__ подхватит TEMPLATE.preset в self.PRESET.
Configurator может переопределить self.PRESET для конкретного
экземпляра.
"""

from __future__ import annotations

from DocxConverter import DocxConverter
from templates.stp2024_BSUIR import STP2024


class Stp2024Converter(DocxConverter):
    """Конвертер по СТП 01-2024."""

    TEMPLATE = STP2024