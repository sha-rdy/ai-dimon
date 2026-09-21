"""Типы документов: Base, Markdown, Docx.

Постобработка DOCX (нумерация формул, спецзаголовки, таблицы, списки,
сноски) живёт в PostFixes.Docx — см. PostFixes/__init__.py.
"""

from .BaseDoc import BaseDocument
from .DocxDoc import DocxDocument
from .MarkdownDoc import MarkdownDocument

__all__ = ["BaseDocument", "MarkdownDocument", "DocxDocument"]