"""Постобработка DOCX: автообновление полей, нумерация страниц.

Применяется после всех Pandoc-преобразований и Lua-фильтров,
когда нужно править сам OOXML.
"""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


# ----------------------------------------------------------------
# Автообновление полей (TOC)
# ----------------------------------------------------------------

def enable_field_updates(docx_path: Path) -> None:
    """Включить автообновление полей при открытии DOCX.

    Добавляет <w:updateFields w:val="true"/> в word/settings.xml.
    Word при открытии спросит «Обновить поля?» → пользователь
    нажимает Да → TOC заполняется.
    """
    tmpdir = Path(mkdtemp())
    try:
        with ZipFile(docx_path, "r") as z:
            z.extractall(tmpdir)

        settings_file = tmpdir / "word" / "settings.xml"
        if not settings_file.exists():
            # Если вдруг нет — не падаем, просто пропускаем
            return

        tree = etree.parse(str(settings_file))
        root = tree.getroot()

        uf = root.find("w:updateFields", NS)
        if uf is None:
            uf = etree.SubElement(root, f"{{{W_NS}}}updateFields")
        uf.set(f"{{{W_NS}}}val", "true")

        tree.write(
            str(settings_file),
            xml_declaration=True,
            encoding="UTF-8",
            standalone=True,
        )

        # Перепаковать
        with ZipFile(docx_path, "w", ZIP_DEFLATED) as zout:
            for f in sorted(tmpdir.rglob("*")):
                if f.is_file():
                    arcname = f.relative_to(tmpdir)
                    zout.write(f, str(arcname))
    finally:
        rmtree(tmpdir, ignore_errors=True)


# ----------------------------------------------------------------
# Нумерация страниц
# ----------------------------------------------------------------

def add_page_numbers(
    docx_path: Path,
    align: str = "right",
    font: str = "Times New Roman",
    size_pt: float = 14.0,
    section_index: int = 0,
) -> None:
    """Добавить номер страницы в футер указанной секции.

    Позиция по вертикали задаётся через footer_distance
    в reference.docx (10 мм, см. SectionSpec.footer_offset_mm).
    """
    doc = Document(str(docx_path))
    if section_index >= len(doc.sections):
        return
    section = doc.sections[section_index]

    footer = section.footer
    footer.is_linked_to_previous = False

    # Берём первый параграф футера или создаём
    if footer.paragraphs:
        p = footer.paragraphs[0]
    else:
        p = footer.add_paragraph()

    # Очищаем существующие runs
    for r in list(p.runs):
        r._element.getparent().remove(r._element)

    # Выравнивание
    align_map = {
        "left":   WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right":  WD_ALIGN_PARAGRAPH.RIGHT,
    }
    p.alignment = align_map.get(align, WD_ALIGN_PARAGRAPH.RIGHT)

    # Поле PAGE: <w:fldChar begin/> <w:instrText> PAGE </w:instrText>
    #            <w:fldChar separate/> <w:t>1</w:t> <w:fldChar end/>
    run = p.add_run()
    r = run._r

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    r.append(fld_begin)

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    r.append(instr)

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    r.append(fld_sep)

    placeholder = OxmlElement("w:t")
    placeholder.text = "1"
    r.append(placeholder)

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    r.append(fld_end)

    # Шрифт
    run.font.name = font
    run.font.size = Pt(size_pt)

    doc.save(str(docx_path))