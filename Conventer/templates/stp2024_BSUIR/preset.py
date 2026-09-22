"""Пресет постобработки для СТП 01-2024 (БГУИР).

Список фиксеров и значения FixContext для этого стандарта.
Значения из config.toml перекрывают эти дефолты (см. Stp2024Configurator).
"""

from __future__ import annotations

from PostFixes.Docx import (
    FixContext,
    FixEquationNumbers,
    FixFieldUpdates,
    FixFootnoteMarks,
    FixLists,
    FixPageNumbers,
    FixSpecialHeadings,
    FixTables,
    FixInlineMathSpacing,
    FixSourceCodeWrap,
    FixSourceCodeAlign,
    Preset,
)


_STP2024_SPECIAL: frozenset[str] = frozenset({
    "введение",
    "заключение",
    "содержание",
    "реферат",
    "список использованных источников",
    "перечень условных обозначений",
    "перечень условных обозначений, символов и терминов",
})


STP2024_PRESET = Preset(
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
        FixSourceCodeAlign(),
        FixSourceCodeWrap(),
        FixEquationNumbers(),
        FixInlineMathSpacing(),
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