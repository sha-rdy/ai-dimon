"""Применяет config.toml к любому DocxConverter.

Работает через conv.config_file (путь из TEMPLATE) и conv.PRESET.
Логика не зависит от конкретного стандарта — все параметры либо
в config.toml, либо в preset.py.

Гарантии:
  • Класс-уровень и общий STP2024 не мутируются.
  • Каждый configure() работает на изолированной копии пресета.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from DocxConverter import DocxConverter
from templates._core import TemplateConfig


class DocxConfigurator:
    """Применяет config.toml к экземпляру DocxConverter."""

    def __init__(self, config_path: Path | None = None) -> None:
        # None → использовать config.toml из TEMPLATE конвертера.
        self.config_path = config_path

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def configure(self, conv: DocxConverter) -> DocxConverter:
        cfg_path = self.config_path or conv.config_file
        if not cfg_path.exists():
            return conv

        cfg = TemplateConfig.from_file(cfg_path)

        preset = conv.PRESET.copy() if conv.PRESET is not None else None
        if preset is None:
            return conv

        preset.name = cfg.name or preset.name
        preset.ctx = self._build_ctx(preset.ctx, cfg)
        conv.PRESET = preset

        self._apply_toc(conv, cfg)
        self._apply_filter_flags(conv, cfg)
        return conv

    # ------------------------------------------------------------------
    # Внутреннее: TOC и Lua-флаги
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_toc(conv: DocxConverter, cfg: TemplateConfig) -> None:
        t = cfg.toc
        if "enabled" in t:
            conv.with_toc = bool(t["enabled"])
        if "depth" in t:
            conv.toc_depth = int(t["depth"])
        if "title" in t:
            conv.toc_title = str(t["title"])

    @staticmethod
    def _apply_filter_flags(conv: DocxConverter, cfg: TemplateConfig) -> None:
        f = cfg.features
        for cfg_key, attr in (
            ("uppercase_h1",    "with_uppercase_h1"),
            ("section_numbers", "with_section_numbers"),
            ("figure_captions", "with_figure_captions"),
            ("table_captions",  "with_table_captions"),
        ):
            if cfg_key in f:
                setattr(conv, attr, bool(f[cfg_key]))

    # ------------------------------------------------------------------
    # Внутреннее: сборка FixContext
    # ------------------------------------------------------------------

    @staticmethod
    def _build_ctx(base, cfg: TemplateConfig):
        changes: dict = {}

        h = cfg.headings
        if "special" in h:
            changes["special_texts"] = cfg.special_texts
        if "appendix_prefix" in h:
            changes["appendix_prefix"] = cfg.appendix_prefix
        if "app_letters" in h:
            changes["app_letters"] = cfg.app_letters
        if "special_style" in h:
            changes["special_style_name"] = cfg.special_style_name

        e = cfg.equations
        if "tab_cm" in e:
            changes["eq_tab_cm"] = float(e["tab_cm"])

        pn = cfg.page_numbers
        if "align" in pn:
            changes["pn_align"] = str(pn["align"])
        if "font" in pn:
            changes["pn_font"] = str(pn["font"])
        if "size_pt" in pn:
            changes["pn_size_pt"] = float(pn["size_pt"])

        changes["enabled"] = DocxConfigurator._build_enabled(base, cfg)
        return replace(base, **changes)

    @staticmethod
    def _build_enabled(base, cfg: TemplateConfig) -> dict[str, bool]:
        enabled = dict(base.enabled)
        f = cfg.features

        for cfg_key, fix_name in (
            ("special_headings", "special_headings"),
            ("equation_numbers", "equations"),
            ("field_updates",    "field_updates"),
            ("table_fixes",      "tables"),
            ("list_fixes",       "lists"),
            ("footnote_marks",   "footnote_marks"),
        ):
            if cfg_key in f:
                enabled[fix_name] = bool(f[cfg_key])

        if "enabled" in cfg.page_numbers:
            enabled["page_numbers"] = bool(cfg.page_numbers["enabled"])

        return enabled