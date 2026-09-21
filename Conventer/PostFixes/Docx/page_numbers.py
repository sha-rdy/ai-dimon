"""Номера страниц в футере секции.

Позиция по вертикали задаётся через footer_distance в reference.docx
(10 мм, см. SectionSpec.footer_offset_mm).
"""

from __future__ import annotations

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from .base import DocxFix, FixContext, FixResult


_ALIGN = {
    "left":   WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right":  WD_ALIGN_PARAGRAPH.RIGHT,
}


class FixPageNumbers(DocxFix):
    name = "page_numbers"

    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        result = FixResult(name=self.name)

        if ctx.pn_section_index >= len(doc.sections):
            result.details["reason"] = "секция не найдена"
            return result

        section = doc.sections[ctx.pn_section_index]
        footer = section.footer
        footer.is_linked_to_previous = False

        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        for r in list(p.runs):
            r._element.getparent().remove(r._element)

        p.alignment = _ALIGN.get(ctx.pn_align, WD_ALIGN_PARAGRAPH.RIGHT)

        run = p.add_run()
        r = run._r

        # <w:fldChar begin/> <w:instrText> PAGE </w:instrText>
        # <w:fldChar separate/> <w:t>1</w:t> <w:fldChar end/>
        for tag, attrs in (
            ("w:fldChar",  {"w:fldCharType": "begin"}),
            ("w:instrText", {"xml:space": "preserve"}),
            ("w:fldChar",  {"w:fldCharType": "separate"}),
            ("w:t",        {}),
            ("w:fldChar",  {"w:fldCharType": "end"}),
        ):
            el = OxmlElement(tag)
            for k, v in attrs.items():
                el.set(qn(k), v)
            if tag == "w:instrText":
                el.text = " PAGE "
            elif tag == "w:t":
                el.text = "1"
            r.append(el)

        run.font.name = ctx.pn_font
        run.font.size = Pt(ctx.pn_size_pt)

        result.changes = 1
        return result