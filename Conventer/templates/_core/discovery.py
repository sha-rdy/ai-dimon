"""Автообнаружение шаблонов в templates/<name>/__init__.py."""

from __future__ import annotations

import importlib
from pathlib import Path

from .template import Template


def discover_templates(root: Path | None = None) -> dict[str, Template]:
    """Найти все Template-объекты в подпакетах templates/.

    Пропускает папки, начинающиеся с _ или ., и папки без __init__.py.
    Возвращает dict: {имя_папки: Template}.
    """
    if root is None:
        root = Path(__file__).resolve().parent.parent

    result: dict[str, Template] = {}

    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith("_") or d.name.startswith("."):
            continue
        if not (d / "__init__.py").exists():
            continue

        module_name = f"templates.{d.name}"
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            continue

        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            obj = getattr(mod, attr)
            if isinstance(obj, Template):
                result[d.name] = obj
                break

    return result