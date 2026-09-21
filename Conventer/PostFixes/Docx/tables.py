"""Autofit таблиц на 100% ширины.

Pandoc ставит жёсткие <w:gridCol> и <w:tcW>, из-за чего Word ломает
слова при узких колонках. Снимаем ограничения, ставим autofit + 100%.
"""

from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._ooxml import w
from .base import DocxFix, FixContext, FixResult


class FixTables(DocxFix):
    name = "tables"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)
        for table in doc.tables:
            _fix_one(table)
            result.changes += 1
        return result


def _fix_one(table) -> None:
    tbl = table._tbl
    tblPr = tbl.find(w("tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    for tag in ("tblW", "tblLayout"):
        old = tblPr.find(w(tag))
        if old is not None:
            tblPr.remove(old)

    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), "5000")
    tblW.set(qn("w:type"), "pct")
    tblPr.append(tblW)

    tblLayout = OxmlElement("w:tblLayout")
    tblLayout.set(qn("w:type"), "autofit")
    tblPr.append(tblLayout)

    grid = tbl.find(w("tblGrid"))
    if grid is not None:
        for col in grid.findall(w("gridCol")):
            grid.remove(col)

    for tc in tbl.iter(w("tc")):
        tcPr = tc.find(w("tcPr"))
        if tcPr is None:
            continue
        old = tcPr.find(w("tcW"))
        if old is not None:
            tcPr.remove(old)
        tcW = OxmlElement("w:tcW")
        tcW.set(qn("w:w"), "0")
        tcW.set(qn("w:type"), "auto")
        tcPr.append(tcW)