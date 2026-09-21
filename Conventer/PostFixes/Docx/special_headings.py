"""Смена стиля спецзаголовков (СТП 01-2024, п. 2.1.1).

СТП требует: названия ненумерованных разделов (ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ,
СОДЕРЖАНИЕ, ...) и приложений выравниваются по центру, без абзацного
отступа. В reference.docx для этого есть стиль SpecialHeading.

Pandoc не умеет надёжно применять custom-style к заголовкам,
поэтому стиль меняем здесь.
"""

from __future__ import annotations

from docx import Document

from ._ooxml import is_heading
from ._tracker import SectionTracker
from .base import DocxFix, FixContext, FixResult


class FixSpecialHeadings(DocxFix):
    name = "special_headings"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        try:
            target_style = doc.styles[ctx.special_style_name]
        except KeyError:
            result.details["reason"] = (
                f"стиль {ctx.special_style_name!r} не найден"
            )
            return result

        for para, sec in SectionTracker(doc, ctx):
            if sec.kind not in ("special", "appendix"):
                continue
            if not is_heading(para, 1):
                continue
            if para.style == target_style:
                result.skipped += 1
                continue
            para.style = target_style
            result.changes += 1

        return result