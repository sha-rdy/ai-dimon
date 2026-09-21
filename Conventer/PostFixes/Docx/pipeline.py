"""Единый пайплайн постобработки DOCX.

Порядок:
  1) Все DocxFix-ы применяются к одному открытому Document.
  2) Document сохраняется один раз.
  3) Все PackageFix-ы применяются к одному открытому workspace.
     Один unpack + один repack на всю zip-фазу — атомарно.

Внутри zip-фазы отдельные фиксеры зовут ws.mark_dirty() только
если реально что-то поменяли. Если никто не пометил — оригинал
остаётся побайтово неизменным.
"""

from __future__ import annotations

import logging
from pathlib import Path

from docx import Document

from ._zip import open_docx_zip
from .base import DocxFix, FixContext, FixResult, PackageFix

log = logging.getLogger(__name__)


class DocxPipeline:
    def __init__(
        self,
        docx_fixes: list[DocxFix],
        package_fixes: list[PackageFix],
        ctx: FixContext,
    ) -> None:
        self.docx_fixes = list(docx_fixes)
        self.package_fixes = list(package_fixes)
        self.ctx = ctx

    def run(self, path: Path, *, verbose: bool = False) -> list[FixResult]:
        results: list[FixResult] = []

        active_docx = [f for f in self.docx_fixes if self.ctx.is_enabled(f.name)]
        active_pkg  = [f for f in self.package_fixes if self.ctx.is_enabled(f.name)]

        # --- Фаза 1: python-docx. Один open, один save. ---
        if active_docx:
            doc = Document(str(path))
            total_changes = 0                # ← счётчик
            for fix in active_docx:
                r = fix.apply(doc, self.ctx)
                results.append(r)
                total_changes += r.changes   # ← накапливаем
                if verbose:
                    log.info("%s", r)
            if total_changes > 0:            # ← save только при реальных правках
                doc.save(str(path))

        # --- Фаза 2: zip. Один unpack, один repack. ---
        if active_pkg:
            with open_docx_zip(path) as ws:
                for fix in active_pkg:
                    r = fix.apply(ws, self.ctx)
                    results.append(r)
                    if verbose:
                        log.info("%s", r)

        return results