-- СТП 01-2024, п. 2.2.2, 2.7.3: нумерация разделов и приложений.
--   — обычные разделы: 1, 2, 3...
--   — специальные (Введение, Заключение, Список) — без номера
--   — приложения: ПРИЛОЖЕНИЕ А, Б, В...
--   — подразделы приложений: А.1, А.2...
--
-- Значения ниже подставлены из config.toml.

local SPECIAL = { ["введение"] = true, ["заключение"] = true, ["перечень условных обозначений"] = true, ["перечень условных обозначений, символов и терминов"] = true, ["реферат"] = true, ["содержание"] = true, ["список использованных источников"] = true }

local APP_LETTERS = { "А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М", "Н", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ш", "Щ", "Э", "Ю", "Я" }

local APPENDIX_PREFIX = "приложение"

local section = 0
local subsection = 0
local subsubsection = 0
local app_index = 0
local in_appendix = false

local function is_special(text)
  return SPECIAL[pandoc.text.lower(text)] == true
end

local function is_appendix(text)
  local low = pandoc.text.lower(text)
  return low:sub(1, #APPENDIX_PREFIX) == APPENDIX_PREFIX
end

local function prepend(el, number)
  table.insert(el.content, 1, pandoc.Space())
  table.insert(el.content, 1, pandoc.Str(number))
end

function Header(el)
  local txt = pandoc.utils.stringify(el.content)

  if el.level == 1 then
    if is_special(txt) then
      section = 0
      subsection = 0
      subsubsection = 0
      in_appendix = false
      return el
    end
    if is_appendix(txt) then
      in_appendix = true
      app_index = app_index + 1
      subsection = 0
      subsubsection = 0
      return el
    end
    in_appendix = false
    section = section + 1
    subsection = 0
    subsubsection = 0
    prepend(el, tostring(section))
    return el
  end

  if el.level == 2 then
    if in_appendix then
      subsection = subsection + 1
      subsubsection = 0
      local letter = APP_LETTERS[app_index] or "?"
      prepend(el, letter .. "." .. subsection)
    else
      subsection = subsection + 1
      subsubsection = 0
      prepend(el, section .. "." .. subsection)
    end
    return el
  end

  if el.level == 3 then
    if in_appendix then
      subsubsection = subsubsection + 1
      local letter = APP_LETTERS[app_index] or "?"
      prepend(el, letter .. "." .. subsection .. "." .. subsubsection)
    else
      subsubsection = subsubsection + 1
      prepend(el, section .. "." .. subsection .. "." .. subsubsection)
    end
    return el
  end

  return el
end