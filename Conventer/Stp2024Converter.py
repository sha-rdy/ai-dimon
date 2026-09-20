from pathlib import Path
from typing import ClassVar

from MdToDocxConverter import DocxConverter


class Stp2024Converter(DocxConverter):
    """Конвертер Markdown → DOCX по СТП 01–2024 (БГУИР)."""

    _TEMPLATE_DIR: ClassVar[Path] = (
        Path(__file__).resolve().parent / "templates" / "stp2024_BSUIR"
    )

    REFERENCE_DOC: ClassVar[Path] = _TEMPLATE_DIR / "reference.docx"
    FILTERS_DIR: ClassVar[Path] = _TEMPLATE_DIR / "filters"

    def extra_args(self) -> list[str]:
        return [
            "--highlight-style=tango",
        ]