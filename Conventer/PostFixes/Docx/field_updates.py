"""Автообновление полей (TOC, PAGE) при открытии DOCX.

Добавляет <w:updateFields w:val="true"/> в word/settings.xml.
Word при открытии спросит «Обновить поля?» → пользователь
нажимает Да → TOC заполняется, номера страниц пересчитываются.
"""

from __future__ import annotations

from lxml import etree

from ._ooxml import w
from ._zip import DocxZipWorkspace
from .base import FixContext, FixResult, PackageFix


class FixFieldUpdates(PackageFix):
    name = "field_updates"

    def apply(self, ws: DocxZipWorkspace, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        settings = ws.tmpdir / "word" / "settings.xml"
        if not settings.exists():
            result.details["reason"] = "settings.xml отсутствует"
            return result

        tree = etree.parse(str(settings))
        root = tree.getroot()

        uf = root.find(w("updateFields"))
        if uf is not None and uf.get(w("val")) in ("true", "1"):
            return result

        if uf is None:
            uf = etree.SubElement(root, w("updateFields"))
        uf.set(w("val"), "true")

        tree.write(
            str(settings),
            xml_declaration=True,
            encoding="UTF-8",
            standalone=True,
        )
        ws.mark_dirty()

        result.changes = 1
        return result