# converter/documents/markdown.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .BaseDoc import BaseDocument


@dataclass
class MarkdownDocument(BaseDocument):
    """Markdown-документ.

    Может быть создан двумя способами:
      MarkdownDocument.from_text("# Привет")
      MarkdownDocument.from_file("report.md")
    """

    _text: str = ""
    _source_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- фабрики ---

    @classmethod
    def from_text(cls, text: str, **metadata: Any) -> "MarkdownDocument":
        return cls(_text=text, metadata=metadata)

    @classmethod
    def from_file(cls, path: str | Path) -> "MarkdownDocument":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        text = p.read_text(encoding="utf-8")
        return cls(_text=text, _source_path=p)

    # --- BaseDocument ---

    def read(self) -> None:
        if self._source_path is None:
            raise ValueError("No source file — created from text")
        self._text = self._source_path.read_text(encoding="utf-8")

    def write(self) -> None:
        if self._source_path is None:
            raise ValueError("No target file — nothing to write to")
        self._source_path.write_text(self._text, encoding="utf-8")

    @property
    def content(self) -> str:
        return self._text

    @property
    def source_path(self) -> Path | None:
        return self._source_path

    def __post_init__(self) -> None:
        if not isinstance(self._text, str):
            raise TypeError("Markdown content must be str")