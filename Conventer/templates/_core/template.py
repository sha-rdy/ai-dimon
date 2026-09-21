"""Template — единая точка входа для одного шаблона.

Собирает в одном объекте всё, что нужно знать о стандарте:
  • spec      — стили и поля reference.docx;
  • preset    — какие фиксеры запускать и с каким контекстом;
  • config    — параметры постобработки (читается лениво);
  • пути      — reference.docx, filters/, config.toml;
  • методы    — generate(), check().

Конкретные шаблоны (STP2024 и др.) создаются в
templates/<name>/__init__.py:

    STP2024 = Template(
        name="СТП 01-2024 (БГУИР)",
        directory=Path(__file__).resolve().parent,
        spec=STP2024_BSUIR_SPEC,
        preset=STP2024_PRESET,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Union

from .checker import CheckResult, TemplateChecker
from .config import TemplateConfig
from .filters import generate_filters
from .generator import TemplateGenerator
from .spec import TemplateSpec

if TYPE_CHECKING:
    # Только для типизации: runtime-зависимости от PostFixes у _core нет.
    from PostFixes.Docx import Preset


@dataclass
class Template:
    name: str
    directory: Path
    spec: TemplateSpec
    preset: "Preset | None" = None

    # ------------------------------------------------------------------
    # Пути
    # ------------------------------------------------------------------

    @property
    def config_file(self) -> Path:
        return self.directory / "config.toml"

    @property
    def reference_doc(self) -> Path:
        return self.directory / "reference.docx"

    @property
    def filters_dir(self) -> Path:
        return self.directory / "filters"

    @property
    def filters_src_dir(self) -> Path:
        return self.directory / "filters_src"

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def load_config(self) -> TemplateConfig:
        return TemplateConfig.from_file(self.config_file)

    # ------------------------------------------------------------------
    # Генерация
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        reference: bool = True,
        filters: bool = True,
    ) -> dict[str, Union[Path, list[Path]]]:
        """Сгенерировать reference.docx и/или Lua-фильтры.

        Возвращает отчёт:
            {"reference": Path, "filters": [Path, ...]}
        Ключи присутствуют, только если соответствующая часть включена.
        """
        report: dict[str, Union[Path, list[Path]]] = {}

        if reference:
            report["reference"] = TemplateGenerator(self.spec).generate(
                self.reference_doc
            )

        if filters:
            cfg = self.load_config()
            report["filters"] = generate_filters(
                cfg, self.filters_src_dir, self.filters_dir
            )

        return report

    # ------------------------------------------------------------------
    # Проверка
    # ------------------------------------------------------------------

    def check(self) -> CheckResult:
        return TemplateChecker(self.spec).check(self.reference_doc)