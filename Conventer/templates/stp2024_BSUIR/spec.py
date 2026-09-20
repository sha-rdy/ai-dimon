"""Спецификация шаблона reference.docx под СТП 01-2024 (БГУИР)."""

from templates.spec import Align, SectionSpec, StyleSpec, TabStop, TemplateSpec


STP2024_BSUIR_SPEC = TemplateSpec(
    name="СТП 01-2024 (БГУИР)",
    section=SectionSpec(
        page_width_mm=210.0,
        page_height_mm=297.0,
        margin_top_mm=20.0,
        margin_bottom_mm=20.0,
        margin_left_mm=30.0,
        margin_right_mm=15.0,
        footer_offset_mm=10.0,
    ),
)

_FORMULA_TABS = (TabStop(pos_cm=17.0, align="right"),)


STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Normal",
    font="Times New Roman", size_pt=14.0,
    align=Align.JUSTIFY,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    # tab_stops=_FORMULA_TABS,
    # table_borders=True,
))
STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Table",
    font="Times New Roman", size_pt=14.0,
    align=Align.LEFT,
    first_line_indent_cm=None,
    line_spacing_pt=18.0,
    table_borders=True,
))
STP2024_BSUIR_SPEC.add(StyleSpec(
    name="BodyText",
    base_style="Normal",
    font="Times New Roman", size_pt=14.0,
    align=Align.JUSTIFY,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    tab_stops=_FORMULA_TABS,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="FirstParagraph",
    base_style="Normal",
    font="Times New Roman", size_pt=14.0,
    align=Align.JUSTIFY,
    first_line_indent_cm=None,
    line_spacing_pt=18.0,
    tab_stops=_FORMULA_TABS,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Heading1",
    font="Times New Roman", size_pt=14.0, bold=True,
    color_hex="000000",
    align=Align.LEFT,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    space_after_pt=18.0,
    page_break_before=True,
    keep_with_next=True,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Heading2",
    font="Times New Roman", size_pt=14.0, bold=True,
    color_hex="000000",
    align=Align.LEFT,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    space_after_pt=18.0,
    keep_with_next=True,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Heading3",
    font="Times New Roman", size_pt=14.0, bold=True,
    color_hex="000000",
    align=Align.LEFT,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    keep_with_next=True,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Caption",
    font="Times New Roman", size_pt=14.0,
    align=Align.CENTER,
    first_line_indent_cm=None,
    line_spacing_pt=18.0,
    space_before_pt=6.0,
    space_after_pt=6.0,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="TableCaption",
    font="Times New Roman", size_pt=14.0,
    align=Align.LEFT,
    first_line_indent_cm=1.25,
    line_spacing_pt=18.0,
    space_before_pt=6.0,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="SourceCode",
    font="Courier New", size_pt=12.0,
    align=Align.LEFT,
    first_line_indent_cm=None,
    line_spacing_pt=12.0,
))

STP2024_BSUIR_SPEC.add(StyleSpec(
    name="Title",
    font="Times New Roman", size_pt=14.0, bold=True,
    align=Align.CENTER,
    first_line_indent_cm=None,
    line_spacing_pt=18.0,
))
STP2024_BSUIR_SPEC.add(StyleSpec(
    name="TOCHeading",
    font="Times New Roman", size_pt=14.0, bold=True,
    color_hex="000000",
    align=Align.CENTER,
    first_line_indent_cm=None,
    line_spacing_pt=18.0,
    space_after_pt=18.0,
))