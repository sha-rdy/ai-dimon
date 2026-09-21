"""Публичный API пакета PostFixes.Docx.

Публичное (стабильное):
  • DocxFix, PackageFix, FixContext, FixResult — базовые типы.
  • DocxPipeline                               — прогон фиксеров.
  • DocxZipWorkspace, open_docx_zip            — для своих PackageFix.
  • SectionTracker, SectionContext             — для своих DocxFix.
  • Preset, STP2024                            — пресеты стандартов.
  • Fix*                                       — готовые фиксеры.

Приватное (меняется без предупреждения):
  • _ooxml, _zip, _tracker — внутренние хелперы.
"""

from ._tracker import SectionContext, SectionTracker
from ._zip import DocxZipWorkspace, open_docx_zip
from .base import DocxFix, FixContext, FixResult, PackageFix
from .equations import FixEquationNumbers
from .field_updates import FixFieldUpdates
from .footnotes import FixFootnoteMarks
from .lists import FixLists
from .page_numbers import FixPageNumbers
from .pipeline import DocxPipeline
from .preset import  Preset
from .special_headings import FixSpecialHeadings
from .tables import FixTables


__all__ = [
    # База
    "DocxFix", "PackageFix", "FixContext", "FixResult", "DocxPipeline",
    # Ресурсы для своих фиксеров
    "DocxZipWorkspace", "open_docx_zip",
    "SectionTracker", "SectionContext",
    # Пресеты
    "Preset",
    # Готовые фиксеры
    "FixSpecialHeadings", "FixTables", "FixLists",
    "FixEquationNumbers", "FixPageNumbers",
    "FixFootnoteMarks", "FixFieldUpdates",
]