-- СТП 01-2024, п. 2.5.5: подпись рисунка.
-- Обычные разделы: «Рисунок N.M».
-- Приложения: «Рисунок А.1», «Рисунок Б.1».
-- Спецразделы (Введение, Заключение, ...) не считаются.

local SPECIAL = { $special_lua_table }

local APP_LETTERS = { $app_letters_lua_table }

local APPENDIX_PREFIX = "$appendix_prefix"

local section = 0
local fig_count = 0
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
      fig_count = 0
    elseif is_special(txt) then
      in_appendix = false
      section = 0
      fig_count = 0
    else
      in_appendix = false
      section = section + 1
      fig_count = 0
    end
  end
  return el
end

function Para(el)
  if #el.content ~= 1 then return nil end
  local img = el.content[1]
  if img.t ~= "Image" then return nil end

  fig_count = fig_count + 1
  local num
  if in_appendix then
    local letter = APP_LETTERS[app_index] or "?"
    num = string.format("Рисунок %s.%d", letter, fig_count)
  else
    num = string.format("Рисунок %d.%d", section, fig_count)
  end

  local caption = pandoc.utils.stringify(img.caption or {})
  local text = num
  if caption ~= "" then
    text = num .. " \226\128\147 " .. caption
  end

  img.caption = {}

  return {
    el,
    pandoc.Para({pandoc.Str(text)}),
  }
end