"""Шаблон СТП 01-2024 (БГУИР): spec + preset + config + reference + filters.

Наружу торчит один объект — STP2024. Всё знание о стандарте
собрано в этой папке:

    spec.py            — стили и поля reference.docx
    preset.py          — фиксеры и контекст постобработки
    config.toml        — параметры рантайма (перекрывают preset)
    filters_src/*.lua  — шаблоны Lua с $placeholder
    filters/*.lua      — ГЕНЕРИРУЕТСЯ из filters_src + config.toml
    reference.docx     — ГЕНЕРИРУЕТСЯ из spec.py
"""

from __future__ import annotations

from pathlib import Path

from templates._core import Template

from .preset import STP2024_PRESET
from .spec import STP2024_BSUIR_SPEC


STP2024 = Template(
    name="СТП 01-2024 (БГУИР)",
    directory=Path(__file__).resolve().parent,
    spec=STP2024_BSUIR_SPEC,
    preset=STP2024_PRESET,
)

__all__ = ["STP2024"]