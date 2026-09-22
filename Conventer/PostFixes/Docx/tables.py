"""Таблицы: структура и содержимое ячеек.

FixTableLayout  — tblLayout=fixed, ширины колонок по содержимому.
FixTableCells   — jc=left, firstLine=0, lineRule=atLeast в ячейках.

Почему fixed, а не autofit:
  Word и LibreOffice по-разному понимают autofit. Word пересчитывает
  ширины под содержимое, LibreOffice — нет и берёт tblGrid. Pandoc
  генерирует tblGrid неточно, из-за чего таблица в LibreOffice уезжает
  за поля. С fixed оба редактора читают одни и те же twips.

Почему для каждой колонки задан абсолютный минимум в twips:
  Доля «5% от ширины таблицы» даёт 468 twips = 8 мм. Колонка с числом
  «10» требует ~556 twips (340 на текст + 216 на padding). Не влезает,
  Word рвёт «10» на «1» и «0». То же с «6,4612». Минимум в 1100 twips
  решает обе проблемы.
"""

from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._ooxml import (
    get_or_add_pPr,
    get_or_add_tblPr,
    get_or_add_tcPr,
    m,
    ppr_insert,
    w,
)
from .base import DocxFix, FixContext, FixResult


# Доступная ширина: 210 мм − 30 мм − 15 мм = 165 мм = 9355 twips.
_TABLE_WIDTH_TWIPS = 9355

# Абсолютный минимум на колонку. 1200 twips ≈ 21 мм.
_MIN_TWIPS_PER_COL = 1200

# Максимальная доля одной колонки. Чтобы широкая «Ситуация» не резалась.
_MAX_COL_SHARE = 0.60


# ======================================================================
# Структура: layout, ширины
# ======================================================================

class FixTableLayout(DocxFix):
    """tblLayout=fixed + ширины колонок по содержимому."""

    name = "table_layout"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for table in doc.tables:
            if _fix_layout(table):
                result.changes += 1

        return result


def _fix_layout(table) -> bool:
    tbl = table._tbl

    if _has_merged_cells(tbl):
        _set_fixed_layout(tbl, _TABLE_WIDTH_TWIPS)
        return True

    n_cols = len(table.columns)
    if n_cols == 0:
        return False

    weights = _compute_weights(table, n_cols)
    widths = _normalize(weights, _TABLE_WIDTH_TWIPS, n_cols)

    _set_grid(tbl, widths)
    _set_cell_widths(tbl, widths)
    _set_fixed_layout(tbl, _TABLE_WIDTH_TWIPS)
    return True


def _compute_weights(table, n_cols: int) -> list[float]:
    """Вес колонки — максимальная «визуальная» длина текста в ячейках.

    Формулы считаются на 20% длиннее: Cambria Math рендерится крупнее
    Times New Roman при том же кегле.
    """
    weights = [4.0] * n_cols

    for row in table.rows:
        for j, cell in enumerate(row.cells):
            if j >= n_cols:
                break
            for para in cell.paragraphs:
                length = _paragraph_length(para)
                if length > weights[j]:
                    weights[j] = float(length)

    return weights


def _paragraph_length(para) -> float:
    """Длина текста абзаца с учётом содержимого OMML-формул.

    python-docx para.text видит только <w:t>. Числа внутри <m:oMath>
    лежат в <m:t>. Считаем оба, формулы — с коэффициентом 1.2.
    """
    p = para._p
    w_len = sum(len(t.text or "") for t in p.findall(".//" + w("t")))
    m_len = sum(len(t.text or "") for t in p.findall(".//" + m("t")))
    return w_len + m_len * 1.2


def _normalize(weights: list[float], total: int, n_cols: int) -> list[int]:
    """Ширины колонок: минимум MIN_TWIPS, остаток — по весам.

    Если минимум на все колонки не влезает — откатываемся к равномерному
    распределению.
    """
    even_share = total // n_cols

    # Минимум не должен превышать 80% равномерной доли — иначе для таблиц
    # с большим числом колонок (8+) минимум съест всю ширину.
    min_twips = min(_MIN_TWIPS_PER_COL, int(even_share * 0.8))

    min_total = min_twips * n_cols
    if min_total >= total:
        # Слишком много колонок — равномерно.
        return [even_share] * n_cols

    rest = total - min_total
    total_w = sum(weights)
    if total_w <= 0:
        return [min_twips] * n_cols

    extras = [int(round(w / total_w * rest)) for w in weights]
    diff = rest - sum(extras)
    if diff:
        idx = max(range(n_cols), key=lambda i: weights[i])
        extras[idx] += diff

    widths = [min_twips + e for e in extras]

    # Страховка сверху: одна колонка не больше 50% таблицы.
    max_twips = int(total * _MAX_COL_SHARE)
    for i, width in enumerate(widths):
        if width > max_twips:
            overflow = width - max_twips
            widths[i] = max_twips
            # Разбросать overflow по остальным пропорционально.
            others = [j for j in range(n_cols) if j != i]
            other_total = sum(widths[j] for j in others)
            if other_total == 0:
                continue
            for j in others:
                share = widths[j] / other_total
                widths[j] += int(overflow * share)

    # Финальная коррекция остатка от округлений.
    diff = total - sum(widths)
    if diff:
        idx = max(range(n_cols), key=lambda i: widths[i])
        widths[idx] += diff

    return widths


