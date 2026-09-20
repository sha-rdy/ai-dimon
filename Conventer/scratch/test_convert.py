"""Тест: Markdown → DOCX через Stp2024Converter.

Запуск из папки Conventer/:
    python scratch/test_convert.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Stp2024Converter import Stp2024Converter
from DocumentTypes import MarkdownDocument, DocxDocument
from IConverter import ConverterError


def main() -> None:
    md_path = ROOT / "scratch" / "test.md"
    out_path = ROOT / "scratch" / "test_output.docx"

    conv = Stp2024Converter()
    print("Шаблон:    ", conv.REFERENCE_DOC)
    print("Существует:", conv.REFERENCE_DOC.exists())
    print("Фильтры:   ", conv.FILTERS_DIR)
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

    print(f"✅ Готово: {out_path}")
    print(f"   Размер: {out_path.stat().st_size} байт")


if __name__ == "__main__":
    main()