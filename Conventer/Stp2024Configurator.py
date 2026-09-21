"""Читает config.toml и применяет параметры к Stp2024Converter.

Класс-пресет Stp2024Converter уже имеет корректные значения по умолчанию.
Configurator — точка расширения: переопределить параметры без правки
Python-кода.

Гарантии:
  • Класс-уровень STP2024 (Template) не мутируется.
  • Каждый вызов create() возвращает конвертер со своей изолированной
    копией пресета (Preset.copy() клонирует списки и ctx.enabled).
  • Если в config.toml чего-то нет — берётся значение из STP2024.preset.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from Stp2024Converter import Stp2024Converter
from templates._core import TemplateConfig


class Stp2024Configurator:
    """Применяет config.toml к экземпляру Stp2024Converter."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Stp2024Converter.TEMPLATE.config_file

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def load(self) -> TemplateConfig:
        """Прочитать config.toml."""
        return TemplateConfig.from_file(self.config_path)

    def create(self) -> Stp2024Converter:
        """Создать новый конвертер и настроить его из config.toml."""
        return self.configure(Stp2024Converter())

    def configure(self, conv: Stp2024Converter) -> Stp2024Converter:
        """Применить настройки из config.toml к существующему конвертеру."""
        cfg = self.load()

        preset = conv.PRESET.copy() if conv.PRESET is not None else None
        if preset is None:
            return conv

        preset.name = cfg.name or preset.name
        preset.ctx = self._build_ctx(preset.ctx, cfg)

        # Присваивание на ЭКЗЕМПЛЯРЕ. Класс-уровень не трогаем.
        conv.PRESET = preset

        self._apply_toc(conv, cfg)
        self._apply_filter_flags(conv, cfg)

        return conv

    # ------------------------------------------------------------------
    # Внутреннее: TOC и Lua-флаги (живут на конвертере, не в Preset)
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_toc(conv: Stp2024Converter, cfg: TemplateConfig) -> None:
        t = cfg.toc
        if "enabled" in t:
            conv.with_toc = bool(t["enabled"])
        if "depth" in t:
            conv.toc_depth = int(t["depth"])
        if "title" in t:
            conv.toc_title = str(t["title"])

    @staticmethod
    def _apply_filter_flags(conv: Stp2024Converter, cfg: TemplateConfig) -> None:
        """Lua-флаги маппятся на атрибуты конвертера напрямую."""
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

        # Используем свойства TemplateConfig — они возвращают дефолт,
        # если ключа нет в config.toml. Проверяем наличие ключа в headings,
        # чтобы не перезаписать значение из пресета дефолтом.
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

        changes["enabled"] = Stp2024Configurator._build_enabled(base, cfg)
        return replace(base, **changes)

    @staticmethod
    def _build_enabled(base, cfg: TemplateConfig) -> dict[str, bool]:
        """Слить флаги фиксеров из base.enabled и config.toml.

        Ключи cfg.features, соответствующие Lua-фильтрам
        (uppercase_h1, section_numbers, figure_captions, table_captions),
        сюда не попадают — они управляют конвертером напрямую.
        """
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

        # Отдельная секция [page_numbers] имеет свой enabled.
        if "enabled" in cfg.page_numbers:
            enabled["page_numbers"] = bool(cfg.page_numbers["enabled"])

        return enabled


# ----------------------------------------------------------------------
# Удобная фабрика
# ----------------------------------------------------------------------

def make_stp2024_converter(config_path: Path | None = None) -> Stp2024Converter:
    """Создать конвертер, настроенный из config.toml."""
    return Stp2024Configurator(config_path).create()