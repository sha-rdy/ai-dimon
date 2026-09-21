"""CLI конвертера Markdown → DOCX.

Использование:
    python -m cli list
    python -m cli info stp2024_BSUIR
    python -m cli convert in.md out.docx --template stp2024_BSUIR
    python -m cli convert in.md out.docx --config custom.toml
    python -m cli convert in.md out.docx --no-toc --toc-depth 3 -v
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from DocxConfigurator import DocxConfigurator
from DocxConverter import DocxConverter
from DocumentTypes import MarkdownDocument, DocxDocument
from IConverter import ConverterError
from templates._core import Template, discover_templates


# ----------------------------------------------------------------------
# Хелперы
# ----------------------------------------------------------------------

def _pick_template(name: str | None) -> tuple[str, Template]:
    """Найти шаблон по имени или вернуть единственный доступный."""
    templates = discover_templates()
    if not templates:
        raise SystemExit("❌ В templates/ не найдено ни одного шаблона")

    if name is not None:
        if name not in templates:
            raise SystemExit(
                f"❌ Неизвестный шаблон {name!r}. "
                f"Доступны: {', '.join(templates)}"
            )
        return name, templates[name]

    if len(templates) == 1:
        return next(iter(templates.items()))

    raise SystemExit(
        f"❌ Доступно несколько шаблонов, укажите --template. "
        f"Варианты: {', '.join(templates)}"
    )


def _build_converter(
    template: Template,
    config_path: Path | None,
    skip_config: bool,
) -> DocxConverter:
    conv = DocxConverter(template=template)
    if not skip_config:
        DocxConfigurator(config_path).configure(conv)
    return conv


def _print_results(results) -> None:
    print("\nПостобработка:")
    for r in results:
        mark = "✅" if r.changes else "·"
        print(f"  {mark} {r.name:18s} {r.changes:4d}")


# ----------------------------------------------------------------------
# Команды
# ----------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    templates = discover_templates()
    if not templates:
        print("Шаблоны не найдены в templates/")
        return 1

    print(f"Найдено шаблонов: {len(templates)}\n")
    for name, tmpl in templates.items():
        ref = "✅" if tmpl.reference_doc.exists() else "❌"
        flt = "✅" if tmpl.filters_dir.exists() else "❌"
        cfg = "✅" if tmpl.config_file.exists() else "❌"
        print(f"  [{name}]  {tmpl.name}")
        print(f"     reference: {ref}   filters: {flt}   config: {cfg}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    name, tmpl = _pick_template(args.name)
    print(f"[{name}]  {tmpl.name}\n")
    print(f"  директория:  {tmpl.directory}")
    print(f"  reference:   {tmpl.reference_doc}")
    print(f"  filters:     {tmpl.filters_dir}")
    print(f"  config.toml: {tmpl.config_file}")

    if tmpl.preset is not None:
        print(f"\n  preset:      {tmpl.preset.name}")
        print(f"  фиксеры:")
        for fix in tmpl.preset.docx_fixes:
            print(f"    • {fix.name}  ({type(fix).__name__})")
        for fix in tmpl.preset.package_fixes:
            print(f"    • {fix.name}  ({type(fix).__name__})")
        if tmpl.preset.pandoc_args:
            print(f"  pandoc args: {' '.join(tmpl.preset.pandoc_args)}")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    # --- Вход/выход ---
    src_path = Path(args.input).resolve()
    dst_path = Path(args.output).resolve()

    if not src_path.exists():
        print(f"❌ Входной файл не найден: {src_path}")
        return 1

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Шаблон и конвертер ---
    _, tmpl = _pick_template(args.template)
    conv = _build_converter(
        template=tmpl,
        config_path=Path(args.config) if args.config else None,
        skip_config=args.no_config,
    )

    # --- Override TOC-параметров ---
    if args.no_toc:
        conv.with_toc = False
    elif args.toc:
        conv.with_toc = True
    if args.toc_depth is not None:
        conv.toc_depth = args.toc_depth
    if args.toc_title is not None:
        conv.toc_title = args.toc_title

    conv.verbose = args.verbose

    if not args.quiet:
        print(f"Шаблон:  {tmpl.name}")
        print(f"Вход:    {src_path}")
        print(f"Выход:   {dst_path}")
        if not args.verbose:
            print()
            print(conv.summary())
            print()

    # --- Конвертация ---
    try:
        src = MarkdownDocument.from_file(src_path)
        dst = DocxDocument.at(dst_path)
        conv.convert(src, dst)
    except ConverterError as e:
        print(f"\n❌ Ошибка конвертации: {e}")
        return 2

    # --- Итог ---
    if not args.quiet:
        size = dst_path.stat().st_size
        print(f"\n✅ Готово: {dst_path}  ({size:,} байт)")

    return 0


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli",
        description="Конвертер Markdown → DOCX по СТП/ГОСТ шаблонам.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="список доступных шаблонов")
    p_list.set_defaults(func=cmd_list)

    # info
    p_info = sub.add_parser("info", help="детали шаблона")
    p_info.add_argument("name", nargs="?", help="имя шаблона")
    p_info.set_defaults(func=cmd_info)

    # convert
    p_cv = sub.add_parser("convert", help="сконвертировать Markdown → DOCX")
    p_cv.add_argument("input", help="входной Markdown-файл")
    p_cv.add_argument("output", help="выходной DOCX-файл")
    p_cv.add_argument(
        "--template", "-t",
        help="имя шаблона (по умолчанию — единственный доступный)",
    )
    p_cv.add_argument(
        "--config", "-c",
        help="путь к config.toml (по умолчанию — из шаблона)",
    )
    p_cv.add_argument(
        "--no-config", action="store_true",
        help="не применять config.toml (использовать дефолты пресета)",
    )
    p_cv.add_argument("--toc", action="store_true", help="включить оглавление")
    p_cv.add_argument("--no-toc", action="store_true", help="выключить оглавление")
    p_cv.add_argument("--toc-depth", type=int, help="глубина TOC")
    p_cv.add_argument("--toc-title", help="заголовок TOC")
    p_cv.add_argument("-v", "--verbose", action="store_true",
                      help="печатать работу каждого фиксера")
    p_cv.add_argument("-q", "--quiet", action="store_true",
                      help="не печатать ничего, кроме ошибок")
    p_cv.set_defaults(func=cmd_convert)

    args = parser.parse_args(argv)

    if getattr(args, "verbose", False):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
        )

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())