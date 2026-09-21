"""Тест: Markdown → DOCX с настройкой из config.toml."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Stp2024Configurator import make_stp2024_converter
from DocumentTypes import MarkdownDocument, DocxDocument
from IConverter import ConverterError


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    md_path = ROOT / "scratch" / "test.md"
    out_path = ROOT / "scratch" / "test_output.docx"

    conv = make_stp2024_converter()

    ref = conv.reference_doc
    print("Шаблон:    ", ref)
    print("Существует:", ref is not None and ref.exists())
    print()
    print(conv.summary())
    print()

    if ref is None or not ref.exists():
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
    h1 = sha256(out_path)

    # --- проверка идемпотентности ---
    # Второй прогон на тот же вход: фиксеры не должны ничего изменить.
    # Побайтовое равенство гарантируется тем, что ни один фикс не зовёт
    # mark_dirty()/save(), если правок нет.
    try:
        conv.convert(MarkdownDocument.from_file(md_path), DocxDocument.at(out_path))
    except ConverterError as e:
        print(f"❌ Повторный прогон упал: {e}")
        sys.exit(3)

    h2 = sha256(out_path)
    if h1 == h2:
        print("✅ Идемпотентно: побайтово тот же файл")
    else:
        print("⚠️  Файл отличается после повторного прогона")
        print(f"   до:  {h1}")
        print(f"   после: {h2}")


if __name__ == "__main__":
    main()