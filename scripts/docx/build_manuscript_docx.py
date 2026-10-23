#!/usr/bin/env python3
"""Build an editable Word version of the JMD manuscript (manuscript/manuscript.docx).

The Word file is generated from the same LaTeX source as manuscript.pdf
(manuscript.tex, i.e. manuscript-body.tex with the todo notes hidden):

1. LaTeX is compiled once in a scratch directory so that every figure, table,
   equation, section and citation number can be read from manuscript.aux and
   the formatted reference list from manuscript.bbl. The numbers in the Word
   file are therefore the PDF's numbers, not a re-count.
2. The body is lightly preprocessed (todo notes removed, title block and
   author blocks pulled out, the TikZ-annotated photo and the PDF-only figure
   rasterized) and converted by pandoc with docx_filter.lua. Equations become
   native Word equations, tables become Word tables.
3. The resulting .docx is post-processed to match the asmejour layout: the
   8.5 x 11.25 in page, the title block with the author column, two text
   columns with line numbers, full-width sections for the wide figures and
   tables, run-in subsection headings, the journal footers, and the lists of
   figures and tables.

Requirements: TeX Live (pdflatex, bibtex, asmejour), pandoc >= 3.1,
python-docx, lxml and PyMuPDF.

Usage:
    python scripts/docx/build_manuscript_docx.py            # writes manuscript/manuscript.docx
    python scripts/docx/build_manuscript_docx.py --keep-tmp # keep the scratch directory
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANU = REPO / "manuscript"
LUA_FILTER = HERE / "docx_filter.lua"

# Page geometry measured from manuscript.pdf (asmejour): 612 x 809.86 pt page,
# 60 pt side margins, two 240 pt columns with a 12 pt gutter.
PAGE_W_IN = 8.5
PAGE_H_IN = 809.86 / 72
SIDE_MARGIN_IN = 60 / 72
TEXT_W_IN = PAGE_W_IN - 2 * SIDE_MARGIN_IN  # 6.833 in
# The PDF's gutter is 12 pt, with the right column's line numbers in the
# outer margin. Word always draws line numbers to the left of each column,
# so the gutter is widened to 24 pt to hold the right column's numbers.
GUTTER_IN = 24 / 72
COL_W_IN = (TEXT_W_IN - GUTTER_IN) / 2  # 3.25 in

# Date printed under the corresponding-author footnote of manuscript.pdf at
# 99cdb87 (\today of that build). Override with --date.
DEFAULT_DATE = "October 11, 2026"

VIOLET = "8E44AD"  # \definecolor{dummydata}{RGB}{142,68,173}


# --------------------------------------------------------------------------
# Small LaTeX parsing helpers
# --------------------------------------------------------------------------
def strip_comments(tex: str) -> str:
    """Drop TeX comments. As in TeX, a comment also eats its end of line,
    unless the next line is blank (which must stay a paragraph break)."""
    return re.sub(r"(?<!\\)%[^\n]*(\n(?![ \t]*\n)[ \t]*)?", "", tex)


def match_brace(s: str, i: int, open_c: str = "{", close_c: str = "}") -> int:
    """s[i] == open_c; return the index just past the matching close_c."""
    assert s[i] == open_c, (s[i : i + 30], i)
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError("unbalanced group at %d" % i)


def skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def find_command(s: str, name: str, start: int = 0) -> int:
    pat = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z@])")
    m = pat.search(s, start)
    return m.start() if m else -1


def parse_command(s: str, i: int, name: str, nargs: int, nopt: int = 1):
    """Parse \\name[opt]{a1}...{an} at s[i]; return (end, opts, args)."""
    j = i + 1 + len(name)
    opts, args = [], []
    for _ in range(nopt):
        k = skip_ws(s, j)
        if k < len(s) and s[k] == "[":
            e = match_brace(s, k, "[", "]")
            opts.append(s[k + 1 : e - 1])
            j = e
    for _ in range(nargs):
        k = skip_ws(s, j)
        e = match_brace(s, k)
        args.append(s[k + 1 : e - 1])
        j = e
    return j, opts, args


def remove_commands(s: str, name: str, nargs: int, nopt: int = 1) -> str:
    while True:
        i = find_command(s, name)
        if i < 0:
            return s
        j, _, _ = parse_command(s, i, name, nargs, nopt)
        # swallow a trailing "%"-joined newline already handled; drop one
        # following newline if the command sat on its own lines
        s = s[:i] + s[j:]


def replace_commands(s: str, name: str, nargs: int, fn, nopt: int = 0) -> str:
    pos = 0
    while True:
        i = find_command(s, name, pos)
        if i < 0:
            return s
        j, opts, args = parse_command(s, i, name, nargs, nopt)
        rep = fn(opts, args)
        s = s[:i] + rep + s[j:]
        pos = i + len(rep)


def env_span(s: str, env: str, start: int = 0):
    b = s.find("\\begin{%s}" % env, start)
    if b < 0:
        return None
    e = s.find("\\end{%s}" % env, b)
    return b, e + len("\\end{%s}" % env)


# --------------------------------------------------------------------------
# .aux and .bbl
# --------------------------------------------------------------------------
def parse_aux(aux_text: str):
    labels, cites = {}, {}
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}", aux_text):
        key, num = m.group(1), m.group(2)
        if key.endswith("@cref"):
            continue
        labels[key] = re.sub(r"\\[a-zA-Z@]+\s*", "", num).strip()
    for m in re.finditer(r"\\bibcite\{([^}]*)\}\{\{?([0-9]+)", aux_text):
        cites[m.group(1)] = m.group(2)
    return labels, cites


def bbl_to_latex(bbl: str, cites: dict) -> str:
    body = bbl.split("\\begin{thebibliography}", 1)[1]
    body = body.split("\\end{thebibliography}", 1)[0]
    parts = re.split(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", body)
    out = []
    for k in range(1, len(parts), 2):
        key, text = parts[k], parts[k + 1].strip()
        n = cites.get(key, "?")
        out.append("\\begin{bibentry}{%s}{%s}\n%s\n\\end{bibentry}\n" % (key, n, text))
    return "\n".join(out)


# --------------------------------------------------------------------------
# Figures that pandoc cannot take as they are
# --------------------------------------------------------------------------
def rasterize_pdf_figure(pdf: Path, png: Path, dpi: int = 300):
    import fitz

    doc = fitz.open(pdf)
    doc[0].get_pixmap(dpi=dpi).save(png)


def crop_tikz_photo(manuscript_pdf: Path, image_name_hint: str, png: Path, dpi: int = 600):
    """Rasterize the photo of Fig. 2(b) together with its TikZ callouts.

    The photo is located in the compiled PDF by its image placement; the crop
    is widened upward to include the d_t / d_s labels that sit above it.
    """
    import fitz

    doc = fitz.open(manuscript_pdf)
    best = None
    for pno in range(doc.page_count):
        page = doc[pno]
        for info in page.get_image_info(xrefs=True):
            w = info["bbox"][2] - info["bbox"][0]
            h = info["bbox"][3] - info["bbox"][1]
            # the printed-specimen photo is the right-hand panel of a
            # single-column figure: ~130 pt wide, taller than wide
            if 110 < w < 150 and h > w:
                txt = page.get_text("text", clip=fitz.Rect(info["bbox"][0] - 20, info["bbox"][1] - 20, info["bbox"][2] + 20, info["bbox"][3] + 20))
                if "\U0001d43b" in txt or "H" in txt:  # math-italic H callout
                    best = (pno, fitz.Rect(info["bbox"]))
    if best is None:
        raise RuntimeError("could not locate the Fig. 2(b) photo in the PDF")
    pno, r = best
    clip = fitz.Rect(r.x0 - 1, r.y0 - 12, r.x1 + 1, r.y1 + 1)
    doc[pno].get_pixmap(dpi=dpi, clip=clip).save(png)
    return clip


# --------------------------------------------------------------------------
# Preprocessing of manuscript-body.tex
# --------------------------------------------------------------------------
def _split_cells(row: str):
    cells, depth, cur, i = [], 0, "", 0
    while i < len(row):
        c = row[i]
        if c == "\\":
            cur += row[i : i + 2]
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if c == "&" and depth == 0:
            cells.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    cells.append(cur)
    return cells


def merge_pm_columns(body: str) -> str:
    """Rewrite tabulars that set "mean @{$\\pm$} sd" as two siunitx columns.

    pandoc cannot read S[...] columns or @{...} separators with content, so
    the two columns become one centred column holding "mean ± sd".
    """
    out, pos = [], 0
    while True:
        i = body.find("\\begin{tabular}", pos)
        if i < 0:
            out.append(body[pos:])
            return "".join(out)
        j = match_brace(body, i + len("\\begin{tabular}"))
        spec = body[i + len("\\begin{tabular}") + 1 : j - 1]
        end = body.find("\\end{tabular}", j)
        if "\\pm" not in spec:
            out.append(body[pos:end])
            pos = end
            continue
        # tokenise the column spec into columns and @{} separators
        cols, k, pm_after = [], 0, None
        while k < len(spec):
            c = spec[k]
            if c == "@":
                e = match_brace(spec, k + 1)
                if "\\pm" in spec[k:e]:
                    pm_after = len(cols) - 1
                k = e
            elif c == "S":
                k += 1
                if k < len(spec) and spec[k] == "[":
                    k = match_brace(spec, k, "[", "]")
                cols.append("c")
            elif c in "lcr":
                cols.append(c)
                k += 1
            else:
                k += 1
        new_cols = cols[: pm_after] + ["c"] + cols[pm_after + 2 :]
        rows = body[j:end].split("\\\\")
        new_rows = []
        for row in rows:
            m = re.match(r"(\s*(?:\\(?:top|mid|bottom)rule\s*)*)([\s\S]*)$", row)
            lead, rest = m.group(1), m.group(2)
            if not rest.strip():
                new_rows.append(row)
                continue
            cells = _split_cells(rest)
            merged, col = [], 0
            idx = 0
            while idx < len(cells):
                cell = cells[idx]
                mc = re.match(r"\s*\\multicolumn\{(\d+)\}\{[^}]*\}\{([\s\S]*)\}\s*$", cell)
                span = int(mc.group(1)) if mc else 1
                if col == pm_after and span == 2:
                    merged.append(" " + mc.group(2) + " ")
                elif col == pm_after and span == 1 and idx + 1 < len(cells):
                    merged.append(cell.rstrip() + " $\\pm$ " + cells[idx + 1].lstrip())
                    idx += 1
                    span = 2
                else:
                    merged.append(cell)
                col += span
                idx += 1
            new_rows.append(lead + "&".join(merged))
        new_body = "\\\\".join(new_rows).replace("{-}", "-")
        out.append(body[pos:i] + "\\begin{tabular}{@{}%s@{}}" % "".join(new_cols) + new_body)
        pos = end


def tex_inline_to_text(s: str) -> str:
    """Plain text for the short title-block strings."""
    s = re.sub(r"\s+", " ", s)
    s = s.replace("~", "\u00a0").replace("\\,", "\u2009")
    s = re.sub(r"\\dag(?![a-z])", "\u2020", s)
    s = re.sub(r"\\ddag(?![a-z])", "\u2021", s)
    return s.strip()


def preprocess(body_tex: str, work: Path, labels: dict, cites: dict, bbl: str, pdf: Path):
    tex = strip_comments(body_tex)
    doc_start = tex.index("\\begin{document}") + len("\\begin{document}")
    doc_end = tex.index("\\end{document}")
    body = tex[doc_start:doc_end]
    meta = {}

    # -- todo notes vanish in manuscript.pdf ([disable] option) ----------------
    body = remove_commands(body, "todo", 1, nopt=1)
    body = remove_commands(body, "listoftodos", 0, nopt=1)

    # -- title block --------------------------------------------------------
    authors = []

    def grab_author(opts, args):
        name, affil = args
        corresponding = "\\CorrespondingAuthor" in name
        name = name.replace("\\CorrespondingAuthor", "")
        sup = ""
        m = re.search(r"\\textsuperscript\{(.*)\}\s*$", name)
        if m:
            sup = tex_inline_to_text(m.group(1))
            name = name[: m.start()]
        authors.append(
            {
                "name": tex_inline_to_text(name),
                "sup": sup,
                "corresponding": corresponding,
                "affil": [tex_inline_to_text(x) for x in affil.split("\\\\") if x.strip()],
            }
        )
        return ""

    body = replace_commands(body, "SetAuthorBlock", 2, grab_author)
    meta["authors"] = authors

    def grab(name):
        holder = {}

        def fn(opts, args):
            holder["v"] = args[0]
            return ""

        return holder, fn

    h, fn = grab("title")
    body = replace_commands(body, "title", 1, fn)
    meta["title"] = tex_inline_to_text(h["v"])
    h, fn = grab("keywords")
    body = replace_commands(body, "keywords", 1, fn)
    meta["keywords"] = tex_inline_to_text(h["v"])

    b, e = env_span(body, "abstract")
    abstract = body[b + len("\\begin{abstract}") : e - len("\\end{abstract}")]
    body = body[:b] + body[e:]
    plain, violet = abstract, ""
    m = re.search(r"\\dummy\{", abstract)
    if m:
        end = match_brace(abstract, m.end() - 1)
        violet = tex_inline_to_text(abstract[m.end() : end - 1])
        plain = abstract[: m.start()] + abstract[end:]
    meta["abstract"] = tex_inline_to_text(plain)
    meta["abstract_placeholder"] = violet
    body = remove_commands(body, "maketitle", 0, nopt=0)

    # -- draft note box (\fcolorbox inside a center environment) -------------
    b, e = env_span(body, "center")
    center = body[b:e]
    if "fcolorbox" in center:
        m = re.search(r"\\textcolor\{dummydata\}\{", center)
        end = match_brace(center, m.end() - 1)
        note = center[m.end() : end - 1]
        body = body[:b] + "\\begin{draftnote}\n" + note + "\n\\end{draftnote}\n" + body[e:]

    # -- violet placeholders ---------------------------------------------------
    body = replace_commands(body, "dummy", 1, lambda o, a: "\\textcolor{dummydata}{%s}" % a[0])

    # -- placeholder figure / table macros (they print in the clean PDF) -----
    def figph(opts, args):
        label, cap = args
        return (
            "\\begin{figure}[ht]\n\\centering\n"
            "\\begin{placeholderbox}\n\\textit{Figure placeholder: %s}\n\\end{placeholderbox}\n"
            "\\caption{\\textit{Placeholder.} %s}\n\\label{fig:%s}\n\\end{figure}\n" % (cap, cap, label)
        )

    body = replace_commands(body, "figplaceholder", 2, figph, nopt=1)

    def tabph(opts, args):
        label, cap = args
        return (
            "\\begin{table}[ht]\n\\centering\n\\caption{\\textit{Placeholder.} %s}\n\\label{tab:%s}\n"
            "\\begin{tabular}{@{}lll@{}}\n\\toprule\nColumn A & Column B & Column C \\\\\n\\midrule\n"
            "\\multicolumn{3}{c}{\\textit{(table contents pending)}} \\\\\n\\bottomrule\n"
            "\\end{tabular}\n\\end{table}\n" % (cap, label)
        )

    body = replace_commands(body, "tabplaceholder", 2, tabph)

    # -- section signs used as math superscripts (texmath has no \\S) -------
    body = re.sub(r"\$\^\{?\\S\}?\$", r"\\textsuperscript{\\S}", body)
    body = re.sub(r"\$\\S\$", r"\\S{}", body)

    # -- siunitx S columns joined by @{\,$\pm$\,}: merge into "x ± s" cells -
    body = merge_pm_columns(body)

    # -- siunitx ranges print as "X to Y unit" (range-phrase = { to }) -------
    body = replace_commands(body, "SIrange", 3, lambda o, a: "%s to \\SI{%s}{%s}" % (a[0], a[1], a[2]))

    # -- table notes: {\footnotesize \textsuperscript{a}...} after a tabular --
    body = re.sub(
        r"\\end\{tabular\}\s*\\\\\[[^\]]*\]\s*\{\\footnotesize\s*",
        r"\\end{tabular}\n\\begin{tablenote}",
        body,
    )
    # close the tablenote at the brace that closed the {\footnotesize ...} group
    out, pos = [], 0
    for m in re.finditer(r"\\begin\{tablenote\}", body):
        out.append(body[pos : m.end()])
        k = m.end()
        depth = 1
        while depth:
            c = body[k]
            if c == "\\":
                out.append(body[k : k + 2])
                k += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            out.append(c)
            k += 1
        out.append("\\end{tablenote}")
        pos = k + 1
    out.append(body[pos:])
    body = "".join(out)

    # -- TikZ-annotated photo (Fig. 2b) -> rasterized crop of the PDF -------
    b_e = env_span(body, "tikzpicture")
    if b_e:
        png = work / "fig2b-annotated.png"
        crop_tikz_photo(pdf, "printed-specimen", png)
        b, e = b_e
        body = body[:b] + "\\includegraphics[width=\\linewidth]{%s}" % png + body[e:]

    # -- subfigures without their own captions: plain side-by-side images ---
    def unsub(m):
        width, inner = m.group(1), m.group(2)
        g = re.search(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", inner)
        return "\\includegraphics[width=%s\\linewidth]{%s}" % (width, g.group(2))

    body = re.sub(
        r"\\begin\{subfigure\}(?:\[[^\]]*\])?\{([0-9.]+)\\linewidth\}([\s\S]*?)\\end\{subfigure\}",
        unsub,
        body,
    )
    body = body.replace("\\hfill", " ")

    # -- PDF figures -> PNG -------------------------------------------------
    def pdf_to_png(m):
        opt, path = m.group(1), m.group(2)
        if path.lower().endswith(".pdf"):
            src = (MANU / path).resolve()
            png = work / (src.stem + ".png")
            rasterize_pdf_figure(src, png)
            path = str(png)
        else:
            path = str((MANU / path).resolve())
        return "\\includegraphics%s{%s}" % (opt or "", path)

    body = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", pdf_to_png, body)

    # -- wide floats (figure*/table*) are tracked for full-width sections --
    wide = []
    for env in ("figure*", "table*"):
        pos = 0
        while True:
            sp = env_span(body, env, pos)
            if not sp:
                break
            chunk = body[sp[0] : sp[1]]
            for lab in re.findall(r"\\label\{([^}]*)\}", chunk):
                wide.append(lab)
            pos = sp[1]
    body = body.replace("\\begin{figure*}", "\\begin{figure}").replace("\\end{figure*}", "\\end{figure}")
    body = body.replace("\\begin{table*}", "\\begin{table}").replace("\\end{table*}", "\\end{table}")
    meta["wide"] = wide

    # -- bibliography from the .bbl ------------------------------------------
    i = find_command(body, "bibliographystyle")
    body = remove_commands(body, "bibliographystyle", 1, nopt=0)
    bib = "\\section*{References}\n" + bbl_to_latex(bbl, cites)
    i = find_command(body, "bibliography")
    j, _, _ = parse_command(body, i, "bibliography", 1, 0)
    body = body[:i] + bib + body[j:]

    preamble = (
        "\\documentclass{article}\n"
        "\\newcommand{\\enquote}[1]{``#1''}\n"
        "\\newcommand{\\hrefurl}[2]{\\href{#1}{#2}}\n"
        "\\newcommand{\\urlprefix}{}\n"
        "\\begin{document}\n"
    )
    # drop the .bbl's own \providecommand preamble lines
    body = re.sub(r"\\providecommand\{\\[a-zA-Z]+\}(\[[0-9]\])?(\[[^\]]*\])?\{[^\n]*\n", "", body)
    body = re.sub(r"\\newcommand\{\\enquote\}\[1\]\{``#1''\}", "", body)
    body = re.sub(r"\\expandafter\\ifx\\csname urlstyle\\endcsname\\relax[\s\S]*?\\fi", "", body)
    return preamble + body + "\n\\end{document}\n", meta


# --------------------------------------------------------------------------
# Reference .docx: the styles that reproduce the asmejour look
# --------------------------------------------------------------------------
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NSDECL = 'xmlns:w="%s" xmlns:m="%s" xmlns:r="%s"' % (W_NS, M_NS, R_NS)


def w(tag: str) -> str:
    return "{%s}%s" % (W_NS, tag)


SERIF = "Times New Roman"
SANS = "Arial"
SANS_NARROW = "Arial Narrow"


def _font(name):
    return '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s" w:eastAsia="%s"/>' % (name, name, name, name)


def _pstyle(sid, name, based="Normal", ppr="", rpr="", custom=True, nxt=None, extra=""):
    return (
        '<w:style %s w:type="paragraph"%s w:styleId="%s"><w:name w:val="%s"/>'
        '<w:basedOn w:val="%s"/>%s%s<w:qFormat/><w:pPr>%s</w:pPr><w:rPr>%s</w:rPr></w:style>'
        % (
            NSDECL,
            ' w:customStyle="1"' if custom else "",
            sid,
            name,
            based,
            '<w:next w:val="%s"/>' % nxt if nxt else "",
            extra,
            ppr,
            rpr,
        )
    )


def _cstyle(sid, name, rpr, custom=True):
    return '<w:style %s w:type="character"%s w:styleId="%s"><w:name w:val="%s"/><w:rPr>%s</w:rPr></w:style>' % (
        NSDECL,
        ' w:customStyle="1"' if custom else "",
        sid,
        name,
        rpr,
    )


EXACT = lambda pt: '<w:spacing w:before="0" w:after="0" w:line="%d" w:lineRule="exact"/>' % round(pt * 20)
NOCOLOR = '<w:color w:val="000000"/>'

STYLE_XML = [
    _pstyle("Normal", "Normal", based="", custom=False,
            ppr='<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>',
            rpr=_font(SERIF) + '<w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:val="en-US"/>'),
    _pstyle("BodyText", "Body Text", custom=False,
            ppr=EXACT(10) + '<w:ind w:firstLine="200"/><w:jc w:val="both"/>'),
    _pstyle("FirstParagraph", "First Paragraph", based="BodyText", nxt="BodyText"),
    _pstyle("BodyTextContinued", "Body Text Continued", based="BodyText",
            ppr='<w:ind w:firstLine="0"/>'),
    _pstyle("Compact", "Compact", based="BodyText", ppr=EXACT(10) + '<w:ind w:firstLine="0"/>'),
    _pstyle("Heading1", "heading 1", custom=False, nxt="BodyText",
            ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="260" w:after="120" w:line="240" w:lineRule="exact"/>'
                '<w:outlineLvl w:val="0"/>',
            rpr='<w:b/><w:bCs/><w:sz w:val="20"/><w:szCs w:val="20"/>' + NOCOLOR),
    _pstyle("Heading2", "heading 2", custom=False, nxt="BodyText",
            ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="180" w:after="0" w:line="200" w:lineRule="exact"/>'
                '<w:ind w:firstLine="200"/><w:jc w:val="both"/><w:outlineLvl w:val="1"/>',
            rpr='<w:b/><w:bCs/><w:sz w:val="18"/><w:szCs w:val="18"/>' + NOCOLOR),
    _pstyle("Heading3", "heading 3", custom=False, nxt="BodyText",
            ppr='<w:keepNext/><w:spacing w:before="180" w:after="0" w:line="200" w:lineRule="exact"/>'
                '<w:ind w:firstLine="200"/><w:outlineLvl w:val="2"/>',
            rpr='<w:i/><w:iCs/><w:sz w:val="18"/><w:szCs w:val="18"/>' + NOCOLOR),
    _pstyle("Heading4", "heading 4", custom=False, nxt="BodyText",
            ppr='<w:keepNext/><w:spacing w:before="180" w:after="0" w:line="200" w:lineRule="exact"/>'
                '<w:ind w:firstLine="200"/><w:outlineLvl w:val="2"/>',
            rpr='<w:i/><w:iCs/><w:b w:val="0"/><w:sz w:val="18"/><w:szCs w:val="18"/>' + NOCOLOR),
    # Run-in headings: the paragraph mark is hidden (Word's style separator),
    # so the heading runs into the paragraph that follows it, as in the PDF,
    # while keeping its outline level for the navigation pane.
    # Run-in headings: a body paragraph that opens with the bold (subsection)
    # or italic (\paragraph) heading text, with the space asmejour leaves above.
    _pstyle("RuninHeading2", "Run-in Heading 2", based="BodyText", nxt="BodyText",
            ppr='<w:spacing w:before="180" w:after="0" w:line="200" w:lineRule="exact"/>'),
    _pstyle("RuninHeading4", "Run-in Heading 4", based="BodyText", nxt="BodyText",
            ppr='<w:spacing w:before="180" w:after="0" w:line="200" w:lineRule="exact"/>'),
    _pstyle("Caption", "caption", custom=False,
            ppr='<w:spacing w:before="100" w:after="200" w:line="200" w:lineRule="exact"/><w:jc w:val="both"/>',
            rpr=_font(SANS) + '<w:b/><w:bCs/><w:i w:val="0"/><w:sz w:val="16"/><w:szCs w:val="16"/>' + NOCOLOR),
    _pstyle("ImageCaption", "Image Caption", based="Caption"),
    _pstyle("TableCaption", "Table Caption", based="Caption",
            ppr='<w:keepNext/><w:spacing w:before="120" w:after="120" w:line="200" w:lineRule="exact"/>'),
    _pstyle("Figure", "Figure", ppr='<w:spacing w:before="120" w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>'),
    _pstyle("CaptionedFigure", "Captioned Figure", based="Figure", ppr="<w:keepNext/>"),
    _pstyle("FootnoteText", "footnote text", custom=False,
            ppr='<w:spacing w:before="0" w:after="0" w:line="160" w:lineRule="exact"/>',
            rpr='<w:sz w:val="14"/><w:szCs w:val="14"/>'),
    _pstyle("Bibliography", "Bibliography", custom=False,
            ppr='<w:tabs><w:tab w:val="left" w:pos="300"/></w:tabs>'
                '<w:spacing w:before="0" w:after="0" w:line="190" w:lineRule="exact"/>'
                '<w:ind w:left="300" w:hanging="300"/><w:jc w:val="both"/>',
            rpr='<w:sz w:val="16"/><w:szCs w:val="16"/>'),
    _pstyle("DraftNote", "Draft Note",
            ppr='<w:pBdr><w:top w:val="single" w:sz="4" w:space="3" w:color="%s"/>'
                '<w:left w:val="single" w:sz="4" w:space="3" w:color="%s"/>'
                '<w:bottom w:val="single" w:sz="4" w:space="3" w:color="%s"/>'
                '<w:right w:val="single" w:sz="4" w:space="3" w:color="%s"/></w:pBdr>'
                '<w:shd w:val="clear" w:color="auto" w:fill="F8F4FA"/>'
                '<w:spacing w:before="120" w:after="280" w:line="190" w:lineRule="exact"/>'
                '<w:ind w:left="160" w:right="160"/><w:jc w:val="both"/>' % ((VIOLET,) * 4),
            rpr='<w:color w:val="%s"/><w:sz w:val="16"/><w:szCs w:val="16"/>' % VIOLET),
    _pstyle("FigurePlaceholder", "Figure Placeholder",
            ppr='<w:pBdr><w:top w:val="single" w:sz="4" w:space="12" w:color="000000"/>'
                '<w:left w:val="single" w:sz="4" w:space="4" w:color="000000"/>'
                '<w:bottom w:val="single" w:sz="4" w:space="12" w:color="000000"/>'
                '<w:right w:val="single" w:sz="4" w:space="4" w:color="000000"/></w:pBdr>'
                '<w:keepNext/><w:spacing w:before="240" w:after="240" w:line="240" w:lineRule="auto"/>'
                '<w:ind w:left="240" w:right="240"/><w:jc w:val="center"/>',
            rpr='<w:i/><w:iCs/>'),
    _pstyle("TableNote", "Table Note",
            ppr='<w:spacing w:before="40" w:after="200" w:line="160" w:lineRule="exact"/><w:jc w:val="center"/>',
            rpr='<w:sz w:val="14"/><w:szCs w:val="14"/>'),
    _pstyle("TableText", "Table Text",
            ppr='<w:spacing w:before="0" w:after="0" w:line="200" w:lineRule="exact"/>',
            rpr='<w:sz w:val="16"/><w:szCs w:val="16"/>'),
    _pstyle("EquationCell", "Equation", ppr='<w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>'),
    _pstyle("Title", "Title", custom=False,
            ppr='<w:pBdr><w:left w:val="single" w:sz="36" w:space="15" w:color="000000"/></w:pBdr>'
                '<w:spacing w:before="0" w:after="260" w:line="526" w:lineRule="exact"/><w:ind w:left="380"/>',
            rpr=_font(SANS_NARROW) + '<w:b/><w:bCs/><w:sz w:val="48"/><w:szCs w:val="48"/>' + NOCOLOR),
    _pstyle("Abstract", "Abstract", custom=False,
            ppr=EXACT(10) + '<w:ind w:left="380"/><w:jc w:val="both"/>',
            rpr='<w:i/><w:iCs/><w:sz w:val="18"/><w:szCs w:val="18"/>'),
    _pstyle("Keywords", "Keywords",
            ppr='<w:spacing w:before="200" w:after="0" w:line="200" w:lineRule="exact"/><w:ind w:left="380"/><w:jc w:val="both"/>',
            rpr='<w:i/><w:iCs/><w:sz w:val="18"/><w:szCs w:val="18"/>'),
    _pstyle("AuthorName", "Author Name",
            ppr='<w:keepNext/><w:spacing w:before="0" w:after="20" w:line="260" w:lineRule="exact"/><w:jc w:val="right"/>',
            rpr=_font(SANS_NARROW) + '<w:b/><w:bCs/><w:sz w:val="25"/><w:szCs w:val="25"/>'),
    _pstyle("AuthorAffiliation", "Author Affiliation",
            ppr='<w:spacing w:before="0" w:after="320" w:line="200" w:lineRule="exact"/><w:jc w:val="right"/>',
            rpr=_font(SANS_NARROW) + '<w:sz w:val="16"/><w:szCs w:val="16"/>'),
    _pstyle("Footer", "footer", custom=False,
            ppr='<w:tabs><w:tab w:val="right" w:pos="%d"/></w:tabs>' % round(TEXT_W_IN * 1440),
            rpr=_font(SANS) + '<w:sz w:val="18"/><w:szCs w:val="18"/>'),
    _pstyle("ListHeading", "List of Figures Heading", based="Heading1",
            ppr='<w:spacing w:before="240" w:after="160"/><w:outlineLvl w:val="9"/>'),
    _pstyle("TableofFigures", "table of figures", custom=False,
            ppr='<w:tabs><w:tab w:val="left" w:pos="560"/><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs>'
                '<w:spacing w:before="0" w:after="60" w:line="220" w:lineRule="exact"/>'
                '<w:ind w:left="560" w:right="400" w:hanging="400"/><w:jc w:val="both"/>' % round(TEXT_W_IN * 1440),
            rpr='<w:sz w:val="18"/><w:szCs w:val="18"/>'),
    _pstyle("SectionBreak", "Section Break",
            ppr='<w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>',
            rpr='<w:sz w:val="2"/><w:szCs w:val="2"/>'),
    _cstyle("VerbatimChar", "Verbatim Char", _font("Consolas")),
    _cstyle("Hyperlink", "Hyperlink", '<w:color w:val="0000FF"/><w:u w:val="none"/>', custom=False),
    _cstyle("PlaceholderText", "Placeholder Text", '<w:color w:val="%s"/>' % VIOLET),
    _cstyle("LineNumber", "line number", _font(SERIF) + '<w:color w:val="FF0000"/><w:sz w:val="14"/><w:szCs w:val="14"/>',
            custom=False),
    _cstyle("FootnoteReference", "footnote reference", '<w:vertAlign w:val="superscript"/>', custom=False),
]

TABLE_STYLE = (
    '<w:style %s w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/>'
    '<w:basedOn w:val="TableNormal"/><w:qFormat/>'
    '<w:pPr><w:spacing w:before="0" w:after="0" w:line="200" w:lineRule="exact"/></w:pPr>'
    '<w:rPr><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>'
    '<w:tblPr><w:jc w:val="center"/><w:tblInd w:w="0" w:type="dxa"/>'
    '<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tblBorders>'
    '<w:tblCellMar><w:top w:w="10" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
    '<w:bottom w:w="10" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
    '<w:tblStylePr w:type="firstRow"><w:tcPr><w:tcBorders>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders></w:tcPr></w:tblStylePr>'
    "</w:style>" % NSDECL
)


def build_reference_docx(path: Path):
    from lxml import etree

    default = path.with_name("pandoc-default-reference.docx")
    subprocess.run(["pandoc", "-o", str(default), "--print-default-data-file", "reference.docx"], check=True)
    zin = zipfile.ZipFile(default)
    styles = etree.fromstring(zin.read("word/styles.xml"))
    by_id = {s.get(w("styleId")): s for s in styles.findall(w("style"))}
    for xml in STYLE_XML + [TABLE_STYLE]:
        el = etree.fromstring(xml)
        old = by_id.get(el.get(w("styleId")))
        if old is not None:
            old.getparent().replace(old, el)
        else:
            styles.append(el)
    # document defaults: Times 9 pt, US English
    dd = styles.find(w("docDefaults"))
    rpr = dd.find(w("rPrDefault")).find(w("rPr"))
    for child in list(rpr):
        rpr.remove(child)
    for xml in [_font(SERIF), '<w:sz w:val="18"/>', '<w:szCs w:val="18"/>', '<w:lang w:val="en-US"/>']:
        rpr.append(etree.fromstring(xml.replace("<w:", "<w:", 1).replace("/>", " %s/>" % NSDECL, 1)))
    # headings in pandoc's default use theme colours/fonts: neutralise
    for s in styles.findall(w("style")):
        r = s.find(w("rPr"))
        if r is None:
            continue
        for tag in ("rFonts",):
            for e in r.findall(w(tag)):
                if e.get(w("asciiTheme")):
                    r.remove(e)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                data = etree.tostring(styles, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(item, data)


# --------------------------------------------------------------------------
# Post-processing of the pandoc output
# --------------------------------------------------------------------------
TOP_MARGIN_TW = 920
BOTTOM_MARGIN_TW = 1320
FOOTER_TW = 820
SIDE_TW = round(SIDE_MARGIN_IN * 1440)
COL_SPACE_TW = round(GUTTER_IN * 1440)


def _el(xml: str):
    """Parse a WordprocessingML snippet that uses the w:/m:/r: prefixes."""
    from lxml import etree

    return etree.fromstring("<wrap %s>%s</wrap>" % (NSDECL, xml))[0]


def _xml_text(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _run(text, rpr=""):
    return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, _xml_text(text))


def _para(style, runs, ppr=""):
    return '<w:p %s><w:pPr><w:pStyle w:val="%s"/>%s</w:pPr>%s</w:p>' % (NSDECL, style, ppr, "".join(runs))


def title_block(meta, footnote_id):
    """Author column on the left, title + abstract + keywords on the right."""
    left_w = 2780
    right_w = round(TEXT_W_IN * 1440) - left_w
    cells_left = []
    first_corr = True
    for a in meta["authors"]:
        runs = [_run(a["name"])]
        if a["sup"]:
            runs.append(_run(a["sup"], '<w:vertAlign w:val="superscript"/>'))
        if a["corresponding"]:
            if first_corr:
                runs.append(
                    '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
                    '<w:color w:val="0000FF"/></w:rPr><w:footnoteReference w:id="%d"/></w:r>' % footnote_id
                )
                first_corr = False
            else:
                runs.append(_run("1", '<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="0000FF"/>'
                                      '<w:vertAlign w:val="superscript"/>'))
        cells_left.append(_para("AuthorName", runs))
        aff = []
        for k, line in enumerate(a["affil"]):
            if k:
                aff.append("<w:r><w:br/></w:r>")
            aff.append(_run(line))
        cells_left.append(_para("AuthorAffiliation", aff))
    abstract_runs = [_run(meta["abstract"])]
    if meta.get("abstract_placeholder"):
        abstract_runs.append(_run(" "))
        abstract_runs.append(_run(meta["abstract_placeholder"], '<w:rStyle w:val="PlaceholderText"/>'))
    cells_right = [
        _para("Title", [_run(meta["title"])]),
        _para("Abstract", abstract_runs),
        _para("Keywords", [_run("Keywords: " + meta["keywords"])]),
    ]
    nob = "".join('<w:%s w:val="nil"/>' % s for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    tc = lambda width, content, extra="": (
        '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>%s</w:tc>' % (width, extra, "".join(content))
    )
    return (
        '<w:tbl %s><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
        "<w:tblBorders>%s</w:tblBorders>"
        '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
        '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
        '<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/>'
        "</w:tblPr>"
        '<w:tblGrid><w:gridCol w:w="%d"/><w:gridCol w:w="%d"/></w:tblGrid>'
        "<w:tr>%s%s</w:tr></w:tbl>"
        % (
            NSDECL,
            left_w + right_w,
            nob,
            left_w,
            right_w,
            tc(left_w, cells_left, '<w:tcMar><w:top w:w="300" w:type="dxa"/><w:right w:w="160" w:type="dxa"/></w:tcMar>'),
            tc(right_w, cells_right),
        )
    )


def _sectpr(template, cols: int, lnnum: bool, footers: bool, sect_type: str | None):
    s = copy.deepcopy(template)
    for child in list(s):
        tag = child.tag.split("}")[1]
        if tag in ("cols", "lnNumType", "type") or (tag in ("footerReference", "headerReference") and not footers):
            s.remove(child)
    # schema order: header/footerReference, ..., type, pgSz, pgMar, lnNumType, pgNumType, cols, ...
    pos = 0
    for k, child in enumerate(s):
        if child.tag in (w("headerReference"), w("footerReference"), w("footnotePr"), w("endnotePr")):
            pos = k + 1
    if sect_type:
        s.insert(pos, _el('<w:type w:val="%s"/>' % sect_type))
    pgmar = s.find(w("pgMar"))
    idx = list(s).index(pgmar) + 1
    if lnnum:
        s.insert(idx, _el('<w:lnNumType w:countBy="1" w:distance="80" w:restart="continuous"/>'))
        idx += 1
    pgnum = s.find(w("pgNumType"))
    if pgnum is not None:
        idx = list(s).index(pgnum) + 1
    s.insert(idx, _el('<w:cols w:num="%d" w:space="%d"/>' % (cols, COL_SPACE_TW) if cols > 1 else '<w:cols w:space="%d"/>' % COL_SPACE_TW))
    return s


def _break_para(sectpr):
    p = _el('<w:p><w:pPr><w:pStyle w:val="SectionBreak"/></w:pPr></w:p>')
    p.find(w("pPr")).append(sectpr)
    return p


def _style_of(p):
    ppr = p.find(w("pPr"))
    if ppr is None:
        return None
    ps = ppr.find(w("pStyle"))
    return ps.get(w("val")) if ps is not None else None


def _next_element(el, tag):
    n = el.getnext()
    while n is not None and n.tag != tag:
        if n.tag in (w("p"), w("tbl")) and n.tag != tag:
            return None
        n = n.getnext()
    return n


def _field_runs(instr, cached, rpr=""):
    return (
        '<w:r><w:rPr>%s</w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:rPr>%s</w:rPr><w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
        '<w:r><w:rPr>%s</w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:rPr>%s</w:rPr><w:t>%s</w:t></w:r>'
        '<w:r><w:rPr>%s</w:rPr><w:fldChar w:fldCharType="end"/></w:r>' % (rpr, rpr, instr, rpr, rpr, cached, rpr)
    )


def size_table(tbl, avail_tw: int):
    gcs = tbl.find(w("tblGrid")).findall(w("gridCol"))
    n = len(gcs)
    nat = [400] * n
    rows = tbl.findall(w("tr"))
    for tr in rows:
        col = 0
        for tc in tr.findall(w("tc")):
            gs = tc.find(w("tcPr") + "/" + w("gridSpan"))
            span = int(gs.get(w("val"))) if gs is not None else 1
            text = "".join(t.text or "" for t in tc.iter(w("t")))
            if span == 1 and col < n:
                nat[col] = max(nat[col], round(len(text) * 82) + 200)
            col += span
    # a spanning cell (\multicolumn) needs its columns wide enough together
    for tr in rows:
        col = 0
        for tc in tr.findall(w("tc")):
            gs = tc.find(w("tcPr") + "/" + w("gridSpan"))
            span = int(gs.get(w("val"))) if gs is not None else 1
            if span > 1 and col + span <= n:
                need = round(len("".join(t.text or "" for t in tc.iter(w("t")))) * 82) + 200
                have = sum(nat[col : col + span])
                if need > have:
                    for c in range(col, col + span):
                        nat[c] += -(-(need - have) // span)
            col += span
    total = sum(nat)
    if total > avail_tw:
        nat = [max(300, round(x * avail_tw / total)) for x in nat]
        nat[-1] += avail_tw - sum(nat)
    for gc, wd in zip(gcs, nat):
        gc.set(w("w"), str(wd))
    for tr in rows:
        col = 0
        for tc in tr.findall(w("tc")):
            tcpr = tc.find(w("tcPr"))
            gs = tcpr.find(w("gridSpan")) if tcpr is not None else None
            span = int(gs.get(w("val"))) if gs is not None else 1
            tcw = tcpr.find(w("tcW")) if tcpr is not None else None
            if tcw is not None:
                tcw.set(w("type"), "dxa")
                tcw.set(w("w"), str(sum(nat[col : col + span])))
            col += span
    tblpr = tbl.find(w("tblPr"))
    tw = tblpr.find(w("tblW"))
    tw.set(w("type"), "dxa")
    tw.set(w("w"), str(sum(nat)))
    for e in tblpr.findall(w("tblLayout")):
        tblpr.remove(e)
    lay = _el('<w:tblLayout w:type="fixed"/>')
    # schema order inside tblPr: ... tblW, jc, ..., tblLayout, tblCellMar, tblLook
    anchor = tblpr.find(w("tblCellMar")) if tblpr.find(w("tblCellMar")) is not None else tblpr.find(w("tblLook"))
    if anchor is not None:
        anchor.addprevious(lay)
    else:
        tblpr.append(lay)
    if tblpr.find(w("jc")) is None:
        tw.addnext(_el('<w:jc w:val="center"/>'))


def postprocess(raw_docx: Path, out_docx: Path, meta: dict, labels: dict, date_str: str, page_of: dict | None = None):
    import docx
    from docx.shared import Twips
    from lxml import etree

    d = docx.Document(str(raw_docx))
    body = d.element.body

    # ---- pandoc re-declares custom-style names it was given; keep ours -----
    st_el = d.styles.element
    first, remap = {}, {}
    for s_ in list(st_el.findall(w("style"))):
        nm = s_.find(w("name"))
        key = (s_.get(w("type")), nm.get(w("val")) if nm is not None else s_.get(w("styleId")))
        sid = s_.get(w("styleId"))
        if key in first:
            if first[key] != sid:
                remap[sid] = first[key]
            st_el.remove(s_)
        else:
            first[key] = sid
    for el in list(body.iter(w("pStyle"))) + list(body.iter(w("rStyle"))):
        if el.get(w("val")) in remap:
            el.set(w("val"), remap[el.get(w("val"))])

    # ---- list indents as in the PDF: "(1)" 12 pt in, text at 32 pt ---------
    numbering = d.part.numbering_part.element
    for lvl in numbering.iter(w("lvl")):
        if lvl.get(w("ilvl")) != "0":
            continue
        fmt = lvl.find(w("numFmt"))
        bullet = fmt is not None and fmt.get(w("val")) == "bullet"
        ind = lvl.find(w("pPr")).find(w("ind"))
        ind.set(w("left"), "420" if bullet else "640")
        ind.set(w("hanging"), "220" if bullet else "400")

    # ---- page geometry, footers, line numbers (final section) -------------
    sec = d.sections[0]
    sec.page_width = Twips(round(PAGE_W_IN * 1440))
    sec.page_height = Twips(round(PAGE_H_IN * 1440))
    sec.left_margin = sec.right_margin = Twips(SIDE_TW)
    sec.top_margin = Twips(TOP_MARGIN_TW)
    sec.bottom_margin = Twips(BOTTOM_MARGIN_TW)
    sec.header_distance = Twips(500)
    sec.footer_distance = Twips(FOOTER_TW)
    d.settings.odd_and_even_pages_header_footer = True

    def footer_xml(even):
        b = "<w:b/><w:bCs/>"
        page = _field_runs("PAGE", "1", b)
        if even:
            runs = page + _run(" / ", b) + _run("PREPRINT FOR REVIEW") + "<w:r><w:tab/></w:r>" + _run("Transactions of the ASME", b)
        else:
            runs = _run("Journal of Mechanical Design", b) + "<w:r><w:tab/></w:r>" + _run("PREPRINT FOR REVIEW") + _run(" / ", b) + page
        return _el('<w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr>%s</w:p>' % runs)

    for ftr, even in ((sec.footer, False), (sec.even_page_footer, True)):
        ftr.is_linked_to_previous = False
        el = ftr._element
        for p in el.findall(w("p")):
            el.remove(p)
        el.append(footer_xml(even))

    final = body.find(w("sectPr"))
    template = copy.deepcopy(final)

    # ---- corresponding-author footnote --------------------------------------
    fn_part = None
    for rel in d.part.rels.values():
        if rel.reltype.endswith("/footnotes"):
            fn_part = rel.target_part
    fn_root = etree.fromstring(fn_part.blob) if not hasattr(fn_part, "element") else fn_part.element
    ids = [int(f.get(w("id"))) for f in fn_root.findall(w("footnote"))]
    fn_id = max(ids + [0]) + 1
    fn_root.append(
        _el(
            '<w:footnote w:id="%d">'
            '<w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
            '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
            '<w:r><w:t xml:space="preserve">Corresponding Author.</w:t></w:r></w:p>'
            '<w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr><w:r><w:t>%s</w:t></w:r></w:p>'
            "</w:footnote>" % (fn_id, _xml_text(date_str))
        )
    )
    if not hasattr(fn_part, "element"):
        fn_part._blob = etree.tostring(fn_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # ---- title block + its one-column section ----------------------------
    tb = _el(title_block(meta, fn_id))
    body.insert(0, tb)
    tb.addnext(_break_para(_sectpr(template, 1, False, True, None)))

    # ---- equations: borderless two-cell tables ------------------------------
    col_tw = round(COL_W_IN * 1440)
    for p in list(body.iter(w("p"))):
        if _style_of(p) != "EqTableMarker":
            continue
        tbl = _next_element(p, w("tbl"))
        p.getparent().remove(p)
        if tbl is None:
            continue
        tblpr = tbl.find(w("tblPr"))
        for child in list(tblpr):
            tblpr.remove(child)
        nob = "".join('<w:%s w:val="nil"/>' % s for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
        for xml in (
            '<w:tblW w:w="%d" w:type="dxa"/>' % col_tw,
            '<w:jc w:val="center"/>',
            "<w:tblBorders>%s</w:tblBorders>" % nob,
            '<w:tblLayout w:type="fixed"/>',
            '<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>',
            '<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/>',
        ):
            tblpr.append(_el(xml))
        grid = tbl.find(w("tblGrid"))
        widths = [round(col_tw * 0.88), col_tw - round(col_tw * 0.88)]
        for gc, wd in zip(grid.findall(w("gridCol")), widths):
            gc.set(w("w"), str(wd))
        for k, tc in enumerate(tbl.iter(w("tc"))):
            tcpr = tc.find(w("tcPr"))
            if tcpr is None:
                tcpr = _el("<w:tcPr/>")
                tc.insert(0, tcpr)
            for child in list(tcpr):
                if child.tag in (w("tcW"), w("vAlign")):
                    tcpr.remove(child)
            tcpr.insert(0, _el('<w:tcW w:w="%d" w:type="dxa"/>' % widths[k % 2]))
            tcpr.append(_el('<w:vAlign w:val="center"/>'))
            for cp in tc.findall(w("p")):
                ppr = cp.find(w("pPr"))
                if ppr is None:
                    ppr = _el("<w:pPr/>")
                    cp.insert(0, ppr)
                ps = ppr.find(w("pStyle"))
                if ps is None:
                    ps = _el('<w:pStyle w:val="EquationCell"/>')
                    ppr.insert(0, ps)
                ps.set(w("val"), "EquationCell")
                jc = ppr.find(w("jc"))
                if jc is not None:
                    ppr.remove(jc)
                ppr.append(_el('<w:jc w:val="%s"/>' % ("center" if k % 2 == 0 else "right")))
        tbl.set("data-eq", "1")

    # ---- data tables: Table Text paragraphs, natural width, centred --------
    def is_figure_table(t):
        st_ = t.find(w("tblPr") + "/" + w("tblStyle"))
        return st_ is not None and st_.get(w("val")) == "FigureTable"

    for tbl in body.iter(w("tbl")):
        if tbl.get("data-eq") or tbl is tb or is_figure_table(tbl):
            continue
        tblpr = tbl.find(w("tblPr"))
        tw = tblpr.find(w("tblW"))
        if tw is not None:
            tw.set(w("type"), "auto")
            tw.set(w("w"), "0")
        lay = tblpr.find(w("tblLayout"))
        if lay is not None:
            tblpr.remove(lay)
        for tcw in tbl.iter(w("tcW")):
            tcw.set(w("type"), "auto")
            tcw.set(w("w"), "0")
        for cp in tbl.iter(w("p")):
            ppr = cp.find(w("pPr"))
            if ppr is None:
                ppr = _el("<w:pPr/>")
                cp.insert(0, ppr)
            ps = ppr.find(w("pStyle"))
            if ps is None:
                ps = _el('<w:pStyle w:val="TableText"/>')
                ppr.insert(0, ps)
            ps.set(w("val"), "TableText")
    for tbl in body.iter(w("tbl")):
        if "data-eq" in tbl.attrib:
            del tbl.attrib["data-eq"]


    # ---- full-width sections for figure* / table* ---------------------------
    markers = [p for p in body.iter(w("p")) if _style_of(p) in ("WideStart", "WideEnd")]
    # merge back-to-back wide floats into one full-width section
    k = 0
    drop = set()
    while k < len(markers) - 1:
        a, b = markers[k], markers[k + 1]
        if _style_of(a) == "WideEnd" and _style_of(b) == "WideStart":
            n = a.getnext()
            while n is not None and n is not b and n.tag in (w("bookmarkStart"), w("bookmarkEnd")):
                n = n.getnext()
            if n is b:
                drop.update([id(a), id(b)])
        k += 1
    for p in markers:
        if id(p) in drop:
            p.getparent().remove(p)
            continue
        if _style_of(p) == "WideStart":
            p.addprevious(_break_para(_sectpr(template, 2, True, False, "continuous")))
        else:
            p.addprevious(_break_para(_sectpr(template, 1, False, False, "continuous")))
        p.getparent().remove(p)

    # ---- lists of figures and tables (new page, one column) ----------------
    by_num = {}
    for key, num in labels.items():
        kind = "fig" if key.startswith("fig:") else "tab" if key.startswith("tab:") else None
        if kind and num.isdigit():
            by_num[(kind, num)] = "lbl_" + re.sub(r"[^0-9A-Za-z]", "_", key)
            by_num[(kind, num)] = by_num[(kind, num)][:40]
    entries = {"fig": [], "tab": []}
    for p in body.iter(w("p")):
        st = _style_of(p)
        if st not in ("ImageCaption", "TableCaption"):
            continue
        runs = [r for r in p if r.tag in (w("r"), w("hyperlink"))]
        text = "".join(t.text or "" for t in p.iter(w("t")))
        m = re.match(r"(Fig\.|Table) (\d+) ", text)
        if not m:
            continue
        kind = "fig" if m.group(1) == "Fig." else "tab"
        # drop the leading "Fig. N" label, up to and including the em space
        content = []
        found = False
        for r in runs:
            if found:
                content.append(copy.deepcopy(r))
                continue
            ts = list(r.iter(w("t")))
            joined = "".join(t.text or "" for t in ts)
            if "\u2003" in joined:
                found = True
                rest = joined.split("\u2003", 1)[1]
                if rest:
                    rc = copy.deepcopy(r)
                    tcs = list(rc.iter(w("t")))
                    tcs[0].text = rest
                    tcs[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                    for t in tcs[1:]:
                        t.getparent().remove(t)
                    content.append(rc)
        # bookmark the caption itself as the target of the PAGEREF field below
        bname = "cap_%s%s" % (kind, m.group(2))
        bid = str(90000 + len(entries["fig"]) + len(entries["tab"]))
        ppr = p.find(w("pPr"))
        if ppr is not None:
            ppr.addnext(_el('<w:bookmarkStart w:id="%s" w:name="%s"/>' % (bid, bname)))
        else:
            p.insert(0, _el('<w:bookmarkStart w:id="%s" w:name="%s"/>' % (bid, bname)))
        p.append(_el('<w:bookmarkEnd w:id="%s"/>' % bid))
        for r in content:
            for rpr in r.iter(w("rPr")):
                for b in rpr.findall(w("b")) + rpr.findall(w("bCs")):
                    rpr.remove(b)
        entries[kind].append((m.group(2), content, bname))
    last = body.find(w("sectPr"))
    # end the two-column body before the lists
    last.addprevious(_break_para(_sectpr(template, 2, True, False, "continuous")))
    for kind, heading in (("fig", "List of Figures"), ("tab", "List of Tables")):
        last.addprevious(_el(_para("ListHeading", [_run(heading)])))
        for num, content, bname in entries[kind]:
            p = _el('<w:p><w:pPr><w:pStyle w:val="TableofFigures"/></w:pPr></w:p>')
            p.append(_el(_run(num)))
            p.append(_el("<w:r><w:tab/></w:r>"))
            for r in content:
                p.append(r)
            p.append(_el("<w:r><w:tab/></w:r>"))
            bmk = bname
            cached = str((page_of or {}).get((kind, num), ""))
            if bmk:
                for x in etree.fromstring("<x %s>%s</x>" % (NSDECL, _field_runs("PAGEREF %s \\h" % bmk, cached or "?"))):
                    p.append(x)
            last.addprevious(p)
    # the final section: lists of figures/tables on a new page, one column
    new_last = _sectpr(template, 1, False, False, "nextPage")
    body.replace(last, new_last)

    # every section after the first starts on the same page unless set above
    sects = list(body.iter(w("sectPr")))
    for s in sects[1:-1]:
        if s.find(w("type")) is None:
            s.insert(0, _el('<w:type w:val="continuous"/>'))

    # ---- data tables: explicit column widths from the cell contents, capped
    # at the width of the column (or page, for table*) they sit in ---------
    section_cols, pending = {}, []
    for child in body:
        pending.append(child)
        sp = child.find(w("pPr") + "/" + w("sectPr")) if child.tag == w("p") else None
        if child.tag == w("sectPr"):
            sp = child
        if sp is not None:
            cols = sp.find(w("cols"))
            n = int(cols.get(w("num"), "1")) if cols is not None else 1
            for e in pending:
                section_cols[id(e)] = n
            pending = []
    for tbl in body.findall(w("tbl")):
        if tbl is tb or tbl.find(w("tblPr") + "/" + w("tblBorders")) is not None:
            continue  # title block and equation tables are already laid out
        avail = round((COL_W_IN if section_cols.get(id(tbl), 2) == 2 else TEXT_W_IN) * 1440)
        if is_figure_table(tbl):
            # pandoc's one-cell layout table around a multi-part figure
            tblpr = tbl.find(w("tblPr"))
            tblpr.find(w("tblW")).set(w("type"), "dxa")
            tblpr.find(w("tblW")).set(w("w"), str(avail))
            for gc in tbl.find(w("tblGrid")).findall(w("gridCol")):
                gc.set(w("w"), str(avail))
            for tcw in tbl.iter(w("tcW")):
                tcw.set(w("type"), "dxa")
                tcw.set(w("w"), str(avail))
            continue
        size_table(tbl, avail)

    # ---- list items (pandoc leaves them in Normal): justified body text ----
    for p in body.iter(w("p")):
        ppr = p.find(w("pPr"))
        if ppr is not None and ppr.find(w("numPr")) is not None and ppr.find(w("pStyle")) is None:
            ppr.insert(0, _el('<w:pStyle w:val="Compact"/>'))

    # ---- lines holding an inline Word equation may grow rather than clip ---
    for p in body.iter(w("p")):
        if p.find(".//" + "{%s}oMath" % M_NS) is None or p.find(".//" + "{%s}oMathPara" % M_NS) is not None:
            continue
        ppr = p.find(w("pPr"))
        if ppr is None:
            ppr = _el("<w:pPr/>")
            p.insert(0, ppr)
        sp = ppr.find(w("spacing"))
        if sp is None:
            sp = _el("<w:spacing/>")
            ps = ppr.find(w("pStyle"))
            (ps.addnext(sp) if ps is not None else ppr.insert(0, sp))
        sp.set(w("line"), "200")
        sp.set(w("lineRule"), "atLeast")

    # ---- settings: automatic hyphenation (LaTeX hyphenates too) ------------
    st = d.settings.element
    if st.find(w("autoHyphenation")) is None:
        st.append(_el('<w:autoHyphenation w:val="true"/>'))

    cp = d.core_properties
    cp.title = meta["title"]
    cp.author = "; ".join(a["name"] for a in meta["authors"])
    cp.keywords = meta["keywords"]
    cp.subject = "Manuscript draft for ASME Journal of Mechanical Design"
    cp.comments = "Generated from manuscript.tex by scripts/docx/build_manuscript_docx.py"
    d.save(str(out_docx))


def caption_pages(docx_path: Path, work: Path) -> dict:
    """Page of every figure/table caption in a LibreOffice rendering."""
    import fitz

    if not shutil.which("soffice"):
        return {}
    outdir = work / "render"
    outdir.mkdir(exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(docx_path)],
        check=True, capture_output=True,
    )
    pdf = fitz.open(outdir / (docx_path.stem + ".pdf"))
    pages = {}
    for pno in range(pdf.page_count):
        text = pdf[pno].get_text("text")
        for m in re.finditer(r"(Fig\.|Table)\s(\d+) ", text):
            kind = "fig" if m.group(1) == "Fig." else "tab"
            pages.setdefault((kind, m.group(2)), pno + 1)
    return pages


# --------------------------------------------------------------------------
def build_latex(work: Path) -> Path:
    build = work / "latex"
    mdir = build / "manuscript"
    if (mdir / "manuscript.aux").exists() and (mdir / "manuscript.bbl").exists():
        return mdir
    shutil.copytree(MANU, mdir, ignore=shutil.ignore_patterns("*.pdf", "*.docx", "preview", "data"))
    shutil.copytree(REPO / "figures", build / "figures")
    steps = [
        ["pdflatex", "-interaction=nonstopmode", "manuscript"],
        ["bibtex", "manuscript"],
        ["pdflatex", "-interaction=nonstopmode", "manuscript"],
        ["pdflatex", "-interaction=nonstopmode", "manuscript"],
    ]
    for cmd in steps:
        subprocess.run(cmd, cwd=mdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not (mdir / "manuscript.aux").exists():
        sys.exit("LaTeX build failed; see %s/manuscript.log" % mdir)
    return mdir


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(MANU / "manuscript.docx"))
    ap.add_argument("--pdf", default=str(MANU / "manuscript.pdf"),
                    help="compiled manuscript PDF; Fig. 2(b) with its TikZ callouts is cropped from it")
    ap.add_argument("--date", default=DEFAULT_DATE, help="date printed under the corresponding-author note")
    ap.add_argument("--work", default=None, help="scratch directory (default: a new temporary directory)")
    ap.add_argument("--keep-tmp", action="store_true")
    ap.add_argument("--no-render", action="store_true", help="skip the LibreOffice pass that fills list page numbers")
    args = ap.parse_args()

    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="manuscript-docx-"))
    work.mkdir(parents=True, exist_ok=True)
    mdir = build_latex(work)
    labels, cites = parse_aux((mdir / "manuscript.aux").read_text())
    bbl = (mdir / "manuscript.bbl").read_text()

    tex, meta = preprocess((MANU / "manuscript-body.tex").read_text(), work, labels, cites, bbl, Path(args.pdf))
    (work / "manuscript-docx.tex").write_text(tex)
    aux_json = work / "aux.json"
    aux_json.write_text(json.dumps({
        "labels": labels, "cites": cites, "wide": meta["wide"],
        "text_w_in": TEXT_W_IN, "col_w_in": COL_W_IN,
    }))
    ref = work / "reference.docx"
    build_reference_docx(ref)
    raw = work / "pandoc.docx"
    env = dict(os.environ, MANU_DOCX_AUX=str(aux_json))
    res = subprocess.run(
        ["pandoc", "-f", "latex", "-t", "docx", "--reference-doc", str(ref), "--lua-filter", str(LUA_FILTER),
         "--resource-path", str(MANU), "-o", str(raw), str(work / "manuscript-docx.tex")],
        env=env, capture_output=True, text=True,
    )
    sys.stderr.write(res.stderr)
    if res.returncode:
        sys.exit("pandoc failed")
    out = Path(args.out)
    postprocess(raw, out, meta, labels, args.date)
    if not args.no_render:
        pages = caption_pages(out, work)
        if pages:
            postprocess(raw, out, meta, labels, args.date, pages)
    print("wrote", out)
    if not args.keep_tmp and not args.work:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
