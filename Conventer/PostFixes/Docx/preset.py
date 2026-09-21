"""Preset — контейнер фиксеров + FixContext + pandoc-args.

Только тип. Конкретные пресеты (STP2024 и др.) живут в
templates/<standard>/preset.py, чтобы всё знание о стандарте
было в одной папке.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .base import DocxFix, FixContext, PackageFix


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