"""Корневой фасад пакета PostFixes.

Сейчас единственный подпакет — Docx. При добавлении Xlsx/Pptx
сюда добавятся их реэкспорты.
"""

from .Docx import (
    # База
    DocxFix, PackageFix, FixContext, FixResult, DocxPipeline,
    # Ресурсы
    DocxZipWorkspace, open_docx_zip,
    SectionTracker, SectionContext,
    # Пресеты
    Preset, STP2024,
    # Фиксеры
    FixSpecialHeadings, FixTables, FixLists,
    FixEquationNumbers, FixPageNumbers,
    FixFootnoteMarks, FixFieldUpdates,
)


__all__ = [
    "DocxFix", "PackageFix", "FixContext", "FixResult", "DocxPipeline",
    "DocxZipWorkspace", "open_docx_zip",
    "SectionTracker", "SectionContext",
    "Preset", "STP2024",
    "FixSpecialHeadings", "FixTables", "FixLists",
    "FixEquationNumbers", "FixPageNumbers",
    "FixFootnoteMarks", "FixFieldUpdates",
]