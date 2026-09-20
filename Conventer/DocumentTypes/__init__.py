from .BaseDoc import BaseDocument
from .MarkdownDoc import MarkdownDocument
from .DocxDoc import DocxDocument
from .EquationNumbering import number_equations
from .PostProcess import add_page_numbers, enable_field_updates

from .SpecialHeadings import fix_special_headings

from .TableFixes import fix_tables

from .ListFixes import fix_lists

from .FootnoteFixes import fix_footnote_marks

__all__ = [
    "BaseDocument", "MarkdownDocument", "DocxDocument",
    "number_equations",
    "add_page_numbers", "enable_field_updates",
    "fix_special_headings",
    "fix_tables",
    "fix_lists",
    "fix_footnote_marks",
]