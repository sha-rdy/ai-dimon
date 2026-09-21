"""Загрузка конфигурации шаблона из config.toml.

Параметры секции (поля страницы) здесь НЕ хранятся — они живут
в spec.py и применяются при генерации reference.docx.

Свойства-хелперы (special_texts, appendix_prefix, app_letters, ...)
дают потребителям прямой доступ к типичным параметрам, не заставляя
лазить в dict-ы.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class TemplateConfig:
    """Конфигурация одного шаблона."""

    name: str = ""
    headings: dict[str, Any] = field(default_factory=dict)
    equations: dict[str, Any] = field(default_factory=dict)
    page_numbers: dict[str, Any] = field(default_factory=dict)
    toc: dict[str, Any] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Хелперы: headings
    # ------------------------------------------------------------------

    @property
    def special_texts(self) -> frozenset[str]:
        return frozenset(self.headings.get("special", []))

    @property
    def appendix_prefix(self) -> str:
        return str(self.headings.get("appendix_prefix", "приложение"))

    @property
    def app_letters(self) -> str:
        return str(self.headings.get(
            "app_letters",
            "АБВГДЕЖИКЛМНПРСТУФХЦШЩЭЮЯ",
        ))

    @property
    def special_style_name(self) -> str:
        return str(self.headings.get("special_style", "SpecialHeading"))

    # ------------------------------------------------------------------
    # Фабрики
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: Path) -> "TemplateConfig":
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls(
            name=data.get("meta", {}).get("name", ""),
            headings=data.get("headings", {}),
            equations=data.get("equations", {}),
            page_numbers=data.get("page_numbers", {}),
            toc=data.get("toc", {}),
            features=data.get("features", {}),
        )

    @classmethod
    def from_dir(cls, directory: Path) -> "TemplateConfig":
        return cls.from_file(directory / "config.toml")