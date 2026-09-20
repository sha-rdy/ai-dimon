-- СТП 01-2024, п. 2.2.5: заголовки разделов — ПРОПИСНЫМИ.
-- Все H1 апгрейдятся, включая ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ, СПИСОК, ПРИЛОЖЕНИЕ.
-- Смена стиля на SpecialHeading для спецзаголовков — в Python.

local function upcase(inlines)
  for _, inline in ipairs(inlines) do
    if inline.t == "Str" then
      inline.text = pandoc.text.upper(inline.text)
    elseif inline.t == "Emph" or inline.t == "Strong"
        or inline.t == "Strikeout" or inline.t == "SmallCaps" then
      upcase(inline.content)
    end
  end
end

function Header(el)
  if el.level == 1 then
    upcase(el.content)
  end
  return el
end