"""Блоки кода: предикаты и фиксеры.

Общий предикат `is_code_paragraph` — единственное место, где решается
«это абзац кода?». Все фиксеры для блоков кода используют его.
"""

from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._ooxml import ppr_insert, style_ids, w
from .base import DocxFix, FixContext, FixResult
from docx.text.paragraph import Paragraph


# ----------------------------------------------------------------------
# Предикат
# ----------------------------------------------------------------------

_CODE_STYLES: frozenset[str] = frozenset({
    "sourcecode",
    "source code",
    "source-code",
    "verbatim char",
    "preformatted text",
    "pre",
    "code",
})


def is_code_paragraph(para: Paragraph) -> bool:
    """Абзац — фрагмент блока кода?

    Два случая:
      • стиль SourceCode (или один из его вариантов);
      • стиль Compact без numPr — так pandoc помечает строки блока
        кода, кроме первой (у которых стиль уже SourceCode).
    """
    sid, sname = style_ids(para.style)
    if sid in _CODE_STYLES or sname in _CODE_STYLES:
        return True

    if (sid == "compact" or sname == "compact"):
        if para._p.find(".//" + w("numPr")) is None:
            return True

    return False


# ----------------------------------------------------------------------
# Общий помощник для правки pPr
# ----------------------------------------------------------------------

def _force_left(pPr) -> bool:
    """Выставить jc=left. True, если что-то изменилось."""
    old = pPr.find(w("jc"))
    if old is not None and old.get(qn("w:val")) == "left":
        return False
    if old is not None:
        pPr.remove(old)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "left")
    ppr_insert(pPr, jc)
    return True


def _force_wrap(pPr) -> bool:
    """Разрешить перенос строк (wordWrap=0). True, если изменилось."""
    old = pPr.find(w("wordWrap"))
    if old is not None and old.get(qn("w:val")) == "0":
        return False
    if old is not None:
        pPr.remove(old)
    ww = OxmlElement("w:wordWrap")
    ww.set(qn("w:val"), "0")
    ppr_insert(pPr, ww)
    return True


def _drop_right_tabs(pPr) -> bool:
    """Убрать правые таб-стопы. True, если что-то удалили."""
    tabs = pPr.find(w("tabs"))
    if tabs is None:
        return False

    removed = False
    for tab in tabs.findall(w("tab")):
        if tab.get(qn("w:val")) == "right":
            tabs.remove(tab)
            removed = True

    if len(tabs) == 0:
        pPr.remove(tabs)

    return removed


# ----------------------------------------------------------------------
# Фиксеры
# ----------------------------------------------------------------------

class FixSourceCodeAlign(DocxFix):
    """Выравнивание блоков кода по левому краю.

    Нужно потому, что pandoc рендерит блок кода как серию абзацев:
    первый получает SourceCode (там jc=left из стиля), остальные —
    Compact (наследует jc=both от Normal). Без форса в pPr строки
    кода растягиваются к правому краю.
    """

    name = "source_code_align"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for para in doc.paragraphs:
            if not is_code_paragraph(para):
                continue

            pPr = para._p.get_or_add_pPr()
            if _force_left(pPr):
                result.changes += 1

        return result


class FixSourceCodeWrap(DocxFix):
    """Переносы длинных строк в блоках кода.

    Длинные строки не переносятся и уезжают за поля. Ставим wordWrap=0
    и убираем правые таб-стопы (наследие BodyText).
    """

    name = "source_code_wrap"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for para in doc.paragraphs:
            if not is_code_paragraph(para):
                continue

            pPr = para._p.get_or_add_pPr()
            changed = False
            if _force_wrap(pPr):
                changed = True
            if _drop_right_tabs(pPr):
                changed = True

            if changed:
                result.changes += 1

        return result