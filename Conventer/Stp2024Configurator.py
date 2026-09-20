"""Загрузка config.toml и настройка Stp2024Converter."""

from __future__ import annotations

from pathlib import Path

from Stp2024Converter import Stp2024Converter
from templates.loader import TemplateConfig


class Stp2024Configurator:
    """Читает config.toml и применяет параметры к Stp2024Converter."""

    _TEMPLATE_DIR: Path = (
        Path(__file__).resolve().parent / "templates" / "stp2024_BSUIR"
    )
    _CONFIG_FILE: Path = _TEMPLATE_DIR / "config.toml"

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or self._CONFIG_FILE

    def load(self) -> TemplateConfig:
        return TemplateConfig.from_file(self.config_path)

    def create(self) -> Stp2024Converter:
        conv = Stp2024Converter()
        cfg = self.load()
        self._apply(conv, cfg)
        return conv

    def configure(self, conv: Stp2024Converter) -> Stp2024Converter:
        """Применить настройки к существующему конвертеру."""
        cfg = self.load()
        self._apply(conv, cfg)
        return conv

    # --- внутреннее ---

    @staticmethod
    def _apply(conv: Stp2024Converter, cfg: TemplateConfig) -> None:
        # --- Заголовки ---
        h = cfg.headings
        if "special" in h:
            conv.special_headings = tuple(h["special"])
        if "appendix_prefix" in h:
            conv.appendix_prefix = str(h["appendix_prefix"])
        if "special_style" in h:
            conv.special_style_name = str(h["special_style"])

        # --- Формулы ---
        e = cfg.equations
        if "tab_cm" in e:
            conv.eq_tab_cm = float(e["tab_cm"])

        # --- TOC ---
        t = cfg.toc
        if "enabled" in t:
            conv.with_toc = bool(t["enabled"])
        if "depth" in t:
            conv.toc_depth = int(t["depth"])
        if "title" in t:
            conv.toc_title = str(t["title"])

        # --- Номера страниц ---
        pn = cfg.page_numbers
        if "align" in pn:
            conv.pn_align = str(pn["align"])
        if "font" in pn:
            conv.pn_font = str(pn["font"])
        if "size_pt" in pn:
            conv.pn_size_pt = float(pn["size_pt"])
        if "enabled" in pn:
            conv.with_page_numbers = bool(pn["enabled"])

        # --- Фичи ---
        f = cfg.features
        conv.with_uppercase_h1     = bool(f.get("uppercase_h1", True))
        conv.with_section_numbers  = bool(f.get("section_numbers", True))
        conv.with_equation_numbers = bool(f.get("equation_numbers", True))
        conv.with_figure_captions  = bool(f.get("figure_captions", True))
        conv.with_table_captions   = bool(f.get("table_captions", True))
        conv.with_special_headings = bool(f.get("special_headings", True))
        conv.with_field_updates    = bool(f.get("field_updates", True))


# --- Удобная фабрика ---

def make_stp2024_converter() -> Stp2024Converter:
    """Создать конвертер, настроенный из config.toml."""
    return Stp2024Configurator().create()