def _set_grid(tbl, widths: list[int]) -> None:
    """Перезаписать <w:tblGrid> новыми ширинами."""
    old = tbl.find(w("tblGrid"))
    if old is not None:
        tbl.remove(old)

    grid = OxmlElement("w:tblGrid")
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    tblPr = get_or_add_tblPr(tbl)
    tblPr.addnext(grid)


def _set_cell_widths(tbl, widths: list[int]) -> None:
    """Прописать <w:tcW> каждой ячейке по её колонке.

    Учитывает gridSpan: ячейка, растянутая на N колонок, получает
    сумму соответствующих ширин.
    """
    for tr in tbl.findall(w("tr")):
        col_idx = 0
        for tc in tr.findall(w("tc")):
            if col_idx >= len(widths):
                break

            tcPr = get_or_add_tcPr(tc)

            gs = tcPr.find(w("gridSpan"))
            span = 1
            if gs is not None:
                try:
                    span = int(gs.get(qn("w:val")))
                except (TypeError, ValueError):
                    span = 1

            col_end = min(col_idx + span, len(widths))
            cell_width = sum(widths[col_idx:col_end])

            old = tcPr.find(w("tcW"))
            if old is not None:
                tcPr.remove(old)

            tcW = OxmlElement("w:tcW")
            tcW.set(qn("w:w"), str(cell_width))
            tcW.set(qn("w:type"), "dxa")
            tcPr.append(tcW)

            col_idx += span


def _set_fixed_layout(tbl, table_width: int) -> None:
    """tblLayout=fixed, tblW в twips."""
    tblPr = get_or_add_tblPr(tbl)

    for tag in ("tblW", "tblLayout"):
        old = tblPr.find(w(tag))
        if old is not None:
            tblPr.remove(old)

    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), str(table_width))
    tblW.set(qn("w:type"), "dxa")
    tblPr.append(tblW)

    tblLayout = OxmlElement("w:tblLayout")
    tblLayout.set(qn("w:type"), "fixed")
    tblPr.append(tblLayout)


def _has_merged_cells(tbl) -> bool:
    for tc in tbl.iter(w("tc")):
        tcPr = tc.find(w("tcPr"))
        if tcPr is None:
            continue
        if tcPr.find(w("gridSpan")) is not None:
            return True
        if tcPr.find(w("vMerge")) is not None:
            return True
    return False


# ======================================================================
# Содержимое ячеек
# ======================================================================

class FixTableCells(DocxFix):
    """Выравнивание и отступы в абзацах внутри таблиц."""

    name = "table_cells"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if _fix_cell_paragraph(para):
                            result.changes += 1

        return result


def _fix_cell_paragraph(para) -> bool:
    pPr = get_or_add_pPr(para._p)
    changed = False

    # --- 1. jc=left ---
    old_jc = pPr.find(w("jc"))
    if old_jc is None or old_jc.get(qn("w:val")) != "left":
        if old_jc is not None:
            pPr.remove(old_jc)
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "left")
        ppr_insert(pPr, jc)
        changed = True

    # --- 2. firstLine=0 ---
    ind = pPr.find(w("ind"))
    if ind is None:
        ind = OxmlElement("w:ind")
        ind.set(qn("w:firstLine"), "0")
        ind.set(qn("w:left"), "0")
        ppr_insert(pPr, ind)
        changed = True
    else:
        if ind.get(qn("w:firstLine")) not in (None, "0"):
            ind.set(qn("w:firstLine"), "0")
            changed = True
        if ind.get(qn("w:left")) not in (None, "0"):
            ind.set(qn("w:left"), "0")
            changed = True

    # --- 3. lineRule=atLeast + line>=360 ---
    sp = pPr.find(w("spacing"))
    if sp is None:
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:line"), "360")
        sp.set(qn("w:lineRule"), "atLeast")
        ppr_insert(pPr, sp)
        changed = True
    else:
        if sp.get(qn("w:lineRule")) != "atLeast":
            sp.set(qn("w:lineRule"), "atLeast")
            changed = True
        try:
            line_val = int(sp.get(qn("w:line")) or "0")
        except ValueError:
            line_val = 0
        if line_val < 360:
            sp.set(qn("w:line"), "360")
            changed = True

    return changed