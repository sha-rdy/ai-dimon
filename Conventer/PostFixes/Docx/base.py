"""Базовые классы постобработки DOCX.

  • DocxFix    — работает через python-docx Document. Все DocxFix
                 выполняются в одном open/save (см. DocxPipeline).
  • PackageFix — работает с DOCX как с zip. Получает уже открытый
                 DocxZipWorkspace; распаковку/запаковку делает
                 DocxPipeline один раз на всю zip-фазу.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, TYPE_CHECKING

from docx import Document

if TYPE_CHECKING:
    from ._zip import DocxZipWorkspace


# ----------------------------------------------------------------------
# Результат
# ----------------------------------------------------------------------

@dataclass
class FixResult:
    name: str
    changes: int = 0
    skipped: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def touched(self) -> bool:
        return self.changes > 0

    def __str__(self) -> str:
        mark = "✅" if self.touched else "·"
        extra = f"  {self.details}" if self.details else ""
        return f"{mark} {self.name:18s} {self.changes:4d} изменений{extra}"


# ----------------------------------------------------------------------
# Контекст (один на весь прогон пайплайна)
# ----------------------------------------------------------------------

@dataclass
class FixContext:
    """Конфиг документа, а не отдельного фикса."""

    # Спецзаголовки
    special_texts: frozenset[str] = frozenset()
    appendix_prefix: str = "приложение"
    special_style_name: str = "SpecialHeading"

    # Приложения
    app_letters: str = "АБВГДЕЖИКЛМНПРСТУФХЦШЩЭЮЯ"

    # Разделы, где списки не трогаем (библиография)
    skip_list_sections: frozenset[str] = frozenset({
        "список использованных источников",
        "список литературы",
        "библиографический список",
    })

    # Формулы
    eq_tab_cm: float = 16.5

    # Номера страниц
    pn_align: str = "right"
    pn_font: str = "Times New Roman"
    pn_size_pt: float = 14.0
    pn_section_index: int = 0

    # Флаги: имя фикса → вкл/выкл. Отсутствует — значит включён.
    enabled: dict[str, bool] = field(default_factory=dict)

    def is_enabled(self, name: str) -> bool:
        return self.enabled.get(name, True)


# ----------------------------------------------------------------------
# Базовые классы
# ----------------------------------------------------------------------

class DocxFix(ABC):
    """Фикс уровня python-docx Document."""

    name: ClassVar[str] = ""

    @abstractmethod
    def apply(self, doc: Document, ctx: FixContext) -> FixResult:
        ...


class PackageFix(ABC):
    """Фикс уровня zip-архива DOCX.

    Принимает уже открытый workspace. Не открывает/закрывает его сам —
    это делает DocxPipeline один раз на всю zip-фазу, чтобы получить
    одну атомарную перепаковку.
    """

    name: ClassVar[str] = ""

    @abstractmethod
    def apply(self, ws: "DocxZipWorkspace", ctx: FixContext) -> FixResult:
        ...