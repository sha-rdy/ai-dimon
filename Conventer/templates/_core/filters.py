"""Генерация Lua-фильтров из шаблонов и config.toml.

Шаблоны фильтров лежат в filters_src/*.lua и содержат $placeholder-ы
(см. string.Template). Генерация подставляет значения из config.toml
и пишет итоговые .lua в filters/.

Правила шаблонов:
  • $special_lua_table    → '["введение"] = true, ["заключение"] = true, ...'
  • $app_letters_lua_table → '"А", "Б", "В", ...'
  • $appendix_prefix      → 'приложение'

В самом шаблоне символ $ нужно экранировать как $$.

Использование:
    generate_filters(config, src_dir, dst_dir)
"""

from __future__ import annotations

from pathlib import Path
from string import Template

from .config import TemplateConfig


def generate_filters(
    config: TemplateConfig,
    src_dir: Path,
    dst_dir: Path,
) -> list[Path]:
    """Сгенерировать все *.lua из src_dir в dst_dir.

    Возвращает список записанных файлов. Если src_dir нет — пустой
    список (шаблон может не иметь Lua-фильтров).
    """
    if not src_dir.exists():
        return []

    dst_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    subs = _build_substitutions(config)

    for src in sorted(src_dir.glob("*.lua")):
        text = src.read_text(encoding="utf-8")
        rendered = Template(text).substitute(subs)
        dst = dst_dir / src.name
        dst.write_text(rendered, encoding="utf-8")
        written.append(dst)

    return written


# ----------------------------------------------------------------------
# Внутреннее
# ----------------------------------------------------------------------

def _build_substitutions(config: TemplateConfig) -> dict[str, str]:
    return {
        "special_lua_table":     _special_table(config.special_texts),
        "app_letters_lua_table": _letters_table(config.app_letters),
        "appendix_prefix":       config.appendix_prefix,
    }


def _special_table(texts: frozenset[str]) -> str:
    """frozenset → '["введение"] = true, ["заключение"] = true, ...'"""
    if not texts:
        return ""
    items = ", ".join(f'["{t}"] = true' for t in sorted(texts))
    return items


def _letters_table(letters: str) -> str:
    """'АБВ' → '"А", "Б", "В"'"""
    return ", ".join(f'"{ch}"' for ch in letters)