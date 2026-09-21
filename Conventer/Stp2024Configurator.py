"""Удобная обёртка над DocxConfigurator для СТП 01-2024.

Вся логика — в DocxConfigurator. Здесь только фабрика для
Stp2024Converter и путь к config.toml по умолчанию.
"""

from __future__ import annotations

from pathlib import Path

from DocxConfigurator import DocxConfigurator
from Stp2024Converter import Stp2024Converter
from templates._core import TemplateConfig


class Stp2024Configurator(DocxConfigurator):
    def __init__(self, config_path: Path | None = None) -> None:
        if config_path is None:
            config_path = Stp2024Converter.DEFAULT_TEMPLATE.config_file
        super().__init__(config_path)

    def create(self) -> Stp2024Converter:
        conv = Stp2024Converter()
        self.configure(conv)
        return conv


def make_stp2024_converter(config_path: Path | None = None) -> Stp2024Converter:
    """Создать конвертер, настроенный из config.toml."""
    return Stp2024Configurator(config_path).create()