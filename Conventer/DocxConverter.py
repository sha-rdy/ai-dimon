"""Универсальный Markdown → DOCX конвертер.

Специфика стандарта задаётся одним атрибутом класса:
  • TEMPLATE — Template из templates._core.

Template содержит всё: spec (стили reference.docx), preset
(фиксеры + FixContext), пути к reference.docx/filters/config.toml.
DocxConverter берёт preset из TEMPLATE.preset при создании
экземпляра. Configurator может переопределить self.PRESET.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pypandoc

from IConverter import IConverter, ConverterError
from DocumentTypes import MarkdownDocument, DocxDocument
from PostFixes.Docx import DocxPipeline, Preset
from templates._core import Template


class DocxConverter(IConverter[MarkdownDocument, DocxDocument]):
    """Markdown-документ → DOCX-документ."""

    # --- Шаблон (обязателен для наследников) ---
    TEMPLATE: ClassVar[Template | None] = None

    # --- Pandoc: формат входа и базовые аргументы ---
    MARKDOWN_FORMAT: ClassVar[str] = (
        "markdown+pipe_tables+tex_math_dollars+raw_tex+footnotes+smart-implicit_figures"
    )
    BASE_ARGS: ClassVar[list[str]] = ["--standalone"]

    # --- Оглавление (pandoc-опция, не постобработка) ---
    with_toc: bool = True
    toc_depth: int = 2
    toc_title: str = "СОДЕРЖАНИЕ"

    # --- Lua-фильтры: имя файла без .lua → имя атрибута ---
    FILTER_FLAGS: ClassVar[dict[str, str]] = {
        "00-uppercase-h1":    "with_uppercase_h1",
        "01-section-numbers": "with_section_numbers",
        "03-figure-captions": "with_figure_captions",
        "04-table-captions":  "with_table_captions",
    }
    with_uppercase_h1: bool = True
    with_section_numbers: bool = True
    with_figure_captions: bool = True
    with_table_captions: bool = True

    # ------------------------------------------------------------------
    # Инициализация
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        # PRESET — экземплярный. Берём из TEMPLATE.preset, чтобы
        # Configurator мог переопределить через conv.PRESET = ...
        # без влияния на класс.
        self.PRESET: Preset | None = (
            self.TEMPLATE.preset if self.TEMPLATE is not None else None
        )

    # ------------------------------------------------------------------
    # Публичные свойства
    # ------------------------------------------------------------------

    @property
    def reference_doc(self) -> Path | None:
        return self.TEMPLATE.reference_doc if self.TEMPLATE else None

    @property
    def filters_dir(self) -> Path | None:
        return self.TEMPLATE.filters_dir if self.TEMPLATE else None

    @property
    def config_file(self) -> Path | None:
        return self.TEMPLATE.config_file if self.TEMPLATE else None

    # ------------------------------------------------------------------
    # Конвертация
    # ------------------------------------------------------------------

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

        if self.PRESET is not None:
            pipeline = DocxPipeline(
                docx_fixes=self.PRESET.docx_fixes,
                package_fixes=self.PRESET.package_fixes,
                ctx=self.PRESET.ctx,
            )
            pipeline.run(target.path)

    # ------------------------------------------------------------------
    # Аргументы pandoc
    # ------------------------------------------------------------------

    def _build_args(self) -> list[str]:
        args = list(self.BASE_ARGS)

        ref = self.reference_doc
        if ref is not None:
            args.append(f"--reference-doc={ref}")

        if self.with_toc:
            args.append("--toc")
            args.append(f"--toc-depth={self.toc_depth}")
            args.append(f"--metadata=toc-title={self.toc_title}")

        for f in self._filters():
            args.append(f"--lua-filter={f}")

        if self.PRESET is not None:
            args.extend(self.PRESET.pandoc_args)

        args.extend(self.extra_args())
        return args

    def _filters(self) -> list[Path]:
        d = self.filters_dir
        if d is None or not d.exists():
            return []
        result: list[Path] = []
        for f in sorted(d.glob("*.lua")):
            flag = self.FILTER_FLAGS.get(f.stem)
            if flag is None or getattr(self, flag, True):
                result.append(f)
        return result

    def extra_args(self) -> list[str]:
        """Точка расширения: доп. аргументы pandoc от наследника."""
        return []

    # ------------------------------------------------------------------
    # Диагностика
    # ------------------------------------------------------------------

    def summary(self) -> str:
        preset_name = self.PRESET.name if self.PRESET else "—"
        lines = [f"Пресет:  {preset_name}", "", "Pandoc:"]
        for name, enabled in (
            ("Оглавление",       self.with_toc),
            ("ПРОПИСНЫЕ H1",     self.with_uppercase_h1),
            ("Номера разделов",  self.with_section_numbers),
            ("Подписи рисунков", self.with_figure_captions),
            ("Подписи таблиц",   self.with_table_captions),
        ):
            lines.append(f"  {'✅' if enabled else '⛔'} {name}")

        if self.PRESET:
            lines.append("")
            lines.append("Постобработка:")
            for fix in (*self.PRESET.docx_fixes, *self.PRESET.package_fixes):
                on = self.PRESET.ctx.is_enabled(fix.name)
                lines.append(f"  {'✅' if on else '⛔'} {fix.name}")
        return "\n".join(lines)