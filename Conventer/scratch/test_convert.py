"""Тест: Markdown → DOCX с настройкой из config.toml."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Stp2024Configurator import make_stp2024_converter
from DocumentTypes import MarkdownDocument, DocxDocument
from IConverter import ConverterError


def main() -> None:
    md_path = ROOT / "scratch" / "test.md"
    out_path = ROOT / "scratch" / "test_output.docx"

    conv = make_stp2024_converter()

    print("Шаблон:    ", conv.REFERENCE_DOC)
    print("Существует:", conv.REFERENCE_DOC.exists())
    print()
    print(conv.summary())
    print()

    if not conv.REFERENCE_DOC.exists():
        print("❌ reference.docx не найден")
        sys.exit(1)

    md = MarkdownDocument.from_file(md_path)
    docx = DocxDocument.at(out_path)

    try:
        conv.convert(md, docx)
    except ConverterError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(2)

    print()
    print(f"✅ Готово: {out_path}")
    print(f"   Размер: {out_path.stat().st_size} байт")


if __name__ == "__main__":
    main()