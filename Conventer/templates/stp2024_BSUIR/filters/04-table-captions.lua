-- СТП 01-2024, п. 2.6.2: подпись таблицы
-- Формат: «Таблица N.M – Название», слева, НАД таблицей.
-- ВАЖНО: очищаем caption у Table, иначе Pandoc дублирует его.

local section = 0
local tab_count = 0

function Header(el)
  if el.level == 1 then
    section = section + 1
    tab_count = 0
  end
  return el
end

function Table(el)
  tab_count = tab_count + 1
  local num = string.format("Таблица %d.%d", section, tab_count)

  local caption_text = ""
  if el.caption and el.caption.long and #el.caption.long > 0 then
    caption_text = pandoc.utils.stringify(el.caption.long)
  end

  local full_caption = num
  if caption_text ~= "" then
    full_caption = num .. " \226\128\147 " .. caption_text  -- en-dash
  end

  -- Очищаем caption, чтобы Pandoc не рендерил его второй раз
  el.caption = pandoc.Caption({}, {})

  return {
    pandoc.Para({pandoc.Str(full_caption)}),
    el,
  }
end