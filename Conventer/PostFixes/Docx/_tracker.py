"""Единый обход документа с отслеживанием текущего раздела.

Все фиксеры, которым нужно «знать, где мы находимся» (SpecialHeadings,
EquationNumbers, Lists), используют SectionTracker. Это гарантирует,
что special/appendix/normal распознаются одинаково.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Literal

from docx import Document
from docx.text.paragraph import Paragraph

from ._ooxml import is_heading
from .base import FixContext


SectionKind = Literal["preamble", "special", "appendix", "normal"]


@dataclass(frozen=True)
class SectionContext:
    """Состояние «мы находимся внутри H1 X»."""

    kind: SectionKind
    index: int                   # 1-based; 0 для preamble/special
    letter: str | None           # "А" для приложений, иначе None
    heading_text: str            # как в документе: "ВВЕДЕНИЕ", "ПРИЛОЖЕНИЕ А"


class SectionTracker:
    """Итератор по параграфам с контекстом текущего H1.

    Порядок выдачи: каждый параграф документа ровно один раз.
    Для самого заголовка kind — уже НОВЫЙ раздел (заголовок
    «открывает» раздел до того, как его увидит потребитель).
    """

    def __init__(self, doc: Document, ctx: FixContext) -> None:
        self._doc = doc
        self._ctx = ctx

    def __iter__(self) -> Iterator[tuple[Paragraph, SectionContext]]:
        ctx = self._ctx
        state = SectionContext("preamble", 0, None, "")
        section_no = 0
        app_no = 0

        for para in self._doc.paragraphs:
            if is_heading(para, 1):
                text = para.text.strip()
                low = text.lower()

                if low in ctx.special_texts:
                    state = SectionContext("special", 0, None, text)
                elif low.startswith(ctx.appendix_prefix):
                    app_no += 1
                    letter = (
                        ctx.app_letters[app_no - 1]
                        if 0 <= app_no - 1 < len(ctx.app_letters)
                        else "?"
                    )
                    state = SectionContext("appendix", app_no, letter, text)
                else:
                    section_no += 1
                    state = SectionContext("normal", section_no, None, text)

            yield para, state