"""Проверка reference.docx на соответствие СТП 01-2024.

Использование:
    # из любой директории, файл рядом со скриптом:
    python check_reference.py

    # явный путь:
    python check_reference.py path/to/reference.docx

    # найти все reference.docx в проекте и проверить каждый:
    python check_reference.py --scan .
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# ----------------------------- Namespaces -----------------------------

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def q(tag: str) -> str:
    return f"{{{W}}}{tag}"


# ----------------------------- Утилиты -----------------------------

def emu_to_mm(v: str | None) -> float | None:
    return None if v is None else round(int(v) / 36000, 1)


def half_points_to_pt(v: str | None) -> float | None:
    return None if v is None else int(v) / 2


def twips_to_cm(v: str | None) -> float | None:
    return None if v is None else round(int(v) / 567, 2)


def bool_attr(el: ET.Element | None) -> bool:
    if el is None:
        return False
    val = el.get(q("val"))
    return val not in ("0", "false", "off")


# ----------------------------- Требования СТП -----------------------------

# Раздел 2.1.1 и Приложение Л
EXPECTED_SECTION = {
    "top": 20.0, "bottom": 20.0, "left": 30.0, "right": 15.0,
    "footer": 10.0,
}

# Стили, которые Pandoc ищет по имени styleId
NEEDED_STYLES = {
    "Normal", "Heading1", "Heading2", "Heading3",
    "Caption", "TableCaption", "SourceCode", "FirstParagraph",
}

# Ожидаемые параметры для ключевых стилей
EXPECTED_STYLE_PARAMS = {
    "Normal":       {"font": "Times New Roman", "size": 14.0,
                     "align": "both", "indent_cm": 1.25, "line_pt": 18.0},
    "Heading1":     {"font": "Times New Roman", "size": 14.0, "bold": True,
                     "align": "left", "indent_cm": 1.25, "page_break": True},
    "Heading2":     {"font": "Times New Roman", "size": 14.0, "bold": True,
                     "align": "left", "indent_cm": 1.25},
    "Heading3":     {"font": "Times New Roman", "size": 14.0, "bold": True,
                     "align": "left", "indent_cm": 1.25},
    "Caption":      {"font": "Times New Roman", "size": 14.0,
                     "align": "center", "indent_cm": None},
    "TableCaption": {"font": "Times New Roman", "size": 14.0,
                     "align": "left", "indent_cm": 1.25},
    "SourceCode":   {"font": "Courier New", "size": 12.0,
                     "align": "left", "indent_cm": None},
    "FirstParagraph": {"font": "Times New Roman", "size": 14.0,
                       "align": "both", "indent_cm": None},
}

ALIGN_MAP = {
    "both": "по ширине",
    "left": "по левому краю",
    "center": "по центру",
    "right": "по правому краю",
    "distribute": "по ширине (distribute)",
}

# ----------------------------- Парсинг -----------------------------

class StyleInfo:
    def __init__(self, el: ET.Element):
        self.id = el.get(q("styleId"))
        name_el = el.find("w:name", NS)
        self.name = name_el.get(q("val")) if name_el is not None else None
        self.element = el

        rpr = el.find("w:rPr", NS)
        self.font = None
        self.size = None
        self.bold = False
        self.color = None
        if rpr is not None:
            rfonts = rpr.find("w:rFonts", NS)
            if rfonts is not None:
                self.font = rfonts.get(q("ascii"))
            sz = rpr.find("w:sz", NS)
            if sz is not None:
                self.size = half_points_to_pt(sz.get(q("val")))
            self.bold = bool_attr(rpr.find("w:b", NS))
            c = rpr.find("w:color", NS)
            if c is not None:
                self.color = c.get(q("val"))

        ppr = el.find("w:pPr", NS)
        self.align = None
        self.indent_cm = None
        self.line_pt = None
        self.line_rule = None
        self.space_before_pt = None
        self.space_after_pt = None
        self.page_break = False
        self.keep_next = False

        if ppr is not None:
            jc = ppr.find("w:jc", NS)
            if jc is not None:
                self.align = jc.get(q("val"))
            ind = ppr.find("w:ind", NS)
            if ind is not None:
                self.indent_cm = twips_to_cm(ind.get(q("firstLine")))
            sp = ppr.find("w:spacing", NS)
            if sp is not None:
                self.line_pt = half_points_to_pt(sp.get(q("line")))
                self.line_rule = sp.get(q("lineRule"))
                self.space_before_pt = half_points_to_pt(sp.get(q("before")))
                self.space_after_pt = half_points_to_pt(sp.get(q("after")))
            self.page_break = bool_attr(ppr.find(w := "w:pageBreakBefore", NS)
                                        if False else ppr.find("w:pageBreakBefore", NS))
            self.keep_next = bool_attr(ppr.find("w:keepNext", NS))


# ----------------------------- Проверки -----------------------------

def read_xml(path: Path, member: str) -> ET.Element:
    with zipfile.ZipFile(path) as z:
        return ET.fromstring(z.read(member))


def check_section(doc_root: ET.Element) -> tuple[bool, list[str]]:
    issues: list[str] = []
    lines: list[str] = []
    lines.append("Параметры страницы:")

    sect = doc_root.find(".//w:sectPr", NS)
    if sect is None:
        issues.append("sectPr не найден")
        return False, lines

    mar = sect.find("w:pgMar", NS)
    if mar is None:
        issues.append("pgMar не найден")
        return False, lines

    mapping = {"top": "верхнее", "bottom": "нижнее",
               "left": "левое", "right": "правое", "footer": "footer"}

    for key, label in mapping.items():
        got = emu_to_mm(mar.get(q(key)))
        want = EXPECTED_SECTION[key]
        ok = got is not None and abs(got - want) < 0.5
        mark = "✅" if ok else "❌"
        lines.append(f"  {mark} {label:9s}: {got} мм   (ожидается {want})")
        if not ok:
            issues.append(f"{label} поле {got} мм вместо {want} мм")

    return not issues, lines


def check_styles(styles_root: ET.Element) -> tuple[bool, list[str]]:
    issues: list[str] = []
    lines: list[str] = []

    styles: dict[str, StyleInfo] = {}
    for el in styles_root.findall("w:style", NS):
        sid = el.get(q("styleId"))
        if sid:
            styles[sid] = StyleInfo(el)

    lines.append("Стили — наличие:")
    for sid in sorted(NEEDED_STYLES):
        ok = sid in styles
        mark = "✅" if ok else "❌"
        lines.append(f"  {mark} {sid}")
        if not ok:
            issues.append(f"стиль {sid} отсутствует")

    lines.append("")
    lines.append("Стили — параметры:")

    for sid, expected in EXPECTED_STYLE_PARAMS.items():
        if sid not in styles:
            continue
        st = styles[sid]
        lines.append(f"\n  [{sid}]  name='{st.name}'")

        # Шрифт
        if "font" in expected:
            ok = st.font == expected["font"]
            lines.append(f"    {'✅' if ok else '❌'} шрифт: {st.font} "
                         f"(ожидается {expected['font']})")
            if not ok:
                issues.append(f"{sid}: шрифт {st.font} вместо {expected['font']}")

        # Размер
        if "size" in expected:
            ok = st.size is not None and abs(st.size - expected["size"]) < 0.1
            lines.append(f"    {'✅' if ok else '❌'} размер: {st.size} pt "
                         f"(ожидается {expected['size']})")
            if not ok:
                issues.append(f"{sid}: размер {st.size} вместо {expected['size']}")

        # Bold
        if "bold" in expected:
            ok = st.bold == expected["bold"]
            lines.append(f"    {'✅' if ok else '❌'} bold: {st.bold} "
                         f"(ожидается {expected['bold']})")
            if not ok:
                issues.append(f"{sid}: bold={st.bold} вместо {expected['bold']}")

        # Выравнивание
        if "align" in expected:
            got_label = ALIGN_MAP.get(st.align or "", st.align)
            want_label = ALIGN_MAP.get(expected["align"], expected["align"])
            ok = st.align == expected["align"]
            lines.append(f"    {'✅' if ok else '❌'} выравнивание: {got_label} "
                         f"(ожидается {want_label})")
            if not ok:
                issues.append(f"{sid}: выравнивание {st.align} "
                              f"вместо {expected['align']}")

        # Отступ первой строки
        if "indent_cm" in expected:
            want = expected["indent_cm"]
            got = st.indent_cm
            if want is None:
                ok = got is None or got == 0.0
                want_s = "0 / нет"
            else:
                ok = got is not None and abs(got - want) < 0.05
                want_s = f"{want} см"
            lines.append(f"    {'✅' if ok else '❌'} отступ 1-й строки: "
                         f"{got} см (ожидается {want_s})")
            if not ok:
                issues.append(f"{sid}: отступ {got} вместо {want_s}")

        # Межстрочный
        if "line_pt" in expected:
            want = expected["line_pt"]
            ok = (st.line_pt is not None
                  and abs(st.line_pt - want) < 0.1
                  and st.line_rule == "exact")
            got_s = (f"{st.line_pt} pt" if st.line_pt is not None else "—")
            rule_s = st.line_rule or "—"
            lines.append(f"    {'✅' if ok else '❌'} межстрочный: "
                         f"{got_s} / {rule_s} (ожидается {want} pt / exact)")
            if not ok:
                issues.append(f"{sid}: межстрочный {got_s}/{rule_s} "
                              f"вместо {want} pt/exact")

        # Page break before
        if expected.get("page_break"):
            ok = st.page_break
            lines.append(f"    {'✅' if ok else '❌'} page break before: {ok}")
            if not ok:
                issues.append(f"{sid}: нет разрыва страницы перед")

    return not issues, lines


# ----------------------------- Точка входа -----------------------------

def find_default() -> Path:
    """reference.docx рядом со скриптом, или в templates/stp2024/."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / "reference.docx",
        here / "templates" / "stp2024" / "reference.docx",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # вернём «ожидаемый», даже если нет


