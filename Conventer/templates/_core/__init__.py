"""Ядро пакета templates: типы, генератор, чекер, Template.

Конкретные стандарты (stp2024_BSUIR, ...) лежат рядом и используют
эти механизмы. Всё, что здесь есть, — переиспользуемое.
"""

from .checker import CheckResult, Issue, TemplateChecker
from .config import TemplateConfig
from .filters import generate_filters
from .generator import TemplateGenerator
from .spec import Align, SectionSpec, StyleSpec, TabStop, TemplateSpec
from .template import Template


__all__ = [
    "Align", "SectionSpec", "StyleSpec", "TabStop", "TemplateSpec",
    "TemplateConfig",
    "TemplateGenerator",
    "TemplateChecker", "CheckResult", "Issue",
    "generate_filters",
    "Template",
]