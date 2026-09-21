"""Готовые пресеты постобработки.

Preset — замороженный набор:
  • FixContext (все параметры);
  • списки фиксеров в правильном порядке;
  • доп. аргументы pandoc.

Stp2024Converter.PRESET = STP2024. Configurator делает копию через
Preset.copy() и не мутирует общий объект.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .base import DocxFix, FixContext, PackageFix
from .equations import FixEquationNumbers
from .field_updates import FixFieldUpdates
from .footnotes import FixFootnoteMarks
from .lists import FixLists
from .page_numbers import FixPageNumbers
from .special_headings import FixSpecialHeadings
from .tables import FixTables


@dataclass
class Preset:
    name: str
    ctx: FixContext
    docx_fixes: list[DocxFix] = field(default_factory=list)
    package_fixes: list[PackageFix] = field(default_factory=list)
    pandoc_args: list[str] = field(default_factory=list)

    def copy(self, **changes: Any) -> "Preset":
        """Копия с заменой полей.

        dataclasses.replace() копирует ссылки на списки/словари —
        поэтому явно клонируем всё изменяемое, чтобы правки в копии
        не утекли в общий пресет.
        """
        base = replace(self, **changes)
        base.docx_fixes = list(base.docx_fixes)
        base.package_fixes = list(base.package_fixes)
        base.pandoc_args = list(base.pandoc_args)
        if base.ctx is self.ctx:
            base.ctx = replace(self.ctx, enabled=dict(self.ctx.enabled))
        return base


# ----------------------------------------------------------------------
# СТП 01-2024 (БГУИР)
# ----------------------------------------------------------------------

_STP2024_SPECIAL: frozenset[str] = frozenset({
    "введение",
    "заключение",
    "содержание",
    "реферат",
    "список использованных источников",
    "перечень условных обозначений",
    "перечень условных обозначений, символов и терминов",
})


STP2024 = Preset(
    name="СТП 01-2024 (БГУИР)",
    ctx=FixContext(
        special_texts=_STP2024_SPECIAL,
        appendix_prefix="приложение",
        special_style_name="SpecialHeading",
        eq_tab_cm=16.5,
        pn_align="right",
        pn_font="Times New Roman",
        pn_size_pt=14.0,
    ),
    docx_fixes=[
        # Порядок важен:
        #   special_headings ДО equations — EquationNumbers распознаёт
        #   SpecialHeading как H1, поэтому смена стиля должна быть раньше.
        #   page_numbers последним — пишет в футер, ни на что не влияет.
        FixSpecialHeadings(),
        FixTables(),
        FixLists(),
        FixEquationNumbers(),
        FixPageNumbers(),
    ],
    package_fixes=[
        # Все PackageFix работают в одном DocxZipWorkspace (см. DocxPipeline).
        # Порядок внутри zip-фазы не критичен: они правят разные файлы.
        FixFootnoteMarks(),
        FixFieldUpdates(),
    ],
    pandoc_args=["--syntax-highlighting=tango"],
)