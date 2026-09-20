from pathlib import Path
from typing import ClassVar

from MdToDocxConverter import DocxConverter
from DocumentTypes.EquationNumbering import number_equations
from DocumentTypes.PostProcess import add_page_numbers, enable_field_updates
from DocumentTypes.SpecialHeadings import fix_special_headings


class Stp2024Converter(DocxConverter):
    """Конвертер Markdown → DOCX по СТП 01–2024 (БГУИР).

    Никакой логики чтения конфига — только конвертация.
    Параметры приходят извне (см. Stp2024Configurator).
    """

    _TEMPLATE_DIR: ClassVar[Path] = (
        Path(__file__).resolve().parent / "templates" / "stp2024_BSUIR"
    )

    REFERENCE_DOC: ClassVar[Path] = _TEMPLATE_DIR / "reference.docx"
    FILTERS_DIR: ClassVar[Path] = _TEMPLATE_DIR / "filters"

    # --- Атрибуты, которые настраивает Configurator ---
    special_headings: tuple[str, ...] = ()
    appendix_prefix: str = "приложение"
    special_style_name: str = "SpecialHeading"
    eq_tab_cm: float = 16.5

    pn_align: str = "right"
    pn_font: str = "Times New Roman"
    pn_size_pt: float = 14.0

    def extra_args(self) -> list[str]:
        return ["--syntax-highlighting=tango"]

    def convert(self, source, target) -> None:
        super().convert(source, target)

        if getattr(self, "with_special_headings", True):
            n = fix_special_headings(
                target.path,
                style_name=self.special_style_name,
                special_texts=frozenset(self.special_headings),
                appendix_prefix=self.appendix_prefix,
            )
            print(f"Спецзаголовки переоформлены: {n}")

        if self.with_equation_numbers:
            n = number_equations(target.path, tab_cm=self.eq_tab_cm)
            print(f"Пронумеровано формул: {n}")

        if self.with_page_numbers:
            add_page_numbers(
                target.path,
                align=self.pn_align,
                font=self.pn_font,
                size_pt=self.pn_size_pt,
            )
            print("Нумерация страниц: добавлена")

        if self.with_toc and self.with_field_updates:
            enable_field_updates(target.path)
            print("Автообновление полей: включено")