"""Скобка после знака сноски (СТП 01-2024, п. 2.9.1).

СТП требует: знаки сноски выполняют арабскими цифрами со скобкой
и помещают справа на уровне верхнего обреза слова.

Word рендерит footnoteReference как просто цифру. Добавляем «)» сразу
после ссылки в document.xml и footnotes.xml.
"""

from __future__ import annotations

from lxml import etree

from ._ooxml import w, xml_space
from ._zip import DocxZipWorkspace
from .base import FixContext, FixResult, PackageFix


class FixFootnoteMarks(PackageFix):
    name = "footnote_marks"

    def apply(self, ws: DocxZipWorkspace, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        for member, tag in (
            ("document.xml",  "footnoteReference"),
            ("footnotes.xml", "footnoteRef"),
        ):
            f = ws.tmpdir / "word" / member
            if not f.exists():
                continue

            tree = etree.parse(str(f))
            root = tree.getroot()

            changed_here = False
            for ref in root.findall(".//" + w(tag)):
                if _add_paren(ref):
                    result.changes += 1
                    changed_here = True

            if changed_here:
                tree.write(
                    str(f),
                    xml_declaration=True,
                    encoding="UTF-8",
                    standalone=True,
                )
                ws.mark_dirty()

        return result


def _add_paren(ref_el) -> bool:
    """Вставить <w:t>)</w:t> сразу после ref_el, в том же run.

    True — если добавили сейчас. False — если уже было.
    """
    run = ref_el.getparent()
    if run is None:
        return False

    for t in run.findall(w("t")):
        if (t.text or "").endswith(")"):
            return False

    rpr = run.find(w("rPr"))
    if rpr is None:
        rpr = etree.Element(w("rPr"))
        run.insert(0, rpr)
    if rpr.find(w("vertAlign")) is None:
        va = etree.SubElement(rpr, w("vertAlign"))
        va.set(w("val"), "superscript")

    t = etree.Element(w("t"))
    t.text = ")"
    t.set(xml_space(), "preserve")

    idx = list(run).index(ref_el)
    run.insert(idx + 1, t)
    return True