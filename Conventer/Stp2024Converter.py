from pathlib import Path
from typing import ClassVar

from MdToDocxConverter import DocxConverter
from DocumentTypes.EquationNumbering import number_equations


class Stp2024Converter(DocxConverter):
    """Конвертер Markdown → DOCX по СТП 01–2024 (БГУИР)."""

    _TEMPLATE_DIR: ClassVar[Path] = (
        Path(__file__).resolve().parent / "templates" / "stp2024_BSUIR"
    )

    REFERENCE_DOC: ClassVar[Path] = _TEMPLATE_DIR / "reference.docx"
    FILTERS_DIR: ClassVar[Path] = _TEMPLATE_DIR / "filters"

    def extra_args(self) -> list[str]:
        return ["--syntax-highlighting=tango"]

    def convert(self, source, target) -> None:
        super().convert(source, target)
        n = number_equations(target.path)
        print(f"Пронумеровано формул: {n}")