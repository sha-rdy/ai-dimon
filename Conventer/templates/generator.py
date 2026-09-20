"""Генерация reference.docx из TemplateSpec."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

from .spec import Align, StyleSpec, TemplateSpec


_ALIGN_MAP = {
    Align.LEFT:    WD_ALIGN_PARAGRAPH.LEFT,
    Align.CENTER:  WD_ALIGN_PARAGRAPH.CENTER,
    Align.RIGHT:   WD_ALIGN_PARAGRAPH.RIGHT,
    Align.JUSTIFY: WD_ALIGN_PARAGRAPH.JUSTIFY,
}


# Встроенные стили Word: styleId → отображаемое имя.
_BUILTIN_NAMES: dict[str, str] = {
    "Normal":        "Normal",
    "BodyText":      "Body Text",
    "Heading1":      "Heading 1",
    "Heading2":      "Heading 2",
    "Heading3":      "Heading 3",
    "Heading4":      "Heading 4",
    "Heading5":      "Heading 5",
    "Heading6":      "Heading 6",
    "Heading7":      "Heading 7",
    "Heading8":      "Heading 8",
    "Heading9":      "Heading 9",
    "Caption":       "Caption",
    "Title":         "Title",
    "Subtitle":      "Subtitle",
    "Quote":         "Quote",
    "ListParagraph": "List Paragraph",
    "TOCHeading":    "TOC Heading",
    "FootnoteText":  "Footnote Text",
    "Header":        "Header",
    "Footer":        "Footer",
}


class TemplateGenerator:
    """Создаёт reference.docx из спецификации."""

    def __init__(self, spec: TemplateSpec) -> None:
        self.spec = spec

    def generate(self, out_path: Path) -> Path:
        doc = Document()

        self._apply_section(doc)
        self._apply_styles(doc)
        self._placeholder(doc)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(out_path)
        return out_path

    # --- внутреннее ---

    def _apply_section(self, doc: Document) -> None:
        s = doc.sections[0]
        s.page_width = Mm(self.spec.section.page_width_mm)
        s.page_height = Mm(self.spec.section.page_height_mm)
        s.top_margin = Mm(self.spec.section.margin_top_mm)
        s.bottom_margin = Mm(self.spec.section.margin_bottom_mm)
        s.left_margin = Mm(self.spec.section.margin_left_mm)
        s.right_margin = Mm(self.spec.section.margin_right_mm)
        s.footer_distance = Mm(self.spec.section.footer_offset_mm)

    def _apply_styles(self, doc: Document) -> None:
        for spec in self.spec.styles.values():
            style = self._get_or_create(doc, spec.name, spec.base_style)
            self._apply_font(style, spec)
            self._apply_paragraph(style, spec)

    @staticmethod
    def _get_or_create(doc: Document, name: str, base: str):
        """Найти стиль по styleId без warning'ов. Создать, если нет."""

        display = _BUILTIN_NAMES.get(name)
        if display is not None:
            try:
                return doc.styles[display]
            except KeyError:
                pass

        for style in doc.styles:
            if style.style_id == name:
                return style

        st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        try:
            st.base_style = doc.styles[base]
        except KeyError:
            pass
        return st

    @staticmethod
    def _apply_font(style, spec: StyleSpec) -> None:
        f = style.font
        f.name = spec.font
        f.size = Pt(spec.size_pt)
        f.bold = spec.bold
        f.italic = spec.italic

        rpr = style.element.get_or_add_rPr()

        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), spec.font)

        if spec.color_hex is not None:
            color = rpr.find(qn("w:color"))
            if color is None:
                color = OxmlElement("w:color")
                rpr.append(color)
            color.set(qn("w:val"), spec.color_hex)

    @staticmethod
    def _apply_paragraph(style, spec: StyleSpec) -> None:
        p = style.paragraph_format
        p.alignment = _ALIGN_MAP[spec.align]

        if spec.first_line_indent_cm is not None:
            p.first_line_indent = Mm(spec.first_line_indent_cm * 10)
        else:
            p.first_line_indent = Mm(0)

        p.space_before = Pt(spec.space_before_pt)
        p.space_after = Pt(spec.space_after_pt)
        p.keep_with_next = spec.keep_with_next

        if spec.line_spacing_pt is not None:
            p.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            p.line_spacing = Pt(spec.line_spacing_pt)

        ppr = style.element.get_or_add_pPr()

        # Page break before
        if spec.page_break_before:
            if ppr.find(qn("w:pageBreakBefore")) is None:
                ppr.append(OxmlElement("w:pageBreakBefore"))

        # Tab stops
        if spec.tab_stops:
            tabs_el = ppr.find(qn("w:tabs"))
            if tabs_el is None:
                tabs_el = OxmlElement("w:tabs")
                ppr.append(tabs_el)
            for stop in spec.tab_stops:
                tab = OxmlElement("w:tab")
                tab.set(qn("w:val"), stop.align)
                tab.set(qn("w:pos"), str(int(stop.pos_cm * 567)))
                tabs_el.append(tab)

    @staticmethod
    def _placeholder(doc: Document) -> None:
        doc.add_paragraph(
            "Reference document. Pandoc ignores this text; "
            "only styles and section properties matter."
        )