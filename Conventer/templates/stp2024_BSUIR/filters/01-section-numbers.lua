-- Ручная нумерация заголовков по СТП п. 2.2.2.
-- Формат: N — раздел, N.M — подраздел, N.M.K — пункт.
-- Разделитель — ОБЫЧНЫЙ ПРОБЕЛ, не таб.

local section = 0
local subsection = 0
local subsubsection = 0

local function prepend_number(el, number)
  -- Вставляем в начало: "число" + пробел
  table.insert(el.content, 1, pandoc.Space())
  table.insert(el.content, 1, pandoc.Str(number))
end

function Header(el)
  if el.level == 1 then
    section = section + 1
    subsection = 0
    subsubsection = 0
    prepend_number(el, tostring(section))
  elseif el.level == 2 then
    subsection = subsection + 1
    subsubsection = 0
    prepend_number(el, section .. "." .. subsection)
  elseif el.level == 3 then
    subsubsection = subsubsection + 1
    prepend_number(el, section .. "." .. subsection .. "." .. subsubsection)
  end
  return el
end