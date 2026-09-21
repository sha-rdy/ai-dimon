"""Нумерация формул (СТП 01-2024, п. 2.4.6).

Находит display-формулы (<m:oMath>) в одиночных параграфах и добавляет
номер (N.M) через правый таб-стоп. Заодно:
  • оборачивает inline-формулы в <m:oMathPara>;
  • снимает обёртку <w:sdt> (убирает серую рамку Word);
  • ставит отступы сверху/снизу и центрирование (СТП п. 2.4.3).
"""

from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._ooxml import is_heading, m, para_text, ppr_insert, w
from ._tracker import SectionContext, SectionTracker
from .base import DocxFix, FixContext, FixResult


class FixEquationNumbers(DocxFix):
    name = "equations"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)
        eq_in_section = 0

        for para, sec in SectionTracker(doc, ctx):
            if is_heading(para, 1):
                eq_in_section = 0
                continue

            p = para._p
            if not p.findall(".//" + m("oMath")):
                continue

            # Пропускаем параграфы с обычным текстом — там формула inline.
            # Иначе рискуем пронумеровать «где x — это ...».
            if para_text(p).strip():
                continue

            # Идемпотентность: если в конце уже стоит (N.M) — пропускаем.
            if _has_number(p):
                result.skipped += 1
                continue

            _unwrap_sdt(p)
            _ensure_mathpara(p)

            eq_in_section += 1
            num = _format_number(sec, eq_in_section)

            _add_spacing(para)
            _add_right_tab(para, ctx.eq_tab_cm)
            _append_number(para, num)
            result.changes += 1

        return result


# ----------------------------------------------------------------------
# Внутренние
# ----------------------------------------------------------------------

def _format_number(sec: SectionContext, n: int) -> str:
    if sec.kind == "appendix":
        letter = sec.letter or "?"
        return f"({letter}.{n})"
    if sec.kind == "normal":
        return f"({sec.index}.{n})"
    # preamble/special — по СТП формулы в них не нумеруются разделом.
    # Если попали — оставляем хотя бы счётчик.
    return f"({n})"


def _has_number(p) -> bool:
    """Есть ли в конце абзаца <w:t>(N.M)</w:t>."""
    for t in reversed(p.findall(".//" + w("t"))):
        text = (t.text or "").strip()
        if not text:
            continue
        return text.startswith("(") and text.endswith(")")
    return False


def _unwrap_sdt(p) -> None:
    """Развернуть <w:sdt> вокруг формулы — убирает серую рамку Word."""
    for sdt in p.findall(".//" + w("sdt")):
        content = sdt.find(w("sdtContent"))
        if content is None:
            continue
        parent = sdt.getparent()
        idx = list(parent).index(sdt)
        for child in list(content):
            parent.insert(idx, child)
            idx += 1
        parent.remove(sdt)


def _ensure_mathpara(p) -> None:
    """Если <m:oMath> не в <m:oMathPara>, оборачиваем."""
    for omath in p.findall(".//" + m("oMath")):
        parent = omath.getparent()
        if parent.tag == m("oMathPara"):
            continue
        mathpara = OxmlElement("m:oMathPara")
        idx = list(parent).index(omath)
        parent.remove(omath)
        mathpara.append(omath)
        parent.insert(idx, mathpara)


def _add_spacing(para) -> None:
    """Отступы вокруг формулы + центрирование.

    lineRule='atLeast', а не 'exact' — иначе Word обрезает
    высокие формулы (дроби, интегралы).
    """
    pPr = para._p.get_or_add_pPr()

    old = pPr.find(w("spacing"))
    if old is not None:
        pPr.remove(old)

    sp = OxmlElement("w:spacing")
    sp.set(qn("w:before"), "360")
    sp.set(qn("w:after"), "360")
    sp.set(qn("w:line"), "360")
    sp.set(qn("w:lineRule"), "atLeast")
    ppr_insert(pPr, sp)

    old_jc = pPr.find(w("jc"))
    if old_jc is not None:
        pPr.remove(old_jc)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    ppr_insert(pPr, jc)


def _add_right_tab(para, tab_cm: float) -> None:
    """Добавить правый таб-стоп в pPr абзаца (если ещё нет)."""
    pPr = para._p.get_or_add_pPr()
    tabs = pPr.find(w("tabs"))
    if tabs is None:
        tabs = OxmlElement("w:tabs")
        ppr_insert(pPr, tabs)
    for existing in tabs.findall(w("tab")):
        if existing.get(qn("w:val")) == "right":
            return
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), str(int(tab_cm * 567)))
    tabs.append(tab)


def _append_number(para, num: str) -> None:
    """Дописать в конец абзаца: <w:r><w:tab/><w:t>(N.M)</w:t></w:r>."""
    run = OxmlElement("w:r")
    run.append(OxmlElement("w:tab"))
    t = OxmlElement("w:t")
    t.text = num
    run.append(t)
    para._p.append(run)