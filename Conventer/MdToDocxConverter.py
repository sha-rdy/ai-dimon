# converter/docx_base.py
from pathlib import Path
from typing import ClassVar

import pypandoc

from IConverter import IConverter, ConverterError
from DocumentTypes import MarkdownDocument
from DocumentTypes import DocxDocument


class DocxConverter(IConverter[MarkdownDocument, DocxDocument]):
    """Markdown-документ → DOCX-документ.

    Все элементы оформления управляются флагами-атрибутами.
    Их можно менять на уровне класса (у наследника) или
    у конкретного экземпляра перед вызовом convert().
    """

    REFERENCE_DOC: ClassVar[Path | None] = None
    FILTERS_DIR: ClassVar[Path | None] = None

    MARKDOWN_FORMAT: ClassVar[str] = (
        "markdown+pipe_tables+tex_math_dollars+raw_tex+footnotes+smart-implicit_figures"
    )
    BASE_ARGS: ClassVar[list[str]] = [
        "--standalone",
    ]

    # ---- Отключаемые фичи ----
    # Оглавление
    with_toc: bool = True
    toc_depth: int = 2
    toc_title: str = "СОДЕРЖАНИЕ"

    # Постобработка DOCX (python-docx)
    with_equation_numbers: bool = True
    with_page_numbers: bool = True
    with_field_updates: bool = True

    # Lua-фильтры (маппинг: имя файла без .lua → имя флага)
    FILTER_FLAGS: ClassVar[dict[str, str]] = {
        "00-uppercase-h1":    "with_uppercase_h1",
        "01-section-numbers": "with_section_numbers",
        "03-figure-captions": "with_figure_captions",
        "04-table-captions":  "with_table_captions",
    }

    # Флаги, соответствующие фильтрам
    with_uppercase_h1: bool = True
    with_section_numbers: bool = True
    with_figure_captions: bool = True
    with_table_captions: bool = True

    # ---- Основной метод ----

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
            target.read()
        except RuntimeError as e:
            raise ConverterError(f"Pandoc failed: {e}") from e

    # ---- Сборка аргументов ----

    def _build_args(self) -> list[str]:
        args = list(self.BASE_ARGS)

        if self.REFERENCE_DOC is not None:
            args.append(f"--reference-doc={self.REFERENCE_DOC}")

        if self.with_toc:
            args.append("--toc")
            args.append(f"--toc-depth={self.toc_depth}")
            args.append(f"--metadata=toc-title={self.toc_title}")

        for f in self._filters():
            args.append(f"--lua-filter={f}")

        args.extend(self.extra_args())
        return args

    def _filters(self) -> list[Path]:
        """Вернуть список .lua-фильтров, отфильтрованных по флагам."""
        if self.FILTERS_DIR is None or not self.FILTERS_DIR.exists():
            return []

        result: list[Path] = []
        for f in sorted(self.FILTERS_DIR.glob("*.lua")):
            flag = self.FILTER_FLAGS.get(f.stem)
            if flag is None:
                # Неизвестный фильтр — включаем всегда
                result.append(f)
                continue
            if getattr(self, flag, True):
                result.append(f)
        return result

    def extra_args(self) -> list[str]:
        return []

    # ---- Диагностика ----

    def summary(self) -> str:
        """Человекочитаемая сводка активных фич."""
        features = [
            ("Оглавление",        self.with_toc),
            ("ПРОПИСНЫЕ H1",      self.with_uppercase_h1),
            ("Нумерация разделов", self.with_section_numbers),
            ("Нумерация формул",  self.with_equation_numbers),
            ("Номера страниц",    self.with_page_numbers),
            ("Подписи рисунков",  self.with_figure_captions),
            ("Подписи таблиц",    self.with_table_captions),
            ("Автообновление полей", self.with_field_updates),
        ]
        lines = ["Активные фичи:"]
        for name, enabled in features:
            mark = "✅" if enabled else "⛔"
            lines.append(f"  {mark} {name}")
        return "\n".join(lines)