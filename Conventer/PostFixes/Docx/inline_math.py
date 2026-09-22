"""Межстрочный для абзацев с inline-формулами.

exact обрезает высокие формулы внутри обычного текста. Для таких
абзацев переключаем lineRule на atLeast: значение остаётся 18 pt,
но строка может вырасти под высоту формулы.
"""

from __future__ import annotations

from docx import Document

from ._ooxml import m, w
from .base import DocxFix, FixContext, FixResult


class FixInlineMathSpacing(DocxFix):
    name = "inline_math_spacing"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for para in doc.paragraphs:
            p = para._p

            if not p.findall(".//" + m("oMath")):
                continue

            if p.find(".//" + m("oMathPara")) is not None:
                continue

            pPr = p.find(w("pPr"))
            if pPr is None:
                continue

            sp = pPr.find(w("spacing"))
            if sp is None:
                continue

            if sp.get(w("lineRule")) == "exact":
                sp.set(w("lineRule"), "atLeast")
                result.changes += 1

        return result