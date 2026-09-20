"""Спецификация шаблона документа.

TemplateSpec описывает:
  • параметры секции (размер страницы, поля, footer);
  • набор стилей с их параметрами.

Спецификации конкретных стандартов (СТП-2024, ГОСТ 7.32 и т.д.)
наследуют или инстанцируют TemplateSpec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


class Align(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "both"


@dataclass(frozen=True)
class SectionSpec:
    """Параметры секции в миллиметрах."""
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    margin_top_mm: float = 20.0
    margin_bottom_mm: float = 20.0
    margin_left_mm: float = 30.0
    margin_right_mm: float = 15.0
    footer_offset_mm: float = 10.0


@dataclass(frozen=True)
class TabStop:
    """Позиция табуляции в абзаце."""
    pos_cm: float
    align: str = "right"   # "left" | "center" | "right"


@dataclass(frozen=True)
class StyleSpec:
    """Параметры одного стиля."""
    name: str                       # styleId, например "Heading1"
    font: str = "Times New Roman"
    size_pt: float = 14.0
    bold: bool = False
    italic: bool = False
    color_hex: str | None = None    # "000000" — принудительно чёрный
    align: Align = Align.JUSTIFY
    first_line_indent_cm: float | None = 1.25
    line_spacing_pt: float | None = 18.0
    space_before_pt: float = 0.0
    space_after_pt: float = 0.0
    page_break_before: bool = False
    keep_with_next: bool = False
    base_style: str = "Normal"
    tab_stops: tuple[TabStop, ...] = ()


@dataclass
class TemplateSpec:
    """Полная спецификация шаблона."""
    name: str
    section: SectionSpec = field(default_factory=SectionSpec)
    styles: dict[str, StyleSpec] = field(default_factory=dict)

    required_styles: ClassVar[set[str] | None] = None

    def add(self, style: StyleSpec) -> "TemplateSpec":
        self.styles[style.name] = style
        return self