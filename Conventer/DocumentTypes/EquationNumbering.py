"""Постобработка DOCX: нумерация формул по СТП 01-2024, п. 2.4.6.

Находит display-формулы (<m:oMathPara>), добавляет в тот же параграф
правый таб-стоп и номер (N.M). Оборачивает inline-формулы в <m:oMathPara>,
снимает обёртку <w:sdt> (убирает серую рамку Word), добавляет отступы
сверху и снизу — как требует СТП п. 2.4.3.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _m(tag: str) -> str:
    return f"{{{M_NS}}}{tag}"


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def number_equations(docx_path: Path, tab_cm: float = 16.5) -> int:
    """Нумерует display-формулы в DOCX.

    Обычные разделы: (N.M).
    Приложения: (А.1), (Б.1).
    Спецразделы (Введение, Заключение, ...) сбрасывают счётчики.
    """
    doc = Document(str(docx_path))

    section = 0
    eq_count = 0
    numbered = 0
    in_appendix = False
    app_index = 0
    app_letters = "АБВГДЕЖИКЛМНПРСТУФХЦШЩЭЮЯ"

    special_lower = {
        "введение", "заключение", "содержание", "реферат",
        "список использованных источников",
        "перечень условных обозначений",
        "перечень условных обозначений, символов и терминов",
    }

    for para in doc.paragraphs:
        style = para.style
        sid = (style.style_id or "").lower() if style else ""
        sname = (style.name or "").lower() if style else ""

        is_h1 = (
            sid in ("heading1", "specialheading")
            or sname in ("heading 1", "specialheading")
        )

        if is_h1:
            text_low = para.text.strip().lower()

            if text_low.startswith("приложение"):
                in_appendix = True
                app_index += 1
                eq_count = 0
            elif text_low in special_lower:
                in_appendix = False
                section = 0
                eq_count = 0
            else:
                in_appendix = False
                section += 1
                eq_count = 0
            continue

        p = para._p
        maths = p.findall(".//" + _m("oMath"))
        if not maths:
            continue

        text = "".join((t.text or "") for t in p.findall(".//" + _w("t")))
        if text.strip():
            continue

        _unwrap_sdt(p)
        _ensure_mathpara(p)

        eq_count += 1
        numbered += 1

        if in_appendix:
            idx = app_index - 1
            letter = app_letters[idx] if 0 <= idx < len(app_letters) else "?"
            num = f"({letter}.{eq_count})"
        else:
            num = f"({section}.{eq_count})"

        _add_equation_spacing(para)
        _add_right_tab(para, tab_cm)
        _append_tab_and_number(para, num)

    doc.save(str(docx_path))
    return numbered

def _unwrap_sdt(p) -> None:
    """Разворачивает <w:sdt> вокруг формулы — убирает серую рамку Word."""
    for sdt in p.findall(".//" + _w("sdt")):
        content = sdt.find(_w("sdtContent"))
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
    for omath in p.findall(".//" + _m("oMath")):
        parent = omath.getparent()
        if parent.tag == _m("oMathPara"):
            continue
        mathpara = OxmlElement("m:oMathPara")
        idx = list(parent).index(omath)
        parent.remove(omath)
        mathpara.append(omath)
        parent.insert(idx, mathpara)


def _add_equation_spacing(para) -> None:
    """Отступы вокруг формулы + выравнивание по центру.
    
    lineRule='atLeast', а не 'exact'. Иначе Word обрезает
    высокие формулы (с дробями, интегралами).
    """
    pPr = para._p.get_or_add_pPr()

    old = pPr.find(_w("spacing"))
    if old is not None:
        pPr.remove(old)

    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "360")
    spacing.set(qn("w:after"), "360")
    spacing.set(qn("w:line"), "360")
    spacing.set(qn("w:lineRule"), "atLeast")
    pPr.append(spacing)

    # Выравнивание по центру для параграфа с формулой
    old_jc = pPr.find(_w("jc"))
    if old_jc is not None:
        pPr.remove(old_jc)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    pPr.append(jc)

def _add_right_tab(para, tab_cm: float) -> None:
    """Добавить правый таб-стоп в pPr абзаца."""
    pPr = para._p.get_or_add_pPr()
    tabs = pPr.find(_w("tabs"))
    if tabs is None:
        tabs = OxmlElement("w:tabs")
        pPr.insert(0, tabs)
    for existing in tabs.findall(_w("tab")):
        if existing.get(qn("w:val")) == "right":
            return
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), str(int(tab_cm * 567)))
    tabs.append(tab)


def _append_tab_and_number(para, num: str) -> None:
    """Дописать в конец абзаца: <w:r><w:tab/><w:t>(N.M)</w:t></w:r>."""
    run = OxmlElement("w:r")
    tab = OxmlElement("w:tab")
    run.append(tab)
    t = OxmlElement("w:t")
    t.text = num
    run.append(t)
    para._p.append(run)