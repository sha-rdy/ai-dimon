"""Корневой фасад пакета PostFixes.

Сейчас единственный подпакет — Docx. При добавлении Xlsx/Pptx
сюда добавятся их реэкспорты.
"""

from .Docx import (
    DocxFix, PackageFix, FixContext, FixResult, DocxPipeline,
    DocxZipWorkspace, open_docx_zip,
    SectionTracker, SectionContext,
    Preset,
    FixSpecialHeadings, FixTables, FixLists,
    FixEquationNumbers, FixPageNumbers,
    FixFootnoteMarks, FixFieldUpdates,
)


__all__ = [
    "DocxFix", "PackageFix", "FixContext", "FixResult", "DocxPipeline",
    "DocxZipWorkspace", "open_docx_zip",
    "SectionTracker", "SectionContext",
    "Preset",
    "FixSpecialHeadings", "FixTables", "FixLists",
    "FixEquationNumbers", "FixPageNumbers",
    "FixFootnoteMarks", "FixFieldUpdates",
]