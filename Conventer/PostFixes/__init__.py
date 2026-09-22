"""Корневой фасад пакета PostFixes.

Сейчас единственный подпакет — Docx. При добавлении Xlsx/Pptx
сюда добавятся их реэкспорты.
"""

from .Docx import (
    DocxFix, PackageFix, FixContext, FixResult, DocxPipeline,
    DocxZipWorkspace, open_docx_zip,
    SectionTracker, SectionContext,
    Preset,
    FixSpecialHeadings, FixTableLayout,FixTableCells, FixLists,
    FixEquationNumbers, FixPageNumbers,
    FixFootnoteMarks, FixFieldUpdates,FixInlineMathSpacing,FixSourceCodeWrap,FixSourceCodeAlign
)


__all__ = [
    "DocxFix", "PackageFix", "FixContext", "FixResult", "DocxPipeline",
    "DocxZipWorkspace", "open_docx_zip",
    "SectionTracker", "SectionContext",
    "Preset",
    "FixSpecialHeadings", "FixTableLayout","FixTableCells", "FixLists",
    "FixEquationNumbers", "FixPageNumbers",
    "FixFootnoteMarks", "FixFieldUpdates","FixInlineMathSpacing","FixSourceCodeWrap","FixSourceCodeAlign"
]