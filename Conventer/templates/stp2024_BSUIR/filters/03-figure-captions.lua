-- СТП 01-2024, п. 2.5.5: подпись рисунка
-- Формат: «Рисунок N.M – Название», по центру, без точки.
-- Работает при отключённом implicit_figures — картинка приходит
-- как Para с одним Image, а не как Figure.

local section = 0
local fig_count = 0

function Header(el)
  if el.level == 1 then
    section = section + 1
    fig_count = 0
  end
  return el
end

function Para(el)
  if #el.content ~= 1 then return nil end
  local img = el.content[1]
  if img.t ~= "Image" then return nil end

  fig_count = fig_count + 1
  local num = string.format("Рисунок %d.%d", section, fig_count)
  local caption = pandoc.utils.stringify(img.caption or {})
  local text = num
  if caption ~= "" then
    text = num .. " \226\128\147 " .. caption  -- en-dash
  end

  return {
    el,
    pandoc.Para({pandoc.Str(text)}),
  }
end