"""Проверка reference.docx против TemplateSpec."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from .spec import Align, StyleSpec, TemplateSpec

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def _q(tag: str) -> str:
    return f"{{{W}}}{tag}"


# --- конвертация единиц OOXML ---

def _twips_to_mm(v: str | None) -> float | None:
    """w:pgMar / w:pgSz — twips (1/20 pt = 1/1440 inch)."""
    return None if v is None else round(int(v) / 56.6929, 1)


def _twentieths_to_pt(v: str | None) -> float | None:
    """w:line при lineRule='exact'/'atLeast' — двадцатые доли пункта."""
    return None if v is None else int(v) / 20


def _half_points_to_pt(v: str | None) -> float | None:
    """w:sz — half-points (14 pt = 28)."""
    return None if v is None else int(v) / 2


def _twips_to_cm(v: str | None) -> float | None:
    """w:ind/@w:firstLine — twips (1 см ≈ 567 twips)."""
    return None if v is None else round(int(v) / 567, 2)


def _bool_attr(el: ET.Element | None) -> bool:
    if el is None:
        return False
    return el.get(_q("val")) not in ("0", "false", "off")


# ----------------------------- результаты -----------------------------

@dataclass
class Issue:
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.where}] {self.message}"


@dataclass
class CheckResult:
    ok: bool
    issues: list[Issue] = field(default_factory=list)
    report: list[str] = field(default_factory=list)

    def add_line(self, line: str) -> None:
        self.report.append(line)

    def fail(self, where: str, msg: str) -> None:
        self.issues.append(Issue(where, msg))
        self.ok = False


# ----------------------------- чекер -----------------------------

class TemplateChecker:
    """Сравнивает reference.docx с TemplateSpec."""

    def __init__(
        self,
        spec: TemplateSpec,
        tol_mm: float = 0.5,
        tol_pt: float = 0.1,
        tol_cm: float = 0.05,
    ) -> None:
        self.spec = spec
        self.tol_mm = tol_mm
        self.tol_pt = tol_pt
        self.tol_cm = tol_cm

    def check(self, docx_path: Path) -> CheckResult:
        result = CheckResult(ok=True)
        result.add_line(f"Шаблон: {self.spec.name}")
        result.add_line(f"Файл:   {docx_path}")
        result.add_line("")

        if not docx_path.exists():
            result.fail("file", "файл не найден")
            result.add_line("❌ файл не найден")
            return result

        try:
            with zipfile.ZipFile(docx_path) as z:
                doc_root = ET.fromstring(z.read("word/document.xml"))
                styles_root = ET.fromstring(z.read("word/styles.xml"))
        except (zipfile.BadZipFile, KeyError) as e:
            result.fail("file", f"не DOCX / повреждён: {e}")
            result.add_line(f"❌ {e}")
            return result

        self._check_section(doc_root, result)
        result.add_line("")
        self._check_styles(styles_root, result)
        return result

    # --- секция ---

    def _check_section(self, doc_root: ET.Element, result: CheckResult) -> None:
        result.add_line("Параметры страницы:")
        sect = doc_root.find(".//w:sectPr", NS)
        if sect is None:
            result.fail("section", "sectPr не найден")
            return
        mar = sect.find("w:pgMar", NS)
        if mar is None:
            result.fail("section", "pgMar не найден")
            return

        s = self.spec.section
        checks = [
            ("верхнее", "top",    s.margin_top_mm),
            ("нижнее",  "bottom", s.margin_bottom_mm),
            ("левое",   "left",   s.margin_left_mm),
            ("правое",  "right",  s.margin_right_mm),
            ("footer",  "footer", s.footer_offset_mm),
        ]
        for label, key, want in checks:
            got = _twips_to_mm(mar.get(_q(key)))
            ok = got is not None and abs(got - want) <= self.tol_mm
            mark = "✅" if ok else "❌"
            result.add_line(f"  {mark} {label:9s}: {got} мм   (ожидается {want})")
            if not ok:
                result.fail("section", f"{label}={got} мм, ожидается {want}")

    # --- стили ---

    def _check_styles(self, styles_root: ET.Element, result: CheckResult) -> None:
        result.add_line("Стили — наличие:")

        by_id: dict[str, ET.Element] = {}
        for el in styles_root.findall("w:style", NS):
            sid = el.get(_q("styleId"))
            if sid:
                by_id[sid] = el

        for sid in sorted(self.spec.styles):
            ok = sid in by_id
            mark = "✅" if ok else "❌"
            result.add_line(f"  {mark} {sid}")
            if not ok:
                result.fail("styles", f"{sid} отсутствует")

        result.add_line("")
        result.add_line("Стили — параметры:")

        for sid, spec in self.spec.styles.items():
            if sid not in by_id:
                continue
            self._check_style(sid, by_id[sid], spec, result)

    def _check_style(
        self,
        sid: str,
        el: ET.Element,
        spec: StyleSpec,
        result: CheckResult,
    ) -> None:
        name_el = el.find("w:name", NS)
        name = name_el.get(_q("val")) if name_el is not None else "?"
        result.add_line(f"\n  [{sid}]  name='{name}'")

        rpr = el.find("w:rPr", NS) or ET.Element("empty")
        ppr = el.find("w:pPr", NS) or ET.Element("empty")

        # Шрифт
        rfonts = rpr.find("w:rFonts", NS)
        font = rfonts.get(_q("ascii")) if rfonts is not None else None
        self._cmp(result, sid, "шрифт", font, spec.font)

        # Размер (w:sz — half-points)
        sz = rpr.find("w:sz", NS)
        size = _half_points_to_pt(sz.get(_q("val"))) if sz is not None else None
        self._cmp_num(result, sid, "размер", size, spec.size_pt, self.tol_pt, "pt")

        # Bold
        bold = _bool_attr(rpr.find("w:b", NS))
        self._cmp(result, sid, "bold", bold, spec.bold)

        # Выравнивание
        jc = ppr.find("w:jc", NS)
        align = jc.get(_q("val")) if jc is not None else None
        self._cmp(result, sid, "выравнивание", align, spec.align.value)

        # Отступ первой строки (w:ind — twips)
        ind = ppr.find("w:ind", NS)
        indent = _twips_to_cm(ind.get(_q("firstLine"))) if ind is not None else None
        if spec.first_line_indent_cm is None:
            ok = indent is None or indent == 0.0
            mark = "✅" if ok else "❌"
            result.add_line(
                f"    {mark} отступ 1-й строки: {indent} (ожидается нет)"
            )
            if not ok:
                result.fail(sid, f"отступ={indent}, ожидается нет")
        else:
            self._cmp_num(
                result, sid, "отступ 1-й строки",
                indent, spec.first_line_indent_cm, self.tol_cm, "см",
            )

        # Межстрочный (w:line — twentieths при lineRule="exact")
        sp = ppr.find("w:spacing", NS)
        line_pt = _twentieths_to_pt(sp.get(_q("line"))) if sp is not None else None
        rule = sp.get(_q("lineRule")) if sp is not None else None
        if spec.line_spacing_pt is not None:
            ok = (
                line_pt is not None
                and abs(line_pt - spec.line_spacing_pt) <= self.tol_pt
                and rule == "exact"
            )
            mark = "✅" if ok else "❌"
            result.add_line(
                f"    {mark} межстрочный: {line_pt} pt / {rule} "
                f"(ожидается {spec.line_spacing_pt} pt / exact)"
            )
            if not ok:
                result.fail(sid, f"межстрочный {line_pt}/{rule}")

        # Page break before
        if spec.page_break_before:
            pbb = _bool_attr(ppr.find("w:pageBreakBefore", NS))
            mark = "✅" if pbb else "❌"
            result.add_line(f"    {mark} page break before: {pbb}")
            if not pbb:
                result.fail(sid, "нет page break before")

        # Keep with next
        if spec.keep_with_next:
            kn = _bool_attr(ppr.find("w:keepNext", NS))
            mark = "✅" if kn else "❌"
            result.add_line(f"    {mark} keep with next: {kn}")
            if not kn:
                result.fail(sid, "нет keep with next")

    # --- сравнение ---

    def _cmp(self, result: CheckResult, sid: str, label: str, got, want) -> None:
        ok = got == want
        mark = "✅" if ok else "❌"
        result.add_line(f"    {mark} {label}: {got} (ожидается {want})")
        if not ok:
            result.fail(sid, f"{label}={got}, ожидается {want}")

    def _cmp_num(
        self,
        result: CheckResult,
        sid: str,
        label: str,
        got,
        want,
        tol: float,
        unit: str,
    ) -> None:
        ok = got is not None and abs(got - want) <= tol
        mark = "✅" if ok else "❌"
        result.add_line(
            f"    {mark} {label}: {got} {unit} (ожидается {want} {unit})"
        )
        if not ok:
            result.fail(sid, f"{label}={got} {unit}, ожидается {want}")