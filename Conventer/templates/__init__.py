"""Пакет шаблонов.

Публичный API — из templates._core. Конкретные стандарты —
в templates/<name>/ (например, templates.stp2024_BSUIR).

CLI — python -m templates.cli.
"""

from ._core import (
    Align, CheckResult, Issue, SectionSpec, StyleSpec,
    TabStop, Template, TemplateChecker, TemplateConfig,
    TemplateGenerator, TemplateSpec, generate_filters,
)

__all__ = [
    "Align", "SectionSpec", "StyleSpec", "TabStop", "TemplateSpec",
    "TemplateConfig",
    "TemplateGenerator",
    "TemplateChecker", "CheckResult", "Issue",
    "generate_filters",
    "Template",
]