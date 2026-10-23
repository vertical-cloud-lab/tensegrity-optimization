-- docx_filter.lua: pandoc filter used by build_manuscript_docx.py.
--
-- Reads the numbers LaTeX assigned (labels and \bibcite entries from
-- manuscript.aux, passed as JSON through $MANU_DOCX_AUX) so that every
-- cross-reference and citation in the Word file carries the same number as
-- manuscript.pdf. Also numbers headings, captions and equations, turns
-- run-in headings and wide floats into markers that the Python
-- post-processing step lays out, and maps the custom LaTeX environments to
-- Word paragraph styles.

local f = assert(io.open(os.getenv('MANU_DOCX_AUX'), 'r'))
local AUX = pandoc.json.decode(f:read('a'), false)
f:close()

local LABELS = AUX.labels
local CITES = AUX.cites
local TEXT_W = AUX.text_w_in
local COL_W = AUX.col_w_in
local WIDE = {}
for _, l in ipairs(AUX.wide) do WIDE[l] = true end

local NBSP = '\u{00A0}'
local EMSP = '\u{2003}'

-- Word bookmark names: a letter first, then letters, digits and
-- underscores, at most 40 chars (pandoc hashes any other name).
local function bm(label)
  return ('lbl_' .. (label:gsub('[^%w]', '_'))):sub(1, 40)
end

local WIDE_BM = {}
for l, _ in pairs(WIDE) do WIDE_BM[bm(l)] = true end

local function warn(msg)
  io.stderr:write('[docx_filter] ' .. msg .. '\n')
end

local function marker(name)
  return pandoc.RawBlock('openxml',
    '<w:p><w:pPr><w:pStyle w:val="' .. name .. '"/></w:pPr></w:p>')
end

local function tab()
  return pandoc.RawInline('openxml', '<w:r><w:tab/></w:r>')
end

-- ---------------------------------------------------------------------------
-- Citations: natbib numeric, sorted and compressed ([1, 2], [3-5] with an en
-- dash as printed by asmejour), each number linked to its reference entry.
-- ---------------------------------------------------------------------------
local function cite_link(n)
  return pandoc.Link({pandoc.Str(tostring(n))}, '#bib' .. tostring(n))
end

