"""Загрузка конфигурации шаблона из config.toml."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib   # pip install tomli


@dataclass
class TemplateConfig:
    """Конфигурация одного шаблона."""
    name: str = ""
    section: dict[str, Any] = field(default_factory=dict)
    headings: dict[str, Any] = field(default_factory=dict)
    equations: dict[str, Any] = field(default_factory=dict)
    page_numbers: dict[str, Any] = field(default_factory=dict)
    toc: dict[str, Any] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "TemplateConfig":
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls(
            name=data.get("meta", {}).get("name", ""),
            section=data.get("section", {}),
            headings=data.get("headings", {}),
            equations=data.get("equations", {}),
            page_numbers=data.get("page_numbers", {}),
            toc=data.get("toc", {}),
            features=data.get("features", {}),
        )

    @classmethod
    def from_dir(cls, directory: Path) -> "TemplateConfig":
        cfg = directory / "config.toml"
        if not cfg.exists():
            raise FileNotFoundError(f"config.toml не найден: {cfg}")
        return cls.from_file(cfg)