def scan_root(root: Path) -> list[Path]:
    return sorted(root.rglob("reference.docx"))


def check_one(path: Path) -> bool:
    print(f"\n{'=' * 66}")
    print(f"Файл: {path}")
    print(f"{'=' * 66}\n")

    if not path.exists():
        print("  ❌ Файл не найден")
        return False

    try:
        doc_root = read_xml(path, "word/document.xml")
        styles_root = read_xml(path, "word/styles.xml")
    except KeyError as e:
        print(f"  ❌ Внутри DOCX нет члена {e} — файл повреждён?")
        return False
    except zipfile.BadZipFile:
        print("  ❌ Не DOCX / битый zip")
        return False

    ok_sec, lines_sec = check_section(doc_root)
    for line in lines_sec:
        print(line)

    print()
    ok_sty, lines_sty = check_styles(styles_root)
    for line in lines_sty:
        print(line)

    print()
    if ok_sec and ok_sty:
        print("  ✅ Все проверки пройдены")
    else:
        print("  ⚠️  Есть замечания — см. ❌ выше")
    return ok_sec and ok_sty


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Проверка reference.docx на соответствие СТП 01-2024."
    )
    parser.add_argument("path", nargs="?", type=Path,
                        help="Путь к reference.docx. "
                             "По умолчанию — рядом со скриптом.")
    parser.add_argument("--scan", type=Path, metavar="DIR",
                        help="Найти все reference.docx в директории "
                             "и проверить каждый.")
    args = parser.parse_args()

    if args.scan:
        files = scan_root(args.scan)
        if not files:
            print(f"В {args.scan} не найдено reference.docx")
            return 1
        all_ok = all(check_one(f) for f in files)
        return 0 if all_ok else 2

    target = args.path or find_default()
    ok = check_one(target)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())