function Cite(el)
  local items = {}
  for _, c in ipairs(el.citations) do
    local n = tonumber(CITES[c.id])
    if not n then
      warn('no \\bibcite for ' .. c.id)
      n = 0
    end
    items[#items + 1] = n
  end
  table.sort(items)
  local out = pandoc.List({pandoc.Str('[')})
  local i = 1
  while i <= #items do
    local j = i
    while j < #items and items[j + 1] == items[j] + 1 do j = j + 1 end
    if j - i >= 2 then
      out:insert(cite_link(items[i]))
      out:insert(pandoc.Str('\u{2013}'))
      out:insert(cite_link(items[j]))
    else
      j = i
      out:insert(cite_link(items[i]))
    end
    if j < #items then
      out:insert(pandoc.Str(','))
      out:insert(pandoc.Space())
    end
    i = j + 1
  end
  out:insert(pandoc.Str(']'))
  return out
end

-- ---------------------------------------------------------------------------
-- \ref / \eqref
-- ---------------------------------------------------------------------------
function Link(el)
  local rt = el.attributes['reference-type']
  if not rt then return nil end
  local key = el.attributes['reference']
  local num = LABELS[key]
  if not num then
    warn('no \\newlabel for ' .. key)
    num = '??'
  end
  if rt == 'eqref' then num = '(' .. num .. ')' end
  return pandoc.Link({pandoc.Str(num)}, '#' .. bm(key))
end

-- ---------------------------------------------------------------------------
-- Simple inline math (t_{180}, E_{\mathrm{reb}}, \rho = 0.75, ...) becomes
-- ordinary Times text: italic letters, upright digits and Greek capitals,
-- real sub/superscripts. This matches the PDF's newtx math and is easier to
-- edit in Word. Anything with fractions, roots or operators like \max stays
-- a Word equation.
-- ---------------------------------------------------------------------------
local GREEK = {
  alpha = 'α', beta = 'β', gamma = 'γ', delta = 'δ', epsilon = 'ϵ', varepsilon = 'ε',
  zeta = 'ζ', eta = 'η', theta = 'θ', iota = 'ι', kappa = 'κ', lambda = 'λ', mu = 'μ',
  nu = 'ν', xi = 'ξ', pi = 'π', rho = 'ρ', sigma = 'σ', tau = 'τ', phi = 'ϕ',
  varphi = 'φ', chi = 'χ', psi = 'ψ', omega = 'ω', ell = 'ℓ',
}
local GREEK_UP = {
  Gamma = 'Γ', Delta = 'Δ', Theta = 'Θ', Lambda = 'Λ', Xi = 'Ξ', Pi = 'Π',
  Sigma = 'Σ', Phi = 'Φ', Psi = 'Ψ', Omega = 'Ω',
}
local SYM = {
  pm = {'±', 'bin'}, mp = {'∓', 'bin'}, times = {'×', 'bin'}, cdot = {'⋅', 'bin'},
  sim = {'∼', 'rel'}, approx = {'≈', 'rel'}, ge = {'≥', 'rel'}, geq = {'≥', 'rel'},
  le = {'≤', 'rel'}, leq = {'≤', 'rel'}, neq = {'≠', 'rel'}, to = {'→', 'rel'},
  star = {'⋆', 'ord'}, dagger = {'†', 'ord'}, ddagger = {'‡', 'ord'},
  partial = {'∂', 'ord'}, infty = {'∞', 'ord'}, prime = {'′', 'ord'},
  ['%'] = {'%', 'ord'}, ['{'] = {'{', 'open'}, ['}'] = {'}', 'close'},
}
local SPACES = {[','] = '\u{2009}', [';'] = ' ', [':'] = ' ', [' '] = ' ', quad = EMSP, qquad = EMSP .. EMSP, ['!'] = ''}

local function tokenize(s)
  local toks, i = {}, 1
  while i <= #s do
    local c = s:sub(i, i)
    if c == '\\' then
      local name = s:match('^\\(%a+)', i)
      if name then
        toks[#toks + 1] = {t = 'cmd', v = name}
        i = i + 1 + #name
      else
        toks[#toks + 1] = {t = 'cmd', v = s:sub(i + 1, i + 1)}
        i = i + 2
      end
    elseif c == '{' then
      local depth, j = 0, i
      while j <= #s do
        local d = s:sub(j, j)
        if d == '\\' then j = j + 1
        elseif d == '{' then depth = depth + 1
        elseif d == '}' then
          depth = depth - 1
          if depth == 0 then break end
        end
        j = j + 1
      end
      if depth ~= 0 then return nil end
      toks[#toks + 1] = {t = 'group', v = s:sub(i + 1, j - 1)}
      i = j + 1
    elseif c:match('%s') then
      i = i + 1
    else
      toks[#toks + 1] = {t = 'char', v = c}
      i = i + 1
    end
  end
  return toks
end

local convert_atoms

local function roman_text(src)
  if src:find('[\\_%^&]') then return nil end
  return src:gsub('[{}]', '')
end

local function script_inlines(src)
  local atoms = convert_atoms(src)
  if not atoms then return nil end
  local out = pandoc.List()
  for _, a in ipairs(atoms) do
    if a.sub or a.sup then return nil end
    out:extend(a.inl)
  end
  return out
end

convert_atoms = function(src)
  local toks = tokenize(src)
  if not toks then return nil end
  local atoms, k = {}, 1
  local function next_arg()
    local t = toks[k]
    k = k + 1
    if not t then return nil end
    if t.t == 'cmd' then return '\\' .. t.v end
    return t.v
  end
  local function push(kind, inl) atoms[#atoms + 1] = {kind = kind, inl = pandoc.List(inl)} end
  while k <= #toks do
    local t = toks[k]
    k = k + 1
    if t.t == 'char' then
      local c = t.v
      if c:match('%a') then
        push('ord', {pandoc.Emph({pandoc.Str(c)})})
      elseif c:match('[%d%.]') then
        local last = atoms[#atoms]
        if last and last.kind == 'num' and not last.sub and not last.sup then
          last.inl[#last.inl] = pandoc.Str(last.inl[#last.inl].text .. c)
        else
          push('num', {pandoc.Str(c)})
        end
      elseif c == '=' or c == '<' or c == '>' then push('rel', {pandoc.Str(c)})
      elseif c == '+' then push('bin', {pandoc.Str('+')})
      elseif c == '-' then push('bin', {pandoc.Str('\u{2212}')})
      elseif c == '/' or c == '|' or c == '!' then push('ord', {pandoc.Str(c)})
      elseif c == "'" then push('ord', {pandoc.Str('′')})
      elseif c == '(' or c == '[' then push('open', {pandoc.Str(c)})
      elseif c == ')' or c == ']' then push('close', {pandoc.Str(c)})
      elseif c == ',' or c == ';' then push('punct', {pandoc.Str(c)})
      elseif c == '_' or c == '^' then
        local arg = next_arg()
        if not arg then return nil end
        local inl = script_inlines(arg)
        if not inl then return nil end
        local last = atoms[#atoms]
        if not last or last.kind == 'rel' or last.kind == 'bin' or last.kind == 'open' or last.kind == 'punct' then
          push('ord', {})
          last = atoms[#atoms]
        end
        local which = (c == '_') and 'sub' or 'sup'
        if last[which] then return nil end
        last[which] = true
        last.inl:insert(c == '_' and pandoc.Subscript(inl) or pandoc.Superscript(inl))
      elseif c == '~' then
        push('ord', {pandoc.Str(NBSP)})
      else
        return nil
      end
    elseif t.t == 'group' then
      local inner = convert_atoms(t.v)
      if not inner then return nil end
      for _, a in ipairs(inner) do atoms[#atoms + 1] = a end
    else
      local n = t.v
      if GREEK[n] then
        push('ord', {pandoc.Emph({pandoc.Str(GREEK[n])})})
      elseif GREEK_UP[n] then
        push('ord', {pandoc.Str(GREEK_UP[n])})
      elseif SYM[n] then
        push(SYM[n][2], {pandoc.Str(SYM[n][1])})
      elseif SPACES[n] then
        if SPACES[n] ~= '' then push('space', {pandoc.Str(SPACES[n])}) end
      elseif n == 'mathrm' or n == 'text' or n == 'textrm' or n == 'mathit' or n == 'mathbf' then
        local arg = next_arg()
        local txt = arg and roman_text(arg)
        if not txt then return nil end
        local str = pandoc.Str(txt)
        if n == 'mathit' then push('ord', {pandoc.Emph({str})})
        elseif n == 'mathbf' then push('ord', {pandoc.Strong({str})})
        else push('ord', {str}) end
      elseif n == 'SI' then
        local num, unit = next_arg(), next_arg()
        local u = unit and roman_text(unit)
        if not num or not u or num:find('[\\{}]') then return nil end
        push('num', {pandoc.Str(num .. NBSP .. u)})
      else
        return nil
      end
    end
  end
  return atoms
end

local function math_to_inlines(src)
  local atoms = convert_atoms(src)
  if not atoms or #atoms == 0 then return nil end
  local out = pandoc.List()
  for i, a in ipairs(atoms) do
    local prev, nxt = atoms[i - 1], atoms[i + 1]
    local operand_before = prev and (prev.kind == 'ord' or prev.kind == 'num' or prev.kind == 'close')
    if a.kind == 'rel' then
      if prev and prev.kind ~= 'open' then out:insert(pandoc.Str(NBSP)) end
      out:extend(a.inl)
      if nxt then out:insert(pandoc.Space()) end
    elseif a.kind == 'bin' and operand_before and nxt then
      out:insert(pandoc.Str(NBSP))
      out:extend(a.inl)
      out:insert(pandoc.Space())
    elseif a.kind == 'punct' then
      out:extend(a.inl)
      if nxt then out:insert(pandoc.Space()) end
    else
      out:extend(a.inl)
    end
  end
  return out
end

function Math(el)
  if el.mathtype ~= 'InlineMath' then return nil end
  local ok, res = pcall(math_to_inlines, el.text)
  if ok and res then return res end
  el.text = txt_for_word(el.text)
  return el
end

-- violet placeholder values (\dummy{...} -> \textcolor{dummydata}{...})
function Span(el)
  local st = el.attributes['style']
  if st and st:match('dummydata') then
    el.attributes['style'] = nil
    el.attributes['custom-style'] = 'Placeholder Text'
    return el
  end
end

-- ---------------------------------------------------------------------------
-- Headings: section numbers as printed ("2 Background", "2.1 Title.")
-- ---------------------------------------------------------------------------
local sec, sub = 0, 0

local function ends_with_punct(inlines)
  local s = pandoc.utils.stringify(inlines)
  return s:match('[%.%?%!:]$') ~= nil
end

function Header(el)
  local label = el.identifier
  el.identifier = label:find(':') and bm(label) or ''
  if el.classes:includes('unnumbered') then
    el.level = 1
    return el
  end
  local content = pandoc.List()
  local num
  if el.level == 1 then
    sec = sec + 1
    sub = 0
    num = tostring(sec)
    content:insert(pandoc.Str(num .. EMSP))
    content:extend(el.content)
  elseif el.level == 2 then
    sub = sub + 1
    num = sec .. '.' .. sub
    content:insert(pandoc.Str(num .. EMSP))
    content:extend(el.content)
    if not ends_with_punct(el.content) then content:insert(pandoc.Str('.')) end
  else
    -- \paragraph: italic run-in heading, unnumbered
    content:extend(el.content)
    if not ends_with_punct(el.content) then content:insert(pandoc.Str('.')) end
  end
  if num and label:find(':') and LABELS[label] and LABELS[label] ~= num then
    warn('section number mismatch for ' .. label .. ': ' .. num .. ' vs ' .. LABELS[label])
  end
  el.content = content
  return el
end

function OrderedList(el)
  el.listAttributes = pandoc.ListAttributes(el.start, 'Decimal', 'TwoParens')
  return el
end

-- ---------------------------------------------------------------------------
-- Figures: absolute image widths (column or full text width), "Fig. N" label
-- ---------------------------------------------------------------------------
local function set_width(img, base_in)
  local w = img.attributes['width']
  local frac = 1.0
  if w and w:match('%%$') then frac = tonumber(w:sub(1, -2)) / 100 end
  img.attributes['width'] = string.format('%.3fin', frac * base_in)
  img.attributes['height'] = nil
  return img
end

local function prefixed_caption(prefix, caption)
  local inl = pandoc.List({pandoc.Str(prefix), pandoc.Str(EMSP)})
  if #caption.long > 0 then inl:extend(caption.long[1].content) end
  caption.long = {pandoc.Plain(inl)}
  return caption
end

function Figure(el)
  local label = el.identifier
  local num = LABELS[label]
  if not num then
    warn('figure without a numbered label: ' .. label)
    num = '?'
  end
  local base = WIDE[label] and TEXT_W or COL_W
  el = el:walk({Image = function(img) return set_width(img, base) end})
  el.caption = prefixed_caption('Fig.' .. NBSP .. num, el.caption)
  el.identifier = bm(label)
  return el
end

-- ---------------------------------------------------------------------------
-- Equations: each display equation becomes a two-cell borderless table
-- (equation | number), the usual way to number equations in Word. Text that
-- follows an equation in the same LaTeX paragraph continues unindented.
-- ---------------------------------------------------------------------------
local eqno = 0

-- Word draws its own operator spacing; explicit TeX spaces and the
-- delimiter commands below come through as odd glyphs in some renderers.
function txt_for_word(txt)
  txt = txt:gsub('\\[;:!]', ' ')
  txt = txt:gsub('\\,', ' ')
  txt = txt:gsub('\\[lr]Vert', '\\|')
  txt = txt:gsub('\\[lr]vert', '|')
  return txt
end

local function equation_blocks(math)
  local txt = math.text
  local label = txt:match('\\label%{([^}]*)%}')
  txt = txt:gsub('\\label%{[^}]*%}', '')
  txt = txt:gsub('\\begin%{equation%*?%}', '')
  txt = txt:gsub('\\end%{equation%*?%}', '')
  txt = txt_for_word(txt)
  eqno = eqno + 1
  local num = tostring(eqno)
  if label and LABELS[label] and LABELS[label] ~= num then
    warn('equation number mismatch for ' .. label)
  end
  local cell1 = {pandoc.Para({pandoc.Math('DisplayMath', txt)})}
  local cell2 = {pandoc.Plain({pandoc.Str('(' .. num .. ')')})}
  local st = pandoc.SimpleTable({}, {'AlignCenter', 'AlignRight'}, {0.88, 0.12}, {}, {{cell1, cell2}})
  local tbl = pandoc.utils.from_simple_table(st)
  local blocks = {marker('EqTableMarker'), tbl}
  if label then
    return {pandoc.Div(blocks, {id = bm(label)})}
  end
  return blocks
end

local function is_space(x)
  return x.t == 'Space' or x.t == 'SoftBreak' or x.t == 'LineBreak'
end

function Para(el)
  local has = false
  for _, x in ipairs(el.content) do
    if x.t == 'Math' and x.mathtype == 'DisplayMath' then has = true end
  end
  if not has then return nil end
  local out, cur = pandoc.List(), pandoc.List()
  local seen = false
  local function flush()
    while #cur > 0 and is_space(cur[1]) do cur:remove(1) end
    while #cur > 0 and is_space(cur[#cur]) do cur:remove(#cur) end
    if #cur > 0 then
      if seen then
        out:insert(pandoc.Div({pandoc.Para(cur)}, {['custom-style'] = 'Body Text Continued'}))
      else
        out:insert(pandoc.Para(cur))
      end
    end
    cur = pandoc.List()
  end
  for _, x in ipairs(el.content) do
    if x.t == 'Math' and x.mathtype == 'DisplayMath' then
      flush()
      out:extend(equation_blocks(x))
      seen = true
    else
      cur:insert(x)
    end
  end
  flush()
  return out
end

-- ---------------------------------------------------------------------------
-- Tables, custom environments, bibliography entries
-- ---------------------------------------------------------------------------
function Div(el)
  local id = el.identifier
  if id:match('^tab:') then
    local num = LABELS[id]
    if not num then
      warn('table without a numbered label: ' .. id)
      num = '?'
    end
    el = el:walk({Table = function(t)
      t.caption = prefixed_caption('Table' .. NBSP .. num, t.caption)
      return t
    end})
    el.identifier = bm(id)
    return el
  end
  if el.classes:includes('draftnote') then
    el.attributes['custom-style'] = 'Draft Note'
    return el
  end
  if el.classes:includes('placeholderbox') then
    el.attributes['custom-style'] = 'Figure Placeholder'
    return el
  end
  if el.classes:includes('tablenote') then
    el.attributes['custom-style'] = 'Table Note'
    return el
  end
  if el.classes:includes('bibentry') then
    local inl = el.content[1].content
    local num = pandoc.utils.stringify(inl[2])
    local rest = pandoc.List()
    for k = 3, #inl do rest:insert(inl[k]) end
    while #rest > 0 and is_space(rest[1]) do rest:remove(1) end
    local c = pandoc.List({pandoc.Str('[' .. num .. ']'), tab()})
    c:extend(rest)
    return pandoc.Div({pandoc.Para(c)}, {id = 'bib' .. num, ['custom-style'] = 'Bibliography'})
  end
end

-- ---------------------------------------------------------------------------
-- Document level: run-in headings and full-width (figure*/table*) floats
-- ---------------------------------------------------------------------------
local function is_wide(b)
  return (b.t == 'Figure' or b.t == 'Div') and b.identifier ~= '' and WIDE_BM[b.identifier]
end

function Pandoc(doc)
  local blocks = doc.blocks
  local out = pandoc.List()
  local i = 1
  while i <= #blocks do
    local b = blocks[i]
    local nxt = blocks[i + 1]
    if b.t == 'Header' and (b.level == 2 or b.level == 4) and nxt and nxt.t == 'Para' then
      -- run-in heading: bold (subsection) or italic (\paragraph) lead-in of
      -- the paragraph that follows, as asmejour sets them
      local lead = (b.level == 2) and pandoc.Strong(b.content) or pandoc.Emph(b.content)
      local c = pandoc.List({lead, pandoc.Space()})
      c:extend(nxt.content)
      local style = (b.level == 2) and 'Run-in Heading 2' or 'Run-in Heading 4'
      out:insert(pandoc.Div({pandoc.Para(c)}, {id = b.identifier, ['custom-style'] = style}))
      i = i + 2
    elseif is_wide(b) then
      out:insert(marker('WideStart'))
      out:insert(b)
      i = i + 1
      while blocks[i] and blocks[i].t == 'Div' and blocks[i].classes:includes('tablenote') do
        out:insert(blocks[i])
        i = i + 1
      end
      out:insert(marker('WideEnd'))
    else
      out:insert(b)
      i = i + 1
    end
  end
  doc.blocks = out
  return doc
end
