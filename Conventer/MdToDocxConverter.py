# converter/docx_base.py
from pathlib import Path
from typing import ClassVar

import pypandoc

from IConverter import IConverter, ConverterError
from DocumentTypes import MarkdownDocument
from DocumentTypes import DocxDocument


class DocxConverter(IConverter[MarkdownDocument, DocxDocument]):
    """Markdown-документ → DOCX-документ."""

    REFERENCE_DOC: ClassVar[Path|None] = None
    FILTERS_DIR: ClassVar[Path | None] = None

    MARKDOWN_FORMAT: ClassVar[str] = (
        "markdown+pipe_tables+tex_math_dollars+implicit_figures+raw_tex+footnotes+smart"
    )
    BASE_ARGS: ClassVar[list[str]] = [
        "--toc",
        "--toc-depth=2",
        "--standalone",
    ]

    def convert(self, source: MarkdownDocument, target: DocxDocument) -> None:
        args = self._build_args()
        try:
            pypandoc.convert_text(
                source.content,
                to="docx",
                format=self.MARKDOWN_FORMAT,
                outputfile=str(target.path),
                extra_args=args,
            )
            target.read()  # пометить, что файл теперь существует
        except RuntimeError as e:
            raise ConverterError(f"Pandoc failed: {e}") from e

    def _build_args(self) -> list[str]:
        args = list(self.BASE_ARGS)
        if self.REFERENCE_DOC is not None:
            args.append(f"--reference-doc={self.REFERENCE_DOC}")

        for f in self._filters():
            args.append(f"--lua-filter={f}")
        args.extend(self.extra_args())
        return args

    def _filters(self) -> list[Path]:
        if self.FILTERS_DIR is None or not self.FILTERS_DIR.exists():
            return []
        return sorted(self.FILTERS_DIR.glob("*.lua"))

    def extra_args(self) -> list[str]:
        return []