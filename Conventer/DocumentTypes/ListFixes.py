"""Постобработка DOCX: перечисления по СТП 01-2024, п. 2.3.5, 2.3.7.

СТП требует:
  — простое перечисление: тире + пробел;
  — сложное перечисление: номер + пробел (без точки).

НО: список использованных источников — это библиография (ГОСТ 7.1),
там формат «1.», «2.», сохраняем как есть.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


# Разделы, где нумерация НЕ трогается (библиография и т.п.)
SKIP_SECTIONS = {
    "список использованных источников",
    "список литературы",
    "библиографический список",
}


def fix_lists(docx_path: Path) -> int:
    """Заменить маркеры списков на СТП-формат. Вернуть число параграфов."""
    doc = Document(str(docx_path))

    counters: dict[tuple[str, str], int] = {}
    last_list_key: tuple[str, str] | None = None

    in_skip_section = False
    fixed = 0

    for para in doc.paragraphs:
        # Отслеживаем текущий H1
        style = para.style
        sid = (style.style_id or "").lower() if style else ""
        sname = (style.name or "").lower() if style else ""
        if sid in ("heading1", "specialheading") or \
           sname in ("heading 1", "specialheading"):
            text_low = para.text.strip().lower()
            in_skip_section = text_low in SKIP_SECTIONS
            last_list_key = None
            continue

        p = para._p
        ppr = p.find(_w("pPr"))
        if ppr is None:
            continue

        numpr = ppr.find(_w("numPr"))
        if numpr is None:
            last_list_key = None
            continue

        # В разделе «Список источников» нумерацию не трогаем
        if in_skip_section:
            continue

        ilvl_el = numpr.find(_w("ilvl"))
        numid_el = numpr.find(_w("numId"))

        ilvl = ilvl_el.get(qn("w:val")) if ilvl_el is not None else "0"
        numid = numid_el.get(qn("w:val")) if numid_el is not None else "0"

        if numid == "0":
            continue

        is_bullet = _is_bullet_numbering(doc, numid, ilvl)

        key = (numid, ilvl)
        if key != last_list_key:
            counters.setdefault(key, 0)
            last_list_key = key

        if is_bullet:
            prefix = "\u2013 "   # «– »
        else:
            counters[key] += 1
            prefix = f"{counters[key]} "

        ppr.remove(numpr)
        _prepend_text(p, prefix)
        fixed += 1

    doc.save(str(docx_path))
    return fixed


def _is_bullet_numbering(doc: Document, numid: str, ilvl: str) -> bool:
    try:
        numbering_part = doc.part.numbering_part
    except (AttributeError, KeyError):
        return False

    root = numbering_part.element
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
            numfmt = lvl.find(f"{W}numFmt")
            if numfmt is not None:
                return numfmt.get(f"{W}val") == "bullet"
    return False


def _prepend_text(p, text: str) -> None:
    first_run = p.find(_w("r"))
    if first_run is None:
        first_run = OxmlElement("w:r")
        p.append(first_run)

    t = first_run.find(_w("t"))
    if t is None:
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        first_run.insert(0, t)
    t.text = text + (t.text or "")