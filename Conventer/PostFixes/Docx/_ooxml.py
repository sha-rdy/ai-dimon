"""OOXML-утилиты: QName, порядок элементов в pPr/rPr, стили.

Единственный модуль, знающий канонический порядок дочерних элементов
<w:pPr> и <w:rPr>. Остальные модули вставляют элементы через
ppr_insert()/rpr_insert() — это гарантирует, что Word не отвергнет файл.
"""

from __future__ import annotations

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def m(tag: str) -> str:
    return f"{{{M_NS}}}{tag}"


def xml_space() -> str:
    return f"{{{XML_NS}}}space"


# Канонический порядок дочерних элементов <w:pPr> (ECMA-376, §17.3.1.26)
_PPR_ORDER = (
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
    "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
    "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
    "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
    "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
    "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl",
    "divId", "cnfStyle", "rPr", "sectPr", "pPrChange",
)

# Канонический порядок дочерних элементов <w:rPr> (ECMA-376, §17.3.2.28)
_RPR_ORDER = (
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps",
    "strike", "dstrike", "outline", "shadow", "emboss", "imprint",
    "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
    "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect",
    "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang",
    "eastAsianLayout", "specVanish", "oMath",
)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _insert_ordered(parent, el, order: tuple[str, ...]) -> None:
    """Вставить el в parent, соблюдая канонический порядок order."""
    local = _local(el.tag)
    try:
        idx = order.index(local)
    except ValueError:
        parent.append(el)
        return

    successors = set(order[idx + 1:])
    for child in parent:
        if _local(child.tag) in successors:
            child.addprevious(el)
            return
    parent.append(el)


def ppr_insert(pPr, el) -> None:
    _insert_ordered(pPr, el, _PPR_ORDER)


def rpr_insert(rPr, el) -> None:
    _insert_ordered(rPr, el, _RPR_ORDER)


# ----------------------------------------------------------------------
# Стили
# ----------------------------------------------------------------------

def style_ids(style) -> tuple[str, str]:
    """(styleId, name) в нижнем регистре. Пустые строки, если стиля нет."""
    if style is None:
        return "", ""
    return (style.style_id or "").lower(), (style.name or "").lower()


def is_heading(para, level: int = 1) -> bool:
    """H1..H3. SpecialHeading считается H1."""
    sid, sname = style_ids(para.style)
    if level == 1:
        return (
            sid in ("heading1", "specialheading")
            or sname in ("heading 1", "specialheading")
        )
    return (
        sid == f"heading{level}"
        or sname in (f"heading {level}", f"heading{level}")
    )


# ----------------------------------------------------------------------
# Параграфы
# ----------------------------------------------------------------------

def para_text(p) -> str:
    """Текст абзаца по всем <w:t> (включая вложенные)."""
    return "".join((t.text or "") for t in p.findall(".//" + w("t")))