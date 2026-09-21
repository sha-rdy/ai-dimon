"""CLI: генерация и проверка reference.docx по спецификациям шаблонов.

Автообнаружение: CLI находит все подпапки templates/<name>/, где
<name> не начинается с _, есть __init__.py, и в модуле есть объект
типа Template. Реестр пополняется сам при добавлении новой папки.

Примеры:
    python -m templates.cli list
    python -m templates.cli generate                    # все шаблоны
    python -m templates.cli generate stp2024_BSUIR
    python -m templates.cli generate stp2024_BSUIR --no-filters
    python -m templates.cli check    stp2024_BSUIR
    python -m templates.cli check-all
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from ._core import Template


# ----------------------------------------------------------------------
# Автообнаружение
# ----------------------------------------------------------------------

def discover() -> dict[str, Template]:
    """Найти все Template-объекты в templates/<name>/__init__.py.

    Пропускает:
      • папки, начинающиеся с _ или .;
      • папки без __init__.py;
      • модули, которые не импортируются (с предупреждением).
    """
    root = Path(__file__).resolve().parent
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
        except Exception as e:
            print(f"⚠️  {module_name}: не удалось импортировать — {e}")
            continue

        # Ищем первый Template-объект в модуле.
        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            obj = getattr(mod, attr)
            if isinstance(obj, Template):
                result[d.name] = obj
                break

    return result


# ----------------------------------------------------------------------
# Команды
# ----------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    registry = discover()
    if not registry:
        print("Шаблоны не найдены в templates/")
        return 1

    print(f"Найдено шаблонов: {len(registry)}\n")
    for name, tmpl in registry.items():
        print(f"  [{name}]  {tmpl.name}")
        print(f"     директория:  {tmpl.directory}")
        print(f"     reference:   {'✅' if tmpl.reference_doc.exists() else '❌'}"
              f"  {tmpl.reference_doc.name}")
        print(f"     filters/:    {'✅' if tmpl.filters_dir.exists() else '❌'}")
        print(f"     filters_src: {'✅' if tmpl.filters_src_dir.exists() else '❌'}")
        print(f"     config.toml: {'✅' if tmpl.config_file.exists() else '❌'}")
        print(f"     preset:      {tmpl.preset.name if tmpl.preset else '—'}")
        print()
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    registry = discover()
    if not registry:
        print("Шаблоны не найдены")
        return 1

    # Без указания имён — генерируем все.
    targets = args.names or list(registry.keys())
    unknown = [n for n in targets if n not in registry]
    if unknown:
        print(f"Неизвестный шаблон: {', '.join(unknown)}")
        print(f"Доступны: {', '.join(registry)}")
        return 1

    exit_code = 0
    for name in targets:
        tmpl = registry[name]
        print(f"\n[{name}]  {tmpl.name}")
        try:
            report = tmpl.generate(
                reference=not args.no_reference,
                filters=not args.no_filters,
            )
        except Exception as e:
            print(f"  ❌ {e}")
            exit_code = 2
            continue

        if "reference" in report:
            print(f"  ✅ reference.docx → {report['reference']}")
        if "filters" in report:
            files = report["filters"]
            print(f"  ✅ filters/      → {len(files)} файлов")
            for f in files:
                print(f"       • {f.name}")

    return exit_code


def cmd_check(args: argparse.Namespace) -> int:
    registry = discover()
    if not registry:
        print("Шаблоны не найдены")
        return 1

    targets = args.names or list(registry.keys())
    unknown = [n for n in targets if n not in registry]
    if unknown:
        print(f"Неизвестный шаблон: {', '.join(unknown)}")
        print(f"Доступны: {', '.join(registry)}")
        return 1

    exit_code = 0
    for name in targets:
        tmpl = registry[name]
        print(f"\n{'=' * 66}")
        print(f"[{name}]  {tmpl.name}")
        print(f"{'=' * 66}\n")

        result = tmpl.check()
        for line in result.report:
            print(line)
        print()
        if result.ok:
            print("  ✅ Все проверки пройдены")
        else:
            print("  ⚠️  Есть замечания — см. ❌ выше")
            exit_code = 2

    return exit_code


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="templates.cli",
        description="Генерация и проверка reference.docx по спецификациям.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="показать все найденные шаблоны")
    p_list.set_defaults(func=cmd_list)

    # generate
    p_gen = sub.add_parser("generate", help="создать reference.docx и/или фильтры")
    p_gen.add_argument(
        "names", nargs="*", metavar="NAME",
        help="имена шаблонов (по умолчанию — все)",
    )
    p_gen.add_argument(
        "--no-reference", action="store_true",
        help="не генерировать reference.docx",
    )
    p_gen.add_argument(
        "--no-filters", action="store_true",
        help="не генерировать Lua-фильтры",
    )
    p_gen.set_defaults(func=cmd_generate)

    # check
    p_chk = sub.add_parser("check", help="проверить reference.docx")
    p_chk.add_argument(
        "names", nargs="*", metavar="NAME",
        help="имена шаблонов (по умолчанию — все)",
    )
    p_chk.set_defaults(func=cmd_check)

    # check-all — алиас на check без аргументов
    p_all = sub.add_parser("check-all", help="проверить все найденные шаблоны")
    p_all.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())