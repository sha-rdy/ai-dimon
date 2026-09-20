"""Постобработка DOCX: смена стиля спецзаголовков.

СТП 01-2024, п. 2.1.1:
    Названия ненумерованных разделов выравниваются по центру
    страницы без абзацного отступа.

Pandoc не умеет надёжно применять custom-style к заголовкам,
поэтому меняем стиль через python-docx.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document


DEFAULT_SPECIAL_TEXTS: frozenset[str] = frozenset({
    "введение",
    "заключение",
    "содержание",
    "реферат",
    "список использованных источников",
    "перечень условных обозначений",
    "перечень условных обозначений, символов и терминов",
})

DEFAULT_APPENDIX_PREFIX: str = "приложение"
DEFAULT_STYLE_NAME: str = "SpecialHeading"


def _is_special(
    text: str,
    special_texts: frozenset[str],
    appendix_prefix: str,
) -> bool:
    low = text.strip().lower()
    if low in special_texts:
        return True
    return low.startswith(appendix_prefix)


def _is_h1(para) -> bool:
    style = para.style
    if style is None:
        return False
    sid = (style.style_id or "").lower()
    sname = (style.name or "").lower()
    return sid == "heading1" or sname in ("heading 1", "heading1")


def fix_special_headings(
    docx_path: Path,
    *,
    style_name: str = DEFAULT_STYLE_NAME,
    special_texts: frozenset[str] = DEFAULT_SPECIAL_TEXTS,
    appendix_prefix: str = DEFAULT_APPENDIX_PREFIX,
) -> int:
    """Заменить стиль спецзаголовков. Возвращает число правок."""
    doc = Document(str(docx_path))

    try:
        special_style = doc.styles[style_name]
    except KeyError:
        return 0

    fixed = 0
    for para in doc.paragraphs:
        if not _is_h1(para):
            continue
        if _is_special(para.text, special_texts, appendix_prefix):
            para.style = special_style
            fixed += 1

    doc.save(str(docx_path))
    return fixed