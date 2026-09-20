"""Постобработка DOCX: убрать фиксированные ширины колонок в таблицах.

Pandoc ставит жёсткие <w:gridCol> и <w:tcW>, из-за чего Word ломает
слова при узких колонках. Снимаем ограничения, ставим autofit + 100%.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def fix_tables(docx_path: Path) -> int:
    """Сделать все таблицы autofit на 100% ширины.

    Возвращает количество обработанных таблиц.
    """
    doc = Document(str(docx_path))
    count = 0

    for table in doc.tables:
        _fix_table(table)
        count += 1

    doc.save(str(docx_path))
    return count


def _fix_table(table) -> None:
    """Настроить одну таблицу: autofit + 100% ширины."""
    tbl = table._tbl
    tblPr = tbl.find(_w("tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    # 1. Убираем старый tblW
    old_w = tblPr.find(_w("tblW"))
    if old_w is not None:
        tblPr.remove(old_w)

    # 2. Ставим 100% ширины
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), "5000")
    tblW.set(qn("w:type"), "pct")
    tblPr.append(tblW)

    # 3. Убираем старый tblLayout
    old_layout = tblPr.find(_w("tblLayout"))
    if old_layout is not None:
        tblPr.remove(old_layout)

    # 4. Autofit
    tblLayout = OxmlElement("w:tblLayout")
    tblLayout.set(qn("w:type"), "autofit")
    tblPr.append(tblLayout)

    # 5. Убираем жёсткие gridCol-ы (Pandoc их задаёт)
    grid = tbl.find(_w("tblGrid"))
    if grid is not None:
        for col in grid.findall(_w("gridCol")):
            grid.remove(col)

    # 6. Убираем жёсткие tcW из ячеек
    for tc in tbl.iter(_w("tc")):
        tcPr = tc.find(_w("tcPr"))
        if tcPr is None:
            continue
        old = tcPr.find(_w("tcW"))
        if old is not None:
            tcPr.remove(old)
        # auto-ширина
        tcW = OxmlElement("w:tcW")
        tcW.set(qn("w:w"), "0")
        tcW.set(qn("w:type"), "auto")
        tcPr.append(tcW)