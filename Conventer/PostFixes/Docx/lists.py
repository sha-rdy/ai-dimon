"""Маркеры перечислений по СТП 01-2024, п. 2.3.5, 2.3.7.

СТП требует:
  • простое перечисление — тире + пробел;
  • сложное перечисление — номер + пробел (без точки).

НО: список использованных источников — это библиография (ГОСТ 7.1),
там формат «1.», «2.», сохраняем как есть.
"""

from __future__ import annotations

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._ooxml import W_NS, is_heading, w, xml_space
from ._tracker import SectionTracker
from .base import DocxFix, FixContext, FixResult


class FixLists(DocxFix):
    name = "lists"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)
        counters: dict[tuple[str, str], int] = {}
        last_key: tuple[str, str] | None = None

        for para, sec in SectionTracker(doc, ctx):
            # При входе в новый H1 сбрасываем счётчики.
            # Это лечит случай, когда pandoc использует один numId
            # для всех списков документа — второй список в другом
            # разделе должен начинаться с 1, а не продолжаться.
            if is_heading(para, 1):
                counters.clear()
                last_key = None
                continue

            # Библиография — формат ГОСТ, не трогаем.
            if sec.kind == "special" and \
               sec.heading_text.lower() in ctx.skip_list_sections:
                continue

            p = para._p
            ppr = p.find(w("pPr"))
            if ppr is None:
                continue

            numpr = ppr.find(w("numPr"))
            if numpr is None:
                last_key = None
                continue

            ilvl_el = numpr.find(w("ilvl"))
            numid_el = numpr.find(w("numId"))
            ilvl = ilvl_el.get(qn("w:val")) if ilvl_el is not None else "0"
            numid = numid_el.get(qn("w:val")) if numid_el is not None else "0"

            # numId="0" — это «нет списка» (заглушка Word).
            if numid == "0":
                continue

            is_bullet = _is_bullet(doc, numid, ilvl)

            key = (numid, ilvl)
            if key != last_key:
                counters.setdefault(key, 0)
                last_key = key

            if is_bullet:
                prefix = "\u2013 "   # «– »
            else:
                counters[key] += 1
                prefix = f"{counters[key]} "

            ppr.remove(numpr)
            _prepend_text(p, prefix)
            result.changes += 1

        return result


def _is_bullet(doc: Document, numid: str, ilvl: str) -> bool:
    """Определить, bullet это или нумерация."""
    try:
        root = doc.part.numbering_part.element
    except (AttributeError, KeyError):
        return False

    W = f"{{{W_NS}}}"

    abstract_id = None
    for num in root.findall(f"{W}num"):
        if num.get(f"{W}numId") == numid:
            ab = num.find(f"{W}abstractNumId")
            if ab is not None:
                abstract_id = ab.get(f"{W}val")
            break
    if abstract_id is None:
        return False

    for an in root.findall(f"{W}abstractNum"):
        if an.get(f"{W}abstractNumId") != abstract_id:
            continue
        for lvl in an.findall(f"{W}lvl"):
            if lvl.get(f"{W}ilvl") != ilvl:
                continue
            fmt = lvl.find(f"{W}numFmt")
            if fmt is not None:
                return fmt.get(f"{W}val") == "bullet"
    return False


def _prepend_text(p, text: str) -> None:
    """Вставить текст в начало первого run абзаца."""
    first = p.find(w("r"))
    if first is None:
        first = OxmlElement("w:r")
        p.append(first)

    t = first.find(w("t"))
    if t is None:
        t = OxmlElement("w:t")
        t.set(qn(xml_space()), "preserve")
        first.insert(0, t)
    t.text = text + (t.text or "")