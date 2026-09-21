-- СТП 01-2024, п. 2.6.2: подпись таблицы.
-- Обычные разделы: «Таблица N.M».
-- Приложения: «Таблица А.1», «Таблица Б.1».

local SPECIAL = { ["введение"] = true, ["заключение"] = true, ["перечень условных обозначений"] = true, ["перечень условных обозначений, символов и терминов"] = true, ["реферат"] = true, ["содержание"] = true, ["список использованных источников"] = true }

local APP_LETTERS = { "А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М", "Н", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ш", "Щ", "Э", "Ю", "Я" }

local APPENDIX_PREFIX = "приложение"

local section = 0
local tab_count = 0
local in_appendix = false
local app_index = 0

local function is_special(text)
  return SPECIAL[pandoc.text.lower(text)] == true
end

local function is_appendix(text)
  local low = pandoc.text.lower(text)
  return low:sub(1, #APPENDIX_PREFIX) == APPENDIX_PREFIX
end

function Header(el)
  if el.level == 1 then
    local txt = pandoc.utils.stringify(el.content)
    if is_appendix(txt) then
      in_appendix = true
      app_index = app_index + 1
      tab_count = 0
    elseif is_special(txt) then
      in_appendix = false
      section = 0
      tab_count = 0
    else
      in_appendix = false
      section = section + 1
      tab_count = 0
    end
  end
  return el
end

function Table(el)
  tab_count = tab_count + 1
  local num
  if in_appendix then
    local letter = APP_LETTERS[app_index] or "?"
    num = string.format("Таблица %s.%d", letter, tab_count)
  else
    num = string.format("Таблица %d.%d", section, tab_count)
  end

  local caption_text = ""
  if el.caption and el.caption.long and #el.caption.long > 0 then
    caption_text = pandoc.utils.stringify(el.caption.long)
  end

  local full_caption = num
  if caption_text ~= "" then
    full_caption = num .. " \226\128\147 " .. caption_text
  end

  el.caption = pandoc.Caption({}, {})

  return {
    pandoc.Para({pandoc.Str(full_caption)}),
    el,
  }
end