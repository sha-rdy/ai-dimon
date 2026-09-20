"""CLI: generate / check reference.docx по спецификации шаблона.

Примеры:
    python -m templates.cli generate stp2024
    python -m templates.cli check stp2024
    python -m templates.cli generate stp2024 --out path/to/reference.docx
    python -m templates.cli check-all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checker import TemplateChecker
from .generator import TemplateGenerator
from .spec import TemplateSpec


# Реестр спецификаций. Пополняется по мере добавления стандартов.
def _registry() -> dict[str, TemplateSpec]:
    from .stp2024_BSUIR.spec import STP2024_BSUIR_SPEC
    return {
        "stp2024_BSUIR": STP2024_BSUIR_SPEC,
    }


def _templates_root() -> Path:
    return Path(__file__).resolve().parent


def _reference_path(style_name: str) -> Path:
    return _templates_root() / style_name / "reference.docx"


# ----------------------------- команды -----------------------------

def cmd_generate(args: argparse.Namespace) -> int:
    registry = _registry()
    if args.style not in registry:
        print(f"Неизвестный стиль '{args.style}'. "
              f"Доступны: {', '.join(registry)}")
        return 1

    spec = registry[args.style]
    out = Path(args.out) if args.out else _reference_path(args.style)

    TemplateGenerator(spec).generate(out)
    print(f"OK: сгенерирован {out}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    registry = _registry()
    if args.style not in registry:
        print(f"Неизвестный стиль '{args.style}'. "
              f"Доступны: {', '.join(registry)}")
        return 1

    spec = registry[args.style]
    path = Path(args.path) if args.path else _reference_path(args.style)

    result = TemplateChecker(spec).check(path)
    for line in result.report:
        print(line)
    print()
    if result.ok:
        print("✅ Все проверки пройдены")
        return 0
    print("⚠️  Есть замечания — см. ❌ выше")
    return 2


def cmd_check_all(args: argparse.Namespace) -> int:
    registry = _registry()
    exit_code = 0
    for style_name, spec in registry.items():
        path = _reference_path(style_name)
        print(f"\n{'=' * 66}")
        print(f"[{style_name}]  {path}")
        print(f"{'=' * 66}\n")
        result = TemplateChecker(spec).check(path)
        for line in result.report:
            print(line)
        print()
        if not result.ok:
            exit_code = 2
    return exit_code


# ----------------------------- main -----------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="templates.cli",
        description="Генерация и проверка reference.docx по спецификациям.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="создать reference.docx")
    p_gen.add_argument("style", help="имя стиля (например, stp2024)")
    p_gen.add_argument("--out", help="путь для записи (по умолчанию — рядом со spec)")
    p_gen.set_defaults(func=cmd_generate)

    p_chk = sub.add_parser("check", help="проверить reference.docx")
    p_chk.add_argument("style", help="имя стиля")
    p_chk.add_argument("--path", help="путь к reference.docx (по умолчанию — рядом)")
    p_chk.set_defaults(func=cmd_check)

    p_all = sub.add_parser("check-all", help="проверить все зарегистрированные стили")
    p_all.set_defaults(func=cmd_check_all)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())