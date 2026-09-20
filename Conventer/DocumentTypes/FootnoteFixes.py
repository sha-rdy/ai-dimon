"""Постобработка DOCX: скобка после знака сноски.

СТП 01-2024, п. 2.9.1:
    Знаки сноски выполняют арабскими цифрами со скобкой
    и помещают справа на уровне верхнего обреза слова.

Word рендерит footnoteReference как просто цифру. Добавляем
«)» сразу после ссылки в document.xml и footnotes.xml.
"""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def fix_footnote_marks(docx_path: Path) -> int:
    """Добавить ')' после знака сноски. Возвращает число правок."""
    tmpdir = Path(mkdtemp())
    fixed = 0
    try:
        with ZipFile(docx_path, "r") as z:
            z.extractall(tmpdir)

        # --- document.xml: ссылки на сноски ---
        doc_file = tmpdir / "word" / "document.xml"
        if doc_file.exists():
            tree = etree.parse(str(doc_file))
            root = tree.getroot()
            for ref in root.findall(".//" + _w("footnoteReference")):
                _add_paren_after(ref, root)
                fixed += 1
            tree.write(str(doc_file), xml_declaration=True,
                       encoding="UTF-8", standalone=True)

        # --- footnotes.xml: определения сносок (номер внизу страницы) ---
        fn_file = tmpdir / "word" / "footnotes.xml"
        if fn_file.exists():
            tree = etree.parse(str(fn_file))
            root = tree.getroot()
            for ref in root.findall(".//" + _w("footnoteRef")):
                _add_paren_after(ref, root)
                fixed += 1
            tree.write(str(fn_file), xml_declaration=True,
                       encoding="UTF-8", standalone=True)

        # --- Перепаковка ---
        with ZipFile(docx_path, "w", ZIP_DEFLATED) as zout:
            for f in sorted(tmpdir.rglob("*")):
                if f.is_file():
                    zout.write(f, str(f.relative_to(tmpdir)))
    finally:
        rmtree(tmpdir, ignore_errors=True)

    return fixed


def _add_paren_after(ref_el, root) -> None:
    """Вставить <w:t>)</w:t> сразу после ref_el, в том же run.

    Убедиться, что run имеет superscript (vertAlign).
    """
    run = ref_el.getparent()
    if run is None:
        return

    # Проверяем, не добавили ли уже скобку
    existing = run.findall(_w("t"))
    for t in existing:
        if (t.text or "").endswith(")"):
            return

    # Гарантируем superscript в rPr
    rpr = run.find(_w("rPr"))
    if rpr is None:
        rpr = etree.SubElement(run, _w("rPr"))
        run.insert(0, rpr)
    if rpr.find(_w("vertAlign")) is None:
        va = etree.SubElement(rpr, _w("vertAlign"))
        va.set(_w("val"), "superscript")

    # Создаём <w:t>)</w:t> и вставляем после ref
    t = etree.Element(_w("t"))
    t.text = ")"
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    idx = list(run).index(ref_el)
    run.insert(idx + 1, t)