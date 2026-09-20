# converter/documents/docx.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .BaseDoc import BaseDocument


@dataclass
class DocxDocument(BaseDocument):
    """DOCX-документ.

    Создаётся пустым с целевым путём:
        DocxDocument.at("report.docx")

    Или оборачивает существующий файл:
        DocxDocument.from_file("report.docx")
    """

    path: Path|None = None 
    metadata: dict[str, Any] = field(default_factory=dict)
    _exists: bool = False

    @classmethod
    def at(cls, path: str | Path, **metadata: Any) -> "DocxDocument":
        """Целевой документ — файла ещё нет, но он появится."""
        return cls(path=Path(path), metadata=metadata, _exists=False)

    @classmethod
    def from_file(cls, path: str | Path, **metadata: Any) -> "DocxDocument":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        return cls(path=p, metadata=metadata, _exists=True)

    # --- BaseDocument ---

    def read(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self._exists = True

    def write(self) -> None:
        if not self._exists:
            raise RuntimeError("Nothing to write — file doesn't exist yet")

    @property
    def content(self) -> Path:
        """Для DOCX содержимое — это путь к файлу.

        Если нужен доступ к параграфам — используйте .open() (см. ниже).
        """
        return self.path

    # --- дополнительный API для постобработки ---

    def open(self):
        """Открыть через python-docx для постобработки."""
        from docx import Document
        return Document(str(self.path))

    def __post_init__(self) -> None:
        if self.path.suffix.lower() != ".docx":
            raise ValueError(f"Expected .docx, got {self.path.suffix}")