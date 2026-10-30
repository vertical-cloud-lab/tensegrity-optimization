#!/usr/bin/env python3
"""Build the drop tower SOP Word template (issue #115).

Writes docs/drop-tower-sop/drop-tower-sop-template.docx from the figures in
docs/drop-tower-sop/figures/. Once people start editing the .docx by hand,
the .docx is the master copy: re-running this script overwrites it.

    python scripts/build_drop_tower_sop.py            # build the .docx
    python scripts/build_drop_tower_sop.py --render   # also fill the table of
        # contents page numbers and write a PDF preview (needs LibreOffice
        # `soffice` and `pip install pypdf`)
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "drop-tower-sop"
FIG = OUT_DIR / "figures"
OUT = OUT_DIR / "drop-tower-sop-template.docx"

REPO = "https://github.com/vertical-cloud-lab/tensegrity-optimization"
PROTO = "f6471ad"  # tip of copilot/add-drop-test-protocol-again (PR #86 data and docs)
EQUIP = "05b6344"  # tip of copilot/add-drop-tower-picture (Lansmont M23 notes)
PHOTOS = "47db4b1"  # tip of claude/request-b-figures-20261027 (manuscript photos)
PHOTOS_OLD = "38f7171"  # tip of claude/part2-review-edits-20261010


def blob(sha, path):
    return f"{REPO}/blob/{sha}/{path}"


L = {
    "issue115": f"{REPO}/issues/115",
    "workspace": f"{REPO}/issues/115#issuecomment-6150496994",
    "halt": f"{REPO}/issues/115#issuecomment-6277017048",
    "request": f"{REPO}/issues/115#issuecomment-6511037439",
    "calendar": "https://verticalcloudlabbyu.slack.com/archives/C0B2MFR5V3L/p1790987654470499",
    "protocol": blob(PROTO, "docs/drop-test-protocol.md"),
    "hook": blob(PROTO, "docs/drop-test-hook-troubleshooting.md"),
    "hook_report": f"{REPO}/pull/86#issuecomment-5051519185",
    "pr86": f"{REPO}/pull/86",
    "pr28": f"{REPO}/pull/28",
    "issue27": f"{REPO}/issues/27",
    "issue36": f"{REPO}/issues/36",
    "issue36_photo": f"{REPO}/issues/36#issuecomment-4509083060",
    "issue36_bungee": f"{REPO}/issues/36#issuecomment-4546364370",
    "issue92": f"{REPO}/issues/92",
    "pin_halt": f"{REPO}/issues/92#issuecomment-5183508899",
    "pin_fixed": f"{REPO}/issues/92#issuecomment-5198107974",
    "pin_closed": f"{REPO}/issues/92#issuecomment-5272416211",
    "liftoff": f"{REPO}/issues/36#issuecomment-4545983664",
    "height77": f"{REPO}/issues/36#issuecomment-4606191756",
    "sens_default": f"{REPO}/pull/74#issuecomment-4663450421",
    "dytran": f"{REPO}/pull/74#issuecomment-4792400480",
    "pr67": f"{REPO}/pull/67",
    "vertex_fell": f"{REPO}/pull/67#issuecomment-4783408053",
    "halfseat": f"{REPO}/pull/67#issuecomment-4867769577",
    "rod_tie": f"{REPO}/pull/67#issuecomment-4870839517",
    "ch5_fell": f"{REPO}/pull/67#issuecomment-4872786485",
    "rotate": f"{REPO}/pull/35#issuecomment-4895789291",
    "tape_entrance": f"{REPO}/pull/67#issuecomment-4918818168",
    "handle": f"{REPO}/pull/67#issuecomment-4938319387",
    "overload": f"{REPO}/pull/82#issuecomment-4983665345",
    "hook_fixed": f"{REPO}/pull/86#issuecomment-5051832087",
    "reenable": f"{REPO}/pull/86#issuecomment-5121788190",
    "tp4_cleared": f"{REPO}/pull/86#issuecomment-5347154331",
    "pu_stick": f"{REPO}/issues/88#issuecomment-5134564783",
    "issue91": f"{REPO}/issues/91",
    "video_auto": "https://youtu.be/TXerxMYEsDM",
    "video_tp4db": "https://youtu.be/BSK_UcERTVw",
    "m23": blob(EQUIP, "equipment/lansmont-m23/README.md"),
    "m23_sheet": blob(EQUIP, "equipment/lansmont-m23/M23_Data_Sheet_official.pdf"),
    "m23_photo": blob(EQUIP, "equipment/lansmont-m23/images/m23_lansmont_datasheet_photo.png"),
    "m23_vendor": "https://www.lansmont.com/sites/default/files/2025-10/M23%20Data%20Sheet.pdf",
    "video": "https://youtu.be/RNjpAmWWmkQ",
    "drops30": blob(PROTO, "data/drop-tests/30drops-real/README.md"),
    "drift1": blob(PROTO, "data/drop-tests/drift-calibration/README.md"),
    "drift2": blob(PROTO, "data/drop-tests/drift-calibration2/README.md"),
    "keymount": blob(PROTO, "data/drop-tests/key-mounted/README.md"),
    "keywax": blob(PROTO, "data/drop-tests/key-mounted-wax/README.md"),
    "vertex": blob(PROTO, "data/drop-tests/vertex-acrylic/README.md"),
    "abc123": blob(PROTO, "docs/drop-test-abc123-blind-analysis.md"),
    "grease": blob(PROTO, "data/drop-tests/pre-post-grease/README.md"),
    "calcheck": blob(PROTO, "docs/drop-test-calibration-check-analysis.md"),
    "tp4_photo": blob(PROTO, "data/drop-tests/calibration-check/tp4-settings-2026-08-18.jpg"),
    "ch5": blob(PROTO, "data/drop-tests/1sne-checkin/ch5-fault-and-replicates.md"),
    "ch5_lab": blob(PROTO, "data/drop-tests/1sne-checkin/README.md"),
    "felts60": blob(PROTO, "docs/drop-test-60in-5felts-analysis.md"),
    "montage": blob(PROTO, "data/drop-tests/60in-5felts-validation/video/figures/07_video_montage_9GMQYQ.png"),
    "printdefects": blob(PROTO, "data/drop-tests/print-defects/README.md"),
    "drops200": blob(PROTO, "data/drop-tests/200drops/README.md"),
    "setup_photo": blob(PHOTOS, "figures/photos/overview-src/carriage-specimen-mdt6ja.jpg"),
    "photo_readme": blob(PHOTOS, "figures/photos/overview/README.md"),
    "table_photo": blob(PHOTOS_OLD, "figures/photos/drop-tower.jpg"),
}

# Figure numbers, in order of appearance (SOP.figure checks the order).
FIGS = {"workspace": 1, "m23": 2, "setup": 3, "console": 4, "pins": 5, "table": 6, "cable": 7, "tp4": 8,
        "impact": 9}

NAVY = RGBColor(0x1F, 0x38, 0x64)
GRAY = RGBColor(0x59, 0x59, 0x59)
LIGHT = "EAF0F8"
HEAD_FILL = "D9E2F3"
WARN_FILL = "FFF2CC"

TOKEN = re.compile(r"(\*\*.+?\*\*|\[[^\]]+\]|\{[^{}|]+\|[^{}]+\})")


class SOP:
    def __init__(self):
        self.doc = Document()
        self.headings = []  # (level, text)
        self.fig_n = 0
        self._setup()

    # ------------------------------------------------------------------ setup
    def _setup(self):
        d = self.doc
        sec = d.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for side in ("left_margin", "right_margin"):
            setattr(sec, side, Inches(1))
        sec.top_margin, sec.bottom_margin = Inches(0.8), Inches(0.8)
        sec.header_distance, sec.footer_distance = Inches(0.4), Inches(0.4)
        st = d.styles
        normal = st["Normal"]
        normal.font.name = "Calibri"
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        normal.font.size = Pt(10.5)
        normal.paragraph_format.space_after = Pt(4)
        normal.paragraph_format.line_spacing = 1.08
        for name, size, before in (("Heading 1", 15, 16), ("Heading 2", 12, 10)):
            s = st[name]
            s.font.name = "Calibri"
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.color.rgb = NAVY
            rpr = s.element.get_or_add_rPr()
            fonts = rpr.find(qn("w:rFonts"))
            if fonts is None:
                fonts = OxmlElement("w:rFonts")
                rpr.insert(0, fonts)
            for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                fonts.set(qn(a), "Calibri")
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                if fonts.get(qn(a)) is not None:
                    del fonts.attrib[qn(a)]
            s.paragraph_format.space_before = Pt(before)
            s.paragraph_format.space_after = Pt(4)
            s.paragraph_format.keep_with_next = True
        cap = st["Caption"]
        cap.font.size = Pt(9)
        cap.font.italic = False
        cap.font.bold = False
        cap.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
        cap.paragraph_format.space_after = Pt(10)
        for name in ("List Number", "List Bullet"):
            st[name].paragraph_format.space_after = Pt(2)
            st[name].font.size = Pt(10.5)
        for lvl, size, bold, before, indent in ((1, 10, True, 3, 0.0), (2, 9.5, False, 0, 0.3)):
            ts = st.add_style(f"toc {lvl}", WD_STYLE_TYPE.PARAGRAPH)
            ts.base_style = normal
            ts.font.size, ts.font.bold = Pt(size), bold
            tpf = ts.paragraph_format
            tpf.space_before, tpf.space_after, tpf.line_spacing = Pt(before), Pt(0), 1.0
            tpf.left_indent = Inches(indent)
            tpf.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        lab = st.add_style("SOP Label", WD_STYLE_TYPE.PARAGRAPH)
        lab.base_style = normal
        lab.font.bold = True
        lab.font.color.rgb = NAVY
        lab.paragraph_format.space_before = Pt(8)
        lab.paragraph_format.space_after = Pt(2)
        lab.paragraph_format.keep_with_next = True
        self._header_footer()

    def _header_footer(self):
        sec = self.doc.sections[0]
        hp = sec.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = hp.add_run("Drop Tower SOP, CB 152A  |  DRAFT: not approved for use")
        r.font.size, r.font.color.rgb = Pt(8.5), GRAY
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("Revision 0.1 (template), 2026-10-29  |  Page ")
        r.font.size, r.font.color.rgb = Pt(8.5), GRAY
        self._field(fp, "PAGE", "1")
        r = fp.add_run(" of ")
        r.font.size, r.font.color.rgb = Pt(8.5), GRAY
        self._field(fp, "NUMPAGES", "1")

    @staticmethod
    def _fld_run(kind):
        r = OxmlElement("w:r")
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), kind)
        r.append(fc)
        return r

    def _field(self, par, code, shown):
        p = par._p
        p.append(self._fld_run("begin"))
        r = OxmlElement("w:r")
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = f" {code} "
        r.append(it)
        p.append(r)
        p.append(self._fld_run("separate"))
        run = par.add_run(shown)
        run.font.size, run.font.color.rgb = Pt(8.5), GRAY
        p.append(self._fld_run("end"))

    # ------------------------------------------------------------ inline text
    def rich(self, par, text, size=None, color=None, bold=False, italic=False):
        """Add text with **bold**, [placeholder] and {link text|url} markup."""
        for tok in TOKEN.split(text):
            if not tok:
                continue
            if tok.startswith("**") and tok.endswith("**"):
                r = par.add_run(tok[2:-2])
                r.bold = True
            elif tok.startswith("[") and tok.endswith("]"):
                r = par.add_run(tok)
                r.font.highlight_color = WD_COLOR_INDEX.GRAY_25
                r.bold = bold
            elif tok.startswith("{") and tok.endswith("}"):
                label, url = tok[1:-1].split("|", 1)
                self.link(par, label, url, size=size)
                continue
            else:
                r = par.add_run(tok)
                r.bold = bold or None
            r.italic = italic or None
            if size:
                r.font.size = Pt(size)
            if color is not None:
                r.font.color.rgb = color
        return par

    def link(self, par, text, url, size=None):
        r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
        h = OxmlElement("w:hyperlink")
        h.set(qn("r:id"), r_id)
        r = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        c = OxmlElement("w:color")
        c.set(qn("w:val"), "0563C1")
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rpr.append(c)
        if size:
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), str(int(size * 2)))
            rpr.append(sz)
        rpr.append(u)
        r.append(rpr)
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = text
        r.append(t)
        h.append(r)
        par._p.append(h)

    # --------------------------------------------------------------- blocks
    def h1(self, text, page_break=False):
        self.headings.append((1, text))
        h = self.doc.add_heading(text, level=1)
        h.paragraph_format.page_break_before = page_break or None
        return h

    def h2(self, text):
        self.headings.append((2, text))
        return self.doc.add_heading(text, level=2)

    def p(self, text="", style=None, **kw):
        par = self.doc.add_paragraph(style=style)
        return self.rich(par, text, **kw)

    def label(self, text):
        return self.doc.add_paragraph(text, style="SOP Label")

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def _new_num(self):
        numbering = self.doc.part.numbering_part.element
        style = self.doc.styles["List Number"]
        num_id = style.element.pPr.numPr.numId.val
        abstract_id = numbering.num_having_numId(num_id).abstractNumId.val
        num = numbering.add_num(abstract_id)
        num.add_lvlOverride(ilvl=0).add_startOverride(1)
        return num.numId

    def numbered(self, items, container=None):
        target = container if container is not None else self.doc
        num_id = self._new_num()
        for it in items:
            par = target.add_paragraph(style="List Number")
            numpr = par._p.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = 0
            numpr.get_or_add_numId().val = num_id
            self.rich(par, it)

    def bullets(self, items, container=None):
        target = container if container is not None else self.doc
        for it in items:
            self.rich(target.add_paragraph(style="List Bullet"), it)

    def box(self, title, text, fill=LIGHT, items=None):
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._widths(t, [6.5])
        self._borders(t, "A6B8D9")
        c = t.rows[0].cells[0]
        c.width = Inches(6.5)
        self._shade(c, fill)
        par = c.paragraphs[0]
        r = par.add_run(title + " ")
        r.bold = True
        r.font.color.rgb = NAVY
        self.rich(par, text)
        if items:
            self.bullets(items, container=c)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)
        return t

    def must_cover(self, text):
        return self.box("What this section must cover:", text)

    def section_block(self, procedure, verify, stop, sources=None, intro=None):
        if intro:
            for line in intro:
                self.p(line)
        self.label("Procedure")
        self.numbered(procedure)
        self.label("How it is verified")
        self.bullets(verify)
        self.label("Stop the test if")
        self.bullets(stop)
        if sources:
            self.label("Sources and related records")
            self.bullets(sources)

    @staticmethod
    def _shade(cell, fill):
        tcpr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        tcpr.append(shd)

    @staticmethod
    def _borders(table, color="8EAADB"):
        tblpr = table._tbl.tblPr
        b = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), color)
            b.append(e)
        SOP._insert(tblpr, b, ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption"))

    @staticmethod
    def _checkbox(par):
        w14 = "http://schemas.microsoft.com/office/word/2010/wordml"
        sdt = OxmlElement("w:sdt")
        sdtpr = OxmlElement("w:sdtPr")
        from lxml import etree

        cb = etree.SubElement(sdtpr, f"{{{w14}}}checkbox")
        etree.SubElement(cb, f"{{{w14}}}checked").set(f"{{{w14}}}val", "0")
        cs = etree.SubElement(cb, f"{{{w14}}}checkedState")
        cs.set(f"{{{w14}}}val", "2612")
        cs.set(f"{{{w14}}}font", "MS Gothic")
        us = etree.SubElement(cb, f"{{{w14}}}uncheckedState")
        us.set(f"{{{w14}}}val", "2610")
        us.set(f"{{{w14}}}font", "MS Gothic")
        sdt.append(sdtpr)
        content = OxmlElement("w:sdtContent")
        r = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        fonts = OxmlElement("w:rFonts")
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia"):
            fonts.set(qn(a), "MS Gothic")
        rpr.append(fonts)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "24")
        rpr.append(sz)
        r.append(rpr)
        t = OxmlElement("w:t")
        t.text = "☐"
        r.append(t)
        content.append(r)
        sdt.append(content)
        par._p.append(sdt)

    @staticmethod
    def _widths(t, widths):
        """Fixed layout with real column widths (Word and LibreOffice both honor the grid)."""
        t.autofit = False
        for gc, w in zip(t._tbl.tblGrid.gridCol_lst, widths):
            gc.w = Inches(w)
        tblw = t._tbl.tblPr.find(qn("w:tblW"))
        if tblw is None:
            tblw = OxmlElement("w:tblW")
            SOP._insert(t._tbl.tblPr, tblw, ("w:jc", "w:tblInd", "w:tblBorders", "w:shd", "w:tblLayout",
                                             "w:tblCellMar", "w:tblLook"))
        tblw.set(qn("w:type"), "dxa")
        tblw.set(qn("w:w"), str(int(round(sum(widths) * 1440))))

    @staticmethod
    def _insert(parent, el, successors):
        for tag in successors:
            nxt = parent.find(qn(tag))
            if nxt is not None:
                nxt.addprevious(el)
                return
        parent.append(el)

    def table(self, header, rows, widths, font=9.5, checkbox_col=None, header_fill=HEAD_FILL, container=None):
        target = container if container is not None else self.doc
        t = target.add_table(rows=1, cols=len(header))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._widths(t, widths)
        self._borders(t)
        trpr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trpr.append(th)
        for i, h in enumerate(header):
            c = t.rows[0].cells[i]
            c.width = Inches(widths[i])
            self._shade(c, header_fill)
            par = c.paragraphs[0]
            r = par.add_run(h)
            r.bold = True
            r.font.size = Pt(font)
        for row in rows:
            cells = t.add_row().cells
            for i, val in enumerate(row):
                c = cells[i]
                c.width = Inches(widths[i])
                par = c.paragraphs[0]
                par.paragraph_format.space_after = Pt(1)
                if checkbox_col is not None and i == checkbox_col:
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    self._checkbox(par)
                    continue
                parts = val if isinstance(val, list) else [val]
                for k, part in enumerate(parts):
                    if k:
                        par = c.add_paragraph()
                        par.paragraph_format.space_after = Pt(1)
                    self.rich(par, part, size=font)
        if container is None:
            self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def checklist(self, rows, title_col="Check", ref_col="Section"):
        body = [["", text, ref] for text, ref in rows]
        return self.table(["Done", title_col, ref_col], body, [0.55, 5.0, 0.95], font=10, checkbox_col=0)

    def figure(self, key, path, width, caption, credit, container=None):
        self.fig_n += 1
        assert FIGS[key] == self.fig_n, f"figure {key} is number {self.fig_n}, FIGS says {FIGS[key]}"
        target = container if container is not None else self.doc
        par = target.paragraphs[0] if container is not None and not target.paragraphs[0].text else target.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_after = Pt(2)
        par.add_run().add_picture(str(path), width=Inches(width))
        cap = target.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Figure {self.fig_n}. ")
        r.bold = True
        self.rich(cap, caption, size=9)
        cap.add_run(" ")
        self.rich(cap, credit, size=8.5, color=RGBColor(0x80, 0x80, 0x80))
        return self.fig_n

    # ------------------------------------------------------------------- TOC
    def toc_marker(self):
        self._toc_par = self.doc.add_paragraph()

    def build_toc(self, pages):
        anchor = self._toc_par
        n = len(self.headings)
        for i, (level, text) in enumerate(self.headings):
            par = anchor.insert_paragraph_before(style=f"toc {level}")
            if i == 0:
                par._p.append(self._fld_run("begin"))
                r = OxmlElement("w:r")
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = ' TOC \\o "1-2" \\h \\z \\u '
                r.append(it)
                par._p.append(r)
                par._p.append(self._fld_run("separate"))
            par.add_run(f"{text}\t{pages.get(text, '')}")
            if i == n - 1:
                par._p.append(self._fld_run("end"))
        anchor._p.getparent().remove(anchor._p)

    def save(self, path):
        self.doc.save(str(path))


# ======================================================================
# Content
# ======================================================================
def content(s: SOP):
    d = s.doc

    # ---------------------------------------------------------- title page
    t = d.add_paragraph()
    t.paragraph_format.space_before = Pt(30)
    r = t.add_run("Drop Tower Standard Operating Procedure")
    r.font.size, r.bold, r.font.color.rgb = Pt(24), True, NAVY
    s.p("Lansmont Model 23 shock test system, Smash Lab (CB 152A), Brigham Young University",
        size=13, color=GRAY)
    s.p("")
    s.box("Status, 2026-10-29:",
          "DRAFT TEMPLATE, not approved for use. Drop tower use has been halted since 2026-10-19, "
          "when the cable of the 10,000 g single-axis accelerometer broke at its connector "
          "({issue #115|" + L["halt"] + "}; section 17.3). Testing resumes when "
          "[restart condition, for example: this SOP is approved and the corrective action for the "
          "cable failure is signed off by the supervisor].", fill=WARN_FILL)
    s.table(["Document control", ""], [
        ["Document", "Drop tower SOP, [document number]"],
        ["Revision", "0.1, template generated 2026-10-29 from the project repository"],
        ["Equipment", "Lansmont Model 23 (M23) shock test system, serial [number], with the Lansmont "
                      "Test Partner 4 (TP4) data recorder ({PR #28|" + L["pr28"] + "}, "
                      "{issue #27|" + L["issue27"] + "})"],
        ["Location", "CB 152A (Smash Lab)"],
        ["Prepared by", "Marcus Madsen, Jinkwan Han"],
        ["Reviewed by", "[name, role, date]"],
        ["Approved by", "[supervisor name], [date] (signatures in section 19)"],
        ["Next review", "[date, for example one year after approval, or after any incident]"],
    ], [1.5, 5.0], font=10)
    s.box("How to use this template (delete this box before approval):", "", items=[
        "Each topic section has the same four parts: **What this section must cover** (the "
        "requirement from the {SOP request|" + L["request"] + "}), **Procedure**, **How it is "
        "verified**, and **Stop the test if**.",
        "Text in [gray brackets] is a placeholder. Replace it or delete it.",
        "Everything else was drafted from the project's repository records (linked under **Sources** "
        "in each section) and from general drop-test practice. Treat all of it as a draft: check "
        "each statement against the machine, the Lansmont manuals, and the supervisor before approval.",
        "Appendix A maps each required item to the section that covers it, so the reviewers can "
        "check that nothing is missing.",
        "After editing, update the table of contents: right-click it and choose Update Field "
        "(Word desktop), or use References, Update Table (Word for the web).",
    ])

    # ----------------------------------------------------------------- TOC
    c = d.add_paragraph()
    c.paragraph_format.page_break_before = True
    r = c.add_run("Contents")
    r.font.size, r.bold, r.font.color.rgb = Pt(16), True, NAVY
    s.toc_marker()

    # ----------------------------------------------------------- 1 checklists
    s.h1("1. Checklists", page_break=True)
    s.p("Print this section and keep it at the drop tower. The right-hand column gives the section "
        "with the full procedure for each item. The checkboxes can be clicked in Word.")
    s.h2("1.1 Start of session (once per session)")
    s.checklist([
        ("The drop tower is booked for today on the Smash Lab calendar, and any shared day is "
         "coordinated with the other booking.", "4"),
        ("At least [two] authorized operators are present. One is named release controller and "
         "recorded in the log.", "12.1, 18"),
        ("Everyone in the room is wearing eye protection.", "6.2"),
        ("Safety key is out and held by the person setting up. Key interlock check done and "
         "recorded.", "7.1"),
        ("Pre-test inspection done and recorded.", "10"),
        ("Today's test plan is inside the approved operating limits. Any increase in height, mass "
         "or pressure has been reviewed.", "8, 12.3"),
        ("Accelerometers suit the expected peak, are mounted, and their cables are routed with "
         "strain relief. Cable travel checked with a slow raise.", "9.2 to 9.4"),
        ("TP4 settings match the reference screen. Session named after specimen and campaign.", "11"),
        ("Exclusion zone marked and clear. [Guard or shield] in place.", "6.3"),
        ("Test log opened for the session.", "17"),
    ])
    s.h2("1.2 Before every drop")
    s.checklist([
        ("Block and specimen retained. Attachment checked by hand.", "9.1"),
        ("Accelerometers tight. Cables clamped, slack loop clear of the drop block, guide rods, "
         "brakes and absorber over the full travel and rebound.", "9.3, 9.4"),
        ("Drop height, mass and pressure match the test plan and the approved limits.", "8"),
        ("TP4 armed with the right channels, trigger and session name. Camera recording, if used.", "11"),
        ("Nobody inside the exclusion zone. Everyone wearing eye protection.", "6"),
        ("Release controller asks \"Ready?\" and hears \"Ready\" from each person present.", "12.1"),
        ("Release controller calls \"All clear, dropping\" and releases.", "12.1"),
    ])
    s.h2("1.3 After every drop")
    s.checklist([
        ("Drop block is held by the brakes and all motion has stopped before anyone approaches.", "12.2"),
        ("Capture checked in the TP4: impact in the record, no channel at full scale, no flat or "
         "stepping channel.", "11, 15"),
        ("Specimen, sensors, cables and fixture inspected. Anything abnormal recorded.", "15"),
        ("Drop recorded in the test log.", "17"),
    ])
    s.h2("1.4 End of session, or before leaving the machine")
    s.checklist([
        ("Drop block lowered to [rest position]. [Mechanical restraint] in place.", "16.3"),
        ("Air supply closed and vented. Gauge reads 0 psi.", "16.2"),
        ("Controller and machine power off.", "16.3"),
        ("Safety key removed and stored at [location].", "7.1, 16.3"),
        ("Accelerometers back in their cases, in the cabinet marked \"Accelerometers\".", "4"),
        ("Acrylic plates on the team's shelf. Computer workbench and center tables cleared.", "4"),
        ("Test log closed. Incidents reported.", "17"),
    ])

    # ------------------------------------------------- 2 purpose and status
    s.h1("2. Purpose, scope and current status", page_break=True)
    s.label("Purpose")
    s.p("This SOP describes how to set up, run and shut down drop tests on the drop tower in CB 152A "
        "so that nobody is hurt, the machine and sensors are not damaged, and the data can be used.")
    s.label("Scope")
    s.p("It applies to everyone who operates the drop tower or works on it: setup, sensor "
        "installation, testing, troubleshooting and shutdown. At least four research teams use the "
        "tower ({issue #115|" + L["issue115"] + "}). [State whether this SOP covers all teams or "
        "only the tensegrity project, and who coordinates with the other teams.]")
    s.label("Current status")
    s.p("Drop tower use was halted on 2026-10-19, after the cable of the 10,000 g single-axis "
        "accelerometer (channel 5, CH5) broke at its connector ({issue #115|" + L["halt"] + "}, "
        f"Figure {FIGS['cable']} (b)). The cable had been intermittent for an hour on 2026-10-17 before it failed "
        "({CH5 fault analysis|" + L["ch5"] + "}). Use was also halted on 2026-08-04, when a guide-rod locking pin "
        "broke and the tower turned out to run with its pins out of their housing ({issue #92|" + L["pin_halt"]
        + "}). [Restart condition and who approves it.]")

    # --------------------------------------------- 3 definitions and roles
    s.h1("3. Definitions and roles")
    s.label("Definitions")
    s.table(["Term", "Meaning in this SOP"], [
        ["Drop tower", "The Lansmont Model 23 shock test system in CB 152A: frame, guide rods, "
                       "hoist, latch, drop block, brakes, absorber and controller."],
        ["Drop block (carriage, drop mass)", "The block that the hoist raises, the latch holds and releases, "
                                             "and the brakes catch, with everything fastened to it. The "
                                             "specimen sits on it."],
        ["Guide-rod locking pins", f"Two pins that go through cross-holes in the guide rods to hold up the raised "
                                   f"drop block while someone works under it, for example to change the absorber "
                                   f"mat. When not in use they sit in their housing, which is part of the tower's "
                                   f"safety circuit (Figure {FIGS['pins']})."],
        ["Hoist (pulley)", "Raises the drop block to the drop height. [Confirm: chain hoist on the top "
                           "of the frame.]"],
        ["Latch", "Holds the drop block at the drop height until release. The release hook is part of it."],
        ["Brakes", "The anti-rebound brakes that catch the drop block after it bounces off the absorber, "
                   "so it does not strike a second time."],
        ["Absorber (mat, programmer)", "The material the drop block strikes, which shapes the shock pulse: "
                                       "felt, cardboard or polyurethane sheet in this project."],
        ["Bungee cords", "Elastic cords that can be attached to the drop block to pull it down faster than "
                         "free fall. They store energy while the drop block is raised."],
        ["Safety key", f"[Confirm: the key in the System Power OFF/ON/START switch on the TouchTest Shock "
                       f"console (Figure {FIGS['console']}). Describe what it disables.]"],
        ["Release controller", "The one person who controls the release for a drop (section 12.1)."],
        ["Exclusion zone", "The area around the tower that must be clear of people during a drop "
                           "(section 6.3)."],
        ["Secure state", "The state the machine is left in when unattended (section 16.3)."],
        ["DAQ", "Data acquisition system. Here, the Lansmont TP4 recorder and its software."],
        ["ICP (IEPE)", "Accelerometers with built-in electronics, powered by a constant current from "
                       "the DAQ (integrated electronics piezoelectric). ICP is PCB Piezotronics' name "
                       "for it."],
        ["g", "Acceleration in multiples of standard gravity, 9.81 m/s². The TP4 writes it as G."],
    ], [1.6, 4.9])
    s.label("Roles")
    s.table(["Role", "Who", "Responsibilities"], [
        ["Supervisor", "[name, for example Jeffrey Hill]", "Approves this SOP, the operating limits, "
         "changes to either, and restarting after an incident. Receives incident notifications."],
        ["SOP owners", "Marcus Madsen, Jinkwan Han", "Keep this SOP, the test log and the "
         "incident register up to date."],
        ["Operator", "Authorized people (section 18)", "Set up, run and shut down tests by this SOP."],
        ["Release controller", "One operator per session", "Holds the safety key during the drop "
         "sequence, gives the calls, releases the drop block."],
        ["Observer", "[optional or required]", "Watches the exclusion zone and the cables during drops "
         "and calls \"Stop\" if needed."],
    ], [1.4, 1.8, 3.3])

    # ------------------------------------ 4 scheduling, workspace, storage
    s.h1("4. Scheduling, workspace and storage")
    s.p("From the drop tower use protocol in {issue #115|" + L["issue115"] + "} and the CB 152A "
        "workspace notes from 2026-10-13 ({comment|" + L["workspace"] + "}).")
    s.label("Booking the drop tower")
    s.numbered([
        "Get your BYU email added to the {Smash Lab calendar|" + L["calendar"] + "} before you book.",
        "Plan the tests for the day you want.",
        "Book the drop tower for the whole day, not a time slot. You may book several days in a row.",
        "If someone has already booked the date you need, contact that person and agree on times.",
    ])
    s.label("Workspace and storage in CB 152A")
    s.numbered([
        "Store items and work only in the areas marked in Figure 1 (a) and (b).",
        "The large wooden tables in the center of the room may be used during testing. Clear and clean "
        "them as soon as testing is done.",
        "When the scheduled testing is finished, put the whole setup away: accelerometers back in their "
        "cases (Figure 1 (c)) and on the shelf marked \"Accelerometers\" (Figure 1 (d)), acrylic plates "
        "on the team's shelf, and the computer workbench and center tables cleared of the team's items.",
    ])
    s.figure("workspace", FIG / "workspace-and-storage-cb152a-2026-10-13.jpg", 6.2,
             "CB 152A workspace and storage, marked in red. (a) Bench area the team may use. (b) The team's "
             "shelf. (c) Accelerometer case (this one is labeled PCB Piezotronics 350C04, SN 73149). "
             "(d) Cabinet shelf marked \"Accelerometers\".",
             "Photos: Marcus Madsen, {issue #115|" + L["workspace"] + "}, 2026-10-13.")

    # ---------------------------------------------------- 5 equipment
    s.h1("5. Equipment and the prepared setup")
    s.h2("5.1 Drop tower")
    lay = d.add_table(rows=1, cols=2)
    s._widths(lay, [4.85, 1.65])
    left, right = lay.rows[0].cells
    left.width, right.width = Inches(4.85), Inches(1.65)
    s.rich(left.paragraphs[0], "Values from the Lansmont M23 data sheet (October 2025 revision) as "
           "transcribed in the {equipment notes|" + L["m23"] + "}. Confirm each one against the lab's "
           "machine and its manual, and fill in the blanks.")
    s.table(["Item", "Value"], [
        ["Model and serial number", "Lansmont Model 23, serial [number]"],
        ["Controller", "TouchTest Shock II table top console [confirm]"],
        ["Maximum acceleration", "5,000 g"],
        ["Minimum pulse duration", "0.25 ms (half-sine)"],
        ["Maximum velocity change", "24 to 32 ft/s (7.3 to 9.7 m/s)"],
        ["Maximum payload", "80 lb (36 kg)"],
        ["Table size", "9.06 in by 9.06 in (23 cm by 23 cm)"],
        ["Air supply", "Plant air at 90 psi (6.2 bar), through filter-regulators on the wall behind the "
                       "tower. [Regulator setting used in the lab.]"],
        ["Machine power", "200 to 240 VAC three-phase at 4 A or more, or 380 to 480 VAC three-phase. "
                          "[Disconnect location.]"],
        ["Emergency stop", "[Equipped? Is it the round button on the console? See section 14.]"],
        ["Manuals", "[Where the M23 and TP4 manuals are kept. The TP4 Quick Start Guide and User's Guide "
                    "were attached to the GitHub issue that started the drop-test protocol.]"],
    ], [1.45, 3.25], font=9, container=left)
    s.figure("m23", FIG / "lansmont-m23-vendor-photo.jpg", 1.25,
             "Lansmont Model 23: hoist at the top, drop block on the guide rods, brake and air components "
             "at the base. [Replace with a labeled photo of the lab's machine.]",
             "Vendor photo, {M23 data sheet|" + L["m23_vendor"] + "}, October 2025.", container=right)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    s.h2("5.2 Instrumentation")
    s.p(f"Channel use in the 2026 campaigns, from the TP4 settings re-entered on 2026-08-18 (Figure {FIGS['tp4']}) and "
        "the per-campaign records on {PR #86|" + L["pr86"] + "}. The Dytran model and serial number are from "
        "{PR #74|" + L["dytran"] + "}; the CH5 model is read off its case (Figure 1 (c)). Ranges, shock ratings "
        "and calibration dates go in the table in section 9.2.")
    s.table(["Channel", "Sensor", "Location and mounting used", "TP4 full scale", "Sensitivity", "Role"], [
        ["CH2, CH3, CH4", "Dytran 3133A4 tri-axis, SN 11799",
         "Top vertex of the specimen, in the printed key seat, held with wax; cable clamped to a rod",
         "14,492.8 / 14,992.5 / 13,624.0 G", "0.690 / 0.667 / 0.734 mV/G", "Output (\"TOP\")"],
        ["CH5", "Single-axis, 10,000 g class. Case label: PCB 350C04, SN 73149 [confirm]",
         "Base acrylic plate, taped (wax in earlier runs)", "9,442.9 G", "1.059 mV/G",
         "Input and trigger"],
        ["DAQ", "Lansmont TP4 [serial]", "[location of recorder and computer]", "", "", "Records all channels"],
    ], [0.75, 1.3, 1.75, 1.05, 0.95, 0.7], font=8.5)
    s.h2("5.3 Fixture and absorber")
    s.bullets([
        "Specimens sit on an acrylic base plate on the drop block and are tied down to the plate bolts "
        "with cords (Figure 3).",
        "Absorber mats used so far: 4 felt sheets plus 1 cardboard sheet, 1/4 in polyurethane sheet "
        "(McMaster 8514K521), and a 1/2 in polyurethane sheet (McMaster 8514K625), which alone has been the "
        "campaign mat since 2026-08-06 ({print-defects setup|" + L["printdefects"] + "}, "
        "{pre/post grease test|" + L["grease"] + "}).",
        "Bungee cords: attached in the first drops ({issue #36|" + L["issue36_bungee"] + "}), removed "
        "for the later campaigns.",
        "An earlier specimen cage used two acrylic plates on four 18 in threaded rods "
        "({drop-test protocol|" + L["protocol"] + "}).",
    ])
    s.h2("5.4 The correctly prepared setup")
    s.p("[Replace Figure 3 with a photo of the setup approved for this SOP, with the parts labeled. Take "
        "it after the corrective actions in section 17.3 are in place.]")
    s.figure("setup", FIG / "prepared-setup-example-mdt6ja.jpg", 6.0,
             "Example of a prepared setup (2026-08-06): specimen mdt6ja on the acrylic base plate, bottom "
             "vertices tied to the plate bolts with cords, the top-vertex accelerometer cable taped at the "
             "vertex, and the base-plate accelerometer under tape. The checkerboard is the scale "
             "reference for video.",
             "Photo: project IDETC 2026 slide deck, slide 23 ({copy in the repository|"
             + L["setup_photo"] + "}).")
    # ------------------------------------------------------ 6 hazards
    s.h1("6. Hazards, eye protection and personnel clearance")
    s.h2("6.1 Hazards")
    s.table(["Hazard", "Where", "Controlled in"], [
        ["Falling drop block: crushing and pinching", "Under and around the drop block, between drop block, "
         "absorber and base", "7.2, 6.3, 16"],
        ["Stored energy: raised drop block, stretched bungee cords, compressed air", "Hoist, latch, "
         "bungee attachment points, air lines and brakes", "7, 14, 16.2"],
        ["Ejected parts: broken specimens, loose sensors, fixture pieces", "Around the table", "6.2, 6.3, 9"],
        ["Pinch points at the latch, hoist and brakes", "Moving parts of the tower", "7.1"],
        ["Cable snagging and whipping", "Sensor cables between drop block and frame", "9.4"],
        ["Compressed air (90 psi)", "Hoses, fittings, brake cylinders", "10, 16.2"],
        ["Electrical (three-phase machine power)", "Machine and controller", "16.3"],
        ["Noise from impacts", "Room", "[hearing protection: required or optional?]"],
    ], [2.4, 2.8, 1.3])
    s.h2("6.2 Eye protection")
    s.must_cover("Specify required protection for operators and anyone near the test.")
    s.section_block(
        procedure=[
            "Everyone in CB 152A wears safety glasses with side shields marked Z87+ (impact rated to ANSI "
            "Z87.1) whenever [the safety key is in, the system is pressurized, or the drop block is raised].",
            "Prescription glasses count only if they are Z87+ rated. Otherwise wear goggles or "
            "over-glasses over them.",
            "[A face shield is required when: for example testing specimens that can shatter, or "
            "whenever the guard is open.]",
            "Spare safety glasses are kept at [location]. Visitors get a pair before entering.",
        ],
        verify=[
            "The release controller checks that everyone present has eye protection on before each "
            "\"Ready?\" call (checklist 1.2).",
        ],
        stop=[
            "Anyone in the room is not wearing eye protection.",
            "Eye protection is cracked, scratched so that vision is impaired, or missing side shields.",
        ])
    s.h2("6.3 Guarding and personnel clearance")
    s.must_cover("Define the exclusion zone, operator location, and protection from ejected parts or "
                 "broken specimens.")
    s.section_block(
        procedure=[
            "Exclusion zone: [distance, for example 1 m] around the tower, marked with [floor tape or a "
            "barrier]. Nobody enters it from the \"Ready?\" call until the drop block is caught and all "
            "motion has stopped (section 12.2).",
            "Operator location during a drop: [at the controller, location], outside the zone, with a "
            "clear view of the tower and the cables.",
            "Guard: [describe the shield or enclosure and when it must be closed].",
            "Tie specimens to the base plate (Figure 3) and clamp sensor cables so a broken specimen or a "
            "loose sensor stays on the table.",
            "Start the camera with its remote from outside the zone (a remote was bought partly for this, "
            "{issue #91|" + L["issue91"] + "}).",
            "Tell everyone else in the room before each drop or run.",
        ],
        verify=[
            "The release controller looks over the zone before calling \"All clear\".",
            "[Optional: an observer watches the zone during automatic runs.]",
        ],
        stop=[
            "Anyone enters the zone after the \"Ready?\" call.",
            "The guard is open or missing.",
            "Any part leaves the table. Re-assess the zone size and the retention before continuing.",
        ])

    # ---------------------------------------------- 7 safety key and mass
    s.h1("7. Safety key and the raised mass")
    s.h2("7.1 Safety key procedure")
    s.must_cover("Require removal of the safety key before working on the machine. Define how to verify "
                 "that the system is configured correctly so removing the key prevents both the pulley "
                 "from raising and the latch from releasing. Specify when the key may be reinserted.")
    s.section_block(
        procedure=[
            f"Remove the safety key from [the System Power key switch on the console (Figure {FIGS['console']}), "
            "confirm] before any work on the machine: mounting a specimen or sensor, adjusting cables, changing "
            "the absorber mat, inspecting, cleaning or troubleshooting.",
            "The person working on the machine keeps the key [in a pocket or on a lanyard] until the work is "
            "done. Nobody else reinserts it.",
            "Reinsert the key only when everyone is out of the exclusion zone, tools and loose items are off the "
            "machine, both locking pins are back in their housing (section 7.2), checklist 1.2 is complete up to "
            "the \"Ready?\" call, and the person who held the key agrees.",
            "The spare key is kept by [supervisor] at [location].",
        ],
        verify=[
            "At the start of each session, and after any maintenance or wiring change, with the key out and the "
            "drop block resting on [its supports]: press the hoist raise control. The block must not move.",
            "With the key out, operate the release control [describe how to test this safely, for example with "
            "the latch empty]. The latch must not open.",
            "With a locking pin out of its housing, the tower must not raise or release either [confirm the "
            "intended behavior in the Lansmont manual]. In July and August 2026 the tower dropped with its pins "
            "out of the housing because the safety had not been set up properly "
            "({issue #92|" + L["pin_fixed"] + "}).",
            "Record the results in the log.",
        ],
        stop=[
            "The hoist raises or the latch releases with the key out, or with a locking pin out of its housing. "
            "The interlock is not working: tag the console \"Do not operate\" (as on 2026-08-04, Figure "
            f"{FIGS['console']}), put the machine in the secure state, and notify the supervisor.",
            "The key is missing, or a second key is in use.",
        ])
    s.figure("console", FIG / "console-key-switch-do-not-operate-2026-08-04.jpg", 3.4,
             "TouchTest Shock console with the System Power key switch (top right) and the \"Do not operate "
             "(safety non-functional)\" tag used after the second locking pin broke, 2026-08-04.",
             "Photo: Marcus Madsen, {issue #92|" + L["pin_halt"] + "}.")
    s.box("Note:", "Removing the safety key does not hold up a raised drop block. Section 7.2 applies "
                   "whenever anyone reaches under it.", fill=WARN_FILL)
    s.h2("7.2 Supporting the raised mass")
    s.must_cover("Define the mechanical restraint required before accessing beneath it. Removal of the "
                 "safety key does not replace mechanical support of the raised mass.")
    s.section_block(
        procedure=[
            "Never put hands, tools or any part of the body under a raised drop block that is held only by the "
            "latch, the hoist or the brakes.",
            "Lower the block to [its rest position] before working under it whenever possible.",
            f"If it must stay raised (for example to change the absorber mat): remove the safety key, then put "
            f"both guide-rod locking pins through the cross-holes in the guide rods under the block (Figure "
            f"{FIGS['pins']} (a)). [Confirm the cross-hole positions and that the block rests on the pins.]",
            "If bungee cords are attached, [detach or relax them] before working near the block. They store "
            "energy while it is raised.",
            f"When the work is done and everyone is clear, take both pins out and put both back in their housing "
            f"(Figure {FIGS['pins']} (b)). Count them out loud: two pins in the housing before the key goes back "
            f"in.",
            "Use only the approved pins (machined from Klein 601-6 screwdrivers, 3/16 in, "
            "{issue #92|" + L["pin_closed"] + "}). Replace a bent or cracked pin before use.",
        ],
        verify=[
            "A second person checks that both pins are in the guide rods before anyone reaches under the block, "
            "and that both are back in their housing before the key goes in.",
            "[Record pin use in the log.]",
        ],
        stop=[
            "A pin is missing, bent or cracked.",
            "The block moves while the pins are being put in.",
            "The tower can operate with a pin out of its housing (section 7.1).",
        ],
        sources=[
            "A pin left in the guide rod during mat changes snapped when the block dropped, 2026-07-30. A second "
            "pin broke on 2026-08-04, the tower turned out to run with its pins out of their housing, and use was "
            "halted until the safety was set up properly on 2026-08-05 ({issue #92|" + L["issue92"] + "}).",
        ])
    s.figure("pins", FIG / "guide-rod-locking-pins-issue92.jpg", 6.5,
             "Guide-rod locking pins. (a) Cross-hole in a guide rod under the raised drop block, with the air "
             "filter-regulators on the wall behind. (b) Both pins in their housing, the state required before a "
             "drop. (c) The pin that was left in and snapped, 2026-07-30.",
             "Photos: Marcus Madsen, {issue #92|" + L["issue92"] + "}, 2026-07-30 and 2026-08-12.")

    # ----------------------------------------------- 8 operating limits
    s.h1("8. Approved operating limits")
    s.must_cover("Establish allowable mass, drop height, pressure, and test configurations, including who "
                 "approves changes.")
    s.p("The \"Used so far\" column comes from the campaign records on {PR #86|" + L["pr86"] + "}. "
        "The approved limits are for the supervisor to set.")
    s.table(["Parameter", "Approved limit", "Machine maximum (M23 data sheet)", "Used so far in this project"], [
        ["Drop mass (drop block, fixture and specimen)", "[ ]", "80 lb (36 kg) payload", "[record the drop block mass]"],
        ["Drop height", "[ ]", "About 77 in free fall with the bungee cords removed "
         "({Jeffrey Hill|" + L["height77"] + "}) [confirm]", "5, 10, 13, 15, 20, 30 and 60 in"],
        ["Peak table acceleration", "[ ]", "5,000 g", "[ ]"],
        ["Air pressure", "[ ]", "90 psi (6.2 bar) supply", "[ ]"],
        ["Bungee cords", "[allowed? how many?]", "", "Attached in the first drops, removed since"],
        ["Absorber mats", "[approved list]", "", "4 felt + 1 cardboard; 1/4 in and 1/2 in polyurethane"],
        ["Automatic repeat drops", "[maximum drops per run]", "", "About 42 s per drop, up to 500 drops per run"],
        ["Peak reading vs. sensor range", "Below [80 %] of the sensor's range and of the TP4 full scale",
         "", "Some channels reached full scale in 2026 (section 17.3)"],
    ], [1.6, 1.4, 1.6, 1.9], font=9)
    s.label("Who approves changes")
    s.numbered([
        "Operators may run any configuration inside the approved limits.",
        "A new limit, a new absorber, a new fixture or block, or bungee cords need [the supervisor's] "
        "approval, recorded in [the log or a revision of this SOP] before the first drop.",
    ])

    # ------------------------------------------- 9 specimen and sensors
    s.h1("9. Specimen and sensor setup")
    s.h2("9.1 Securing the block")
    s.must_cover("Specify how the block is retained and how its attachment is checked before every drop.")
    s.section_block(
        procedure=[
            "The drop block is held at the top by the release hook, which closes under gravity onto [the post "
            "on the block, confirm]. Before every raise, check that the hook has fallen fully closed and "
            "engaged. Never close it by hand with the block unsupported.",
            "Parts fastened to the block: [describe the base plate and fixture fasteners: size, number, "
            "torque]. Mark each bolt with a paint-pen line across the head and the plate (witness mark).",
            "Tie the specimen's bottom vertices to the plate bolts with cords (Figure 3). [Or the approved "
            "method.]",
            "The absorber mat lies flat and centered under the block. Polyurethane sheets can stick to the "
            "block; dusting them fixed this before ({issue #88|" + L["pu_stick"] + "}).",
        ],
        verify=[
            "Before every drop: the hook is seen to be closed on the block; the plate and fixture do not move "
            "when pushed and twisted by hand; the witness marks line up (checklist 1.2).",
            "[Torque check every N drops or each session.]",
        ],
        stop=[
            "The hook does not close by itself (it stuck open on 2026-07-22, section 14).",
            "Anything fastened to the block moves, a fastener is missing, or a witness mark is broken.",
            "The plate is cracked or crazed.",
        ])
    s.h2("9.2 Using proper shock accelerometers")
    s.must_cover("Verify measurement range, shock-survival rating, and suitability for the expected impact.")
    s.section_block(
        procedure=[
            "Estimate the peak acceleration for the planned test from earlier drops with the same height "
            "and absorber. Write the estimate in the test plan.",
            "Pick a sensor whose measurement range is at least [1.5] times the expected peak and whose "
            "shock-survival rating (from its data sheet) is well above the worst case, including the "
            "sensor coming loose and hitting the table.",
            "Set the TP4 so the expected peak stays below [80 %] of full scale. The TP4 \"Full Scale\" "
            "column is the recorder's input range (10 V) divided by the sensitivity: 10 V / 1.059 mV/G = "
            "9,442.9 G for CH5. It is not the sensor's rated range or its shock survival.",
            "Record each sensor's model, serial number, sensitivity, range, shock survival and "
            "calibration date in the table below.",
        ],
        verify=[
            "A second operator checks the sensor data sheet against the expected peak before any new "
            "configuration.",
            "After each drop, the peak is below [80 %] of full scale (checklist 1.3).",
        ],
        stop=[
            "Any channel reaches full scale (clipping).",
            "The peak exceeds the sensor's measurement range.",
            "A sensor was dropped or struck. Check its sensitivity before using it again.",
        ])
    s.table(["Channel", "Model", "Serial", "Sensitivity", "Range (± g)", "Shock survival (± g)",
             "Calibration due"], [
        ["CH2 (X)", "Dytran 3133A4", "11799", "0.690 mV/G", "[ ]", "[ ]", "[calibrated 2023-04-20; due?]"],
        ["CH3 (Y)", "Dytran 3133A4", "11799", "0.667 mV/G", "[ ]", "[ ]", "[same sensor]"],
        ["CH4 (Z)", "Dytran 3133A4", "11799", "0.734 mV/G", "[ ]", "[ ]", "[same sensor]"],
        ["CH5", "[PCB 350C04, confirm]", "[73149, confirm]", "1.059 mV/G", "[ ]", "[ ]",
         "[2022 calibration sticker; due?]"],
    ], [0.7, 1.3, 0.8, 0.9, 0.85, 1.05, 0.9], font=9)
    s.h2("9.3 Accelerometer installation and handling")
    s.must_cover("Specify mounting method, appropriate mounting torque, connector handling, and protection "
                 "from direct impact.")
    s.section_block(
        procedure=[
            "Mounting method for each location: [stud mount to a tapped hole at the torque on the sensor's "
            "data sheet, for example ___ in-lb with a torque wrench; adhesive mount; or the approved method]. "
            "Bare wax and press fits have let sensors fall off (section 17.3).",
            "Top-vertex sensor: seat it fully in the printed key seat with wax inside the housing, tape over "
            "the housing entrance, and tie its cable to a rod so cable pull cannot drag it out of the seat "
            "({half-seated sensor|" + L["halfseat"] + "}, {taped entrance|" + L["tape_entrance"] + "}).",
            "Handle a sensor by its housing, never by its cable ({PR #67|" + L["handle"] + "}).",
            "Connectors: hand-tighten [10-32 coaxial] connectors. Never pull on the cable to disconnect, "
            "never let a connector carry the weight of the cable, and cap unused connectors.",
            "Place sensors and connectors where nothing can strike them during travel or rebound, and away "
            "from the absorber contact area.",
            "Carry sensors in their cases. At the end of the day, return them to their cases and the "
            "cabinet (Figure 1).",
        ],
        verify=[
            "After mounting: a light tug on the sensor body (not the cable) does not move it.",
            "First drop of the session: every channel shows an impact and returns to baseline.",
        ],
        stop=[
            "A sensor is loose, tilted or out of its seat.",
            "A connector is loose or its strain relief is damaged.",
            "Readings are abnormal (section 13).",
        ])
    s.figure("table", FIG / "carriage-table-base-accelerometer.jpg", 3.9,
             "Drop block during the first drop tests. The red mark shows a base accelerometer next to "
             "the absorber plate. The striped elastic cords are bungee cords.",
             "Photo: {issue #36|" + L["issue36_photo"] + "} ({copy|" + L["table_photo"] + "}).")
    s.h2("9.4 Securing accelerometer cable slack")
    s.must_cover("Define cable routing and strain relief throughout the full travel and rebound to prevent "
                 "snagging, pinching, or pulling on connectors.")
    s.section_block(
        procedure=[
            "Route each cable from the sensor to a strain-relief clamp on the drop block within [100 mm] of "
            "the sensor, then in one loop to a fixed anchor on the frame at [location], then to the TP4.",
            "Strain relief at both ends: the clamp takes any pull before it reaches the connector. Use "
            "[cable clamps or P-clips]. Do not tape over the connector.",
            "Size the loop so it reaches the full drop height plus the rebound plus [margin] without going "
            "tight, and so it never hangs into the guide rods, brakes, latch, hoist or absorber.",
            "Before the first drop of a session, and after any change, raise the drop block slowly to the "
            "drop height while watching the cable along the whole travel.",
            "No sharp bends at the connectors. Minimum bend radius: [from the cable data sheet].",
        ],
        verify=[
            "Slow-raise check at the start of each session (checklist 1.1).",
            "Visual check before every drop (checklist 1.2).",
            "After every drop: no kinks, cuts or flattened sections, and no strain at the connectors.",
            "In the TP4 series table, every capture holds an impact. Missed impacts or baseline steps "
            "point to a cable fault.",
        ],
        stop=[
            "A cable touches a moving part, or goes tight anywhere in the travel.",
            "A cable or connector is damaged.",
            "The signal is intermittent: missing impacts, steps in the baseline, false triggers.",
        ],
        sources=[
            "CH5 cable fault: intermittent for an hour on 2026-10-17, then broken by 2026-10-19 "
            "({analysis|" + L["ch5"] + "}). The recommendation at the time was to reseat or replace the "
            "cable and both connectors and give it strain relief clear of the drop block "
            "({lab actions|" + L["ch5_lab"] + "}).",
            "Sensor dragged out of the key seat by cable pull, fixed by clamping the cable to a rod "
            "({run 1|" + L["drift1"] + "}, {run 2|" + L["drift2"] + "}).",
        ])
    s.figure("cable", FIG / "cable-routing-and-failure.jpg", 5.4,
             "(a) Sensor cables tied along a cage rod so a pull cannot drag the top sensor out of its seat, "
             "2026-07-02. (b) The CH5 (10,000 g single-axis) accelerometer cable after it broke at the "
             "connector, 2026-10-19. Drop tower use was halted after this failure.",
             "Photos: (a) Jinkwan Han, {PR #67|" + L["rod_tie"] + "}; (b) Marcus Madsen, "
             "{issue #115|" + L["halt"] + "}.")

    # -------------------------------------------- 10 pre-test inspection
    s.h1("10. Pre-test inspection")
    s.must_cover("Check fasteners, fixtures, guides, lifting and release components, hoses, fittings, "
                 "cables, and sensors for damage or looseness.")
    s.p("Do this inspection with the safety key out and the drop block at rest, at the start of each session "
        "and after any incident. Initial each line in the log.")
    s.table(["Done", "Item", "Check", "Past problem"], [
        ["", "Fasteners", "Block, plate and fixture bolts tight; witness marks line up", ""],
        ["", "Fixture and acrylic plates", "No cracks, crazing or chips", ""],
        ["", "Guide rods and bearings", "Clean, lubricated per [the manual], no scoring; drop block moves "
         "freely", "In early August the block reached only 79 to 86 % of free-fall speed; the rods were "
         "cleaned and greased on 2026-08-10 ({record|" + L["grease"] + "}, {analysis|" + L["abc123"] + "})"],
        ["", "Guide-rod locking pins", "Both in their housing; not bent or cracked", "Pins broke on 2026-07-30 "
         "and 2026-08-04 ({issue #92|" + L["issue92"] + "})"],
        ["", "Hoist (pulley) and its chain", "No damage; [check per manual]", ""],
        ["", "Latch and release hook", "Hook falls closed by itself and engages fully; release works",
         "Hook stuck open after more than 1,500 drops, 2026-07-22 ({fixed by lubrication|"
         + L["hook_fixed"] + "})"],
        ["", "Brakes", "[check per manual]", ""],
        ["", "Air hoses and fittings", "No hissing or cracks; hoses secured; regulator at [ ] psi", ""],
        ["", "Absorber mat", "Right mat for the plan; flat; not worn or compacted past [limit]",
         "Felt compacted with use; polyurethane stuck to the block ({issue #88|" + L["pu_stick"] + "})"],
        ["", "Bungee cords (if used)", "No fraying; right number and attachment", ""],
        ["", "Sensor cables and connectors", "No kinks, cuts or loose connectors; strain relief in place",
         "CH5 cable broke, 2026-10-19"],
        ["", "Sensors", "Mounted firmly; no visible damage", "Sensors fell off or came loose five times in June and July 2026 (section 17.3)"],
        ["", "Safety key and pin interlock", "Check in section 7.1 done", "Tower ran with pins out of "
         "their housing until 2026-08-05"],
        ["", "Emergency stop", "[test per manual, if equipped]", ""],
    ], [0.5, 1.35, 2.35, 2.3], font=9, checkbox_col=0)
    s.label("How it is verified")
    s.bullets(["Each line initialed in the log before the first drop of the session."])
    s.label("Stop the test if")
    s.bullets(["Any line fails. Fix it, or put the machine in the secure state and tell the supervisor."])

    # ------------------------------------------------ 11 DAQ readiness
    s.h1("11. DAQ readiness")
    s.must_cover("Verify sensor connections, excitation, input ranges, triggering, and recording before "
                 "release.")
    s.section_block(
        procedure=[
            "Connections: each sensor cable goes to the TP4 channel in table 5.2, connectors hand tight.",
            f"Excitation: ICP on for every channel with an ICP sensor (CH2 to CH5 in Figure {FIGS['tp4']}). [Check the "
            "sensor bias or fault indicator, if the TP4 shows one.]",
            "Sensitivities come from each sensor's calibration certificate, not a default value (defaults "
            "were typed in during the first tests in June 2026, {PR #74|" + L["sens_default"] + "}).",
            "After any sensor is disconnected and reconnected, re-enable its channel and check that it is "
            "active (a session's data were lost on 2026-07-29, {PR #86|" + L["reenable"] + "}).",
            "Turn off channels with no sensor attached. A channel over its range latched the TP4 and stopped a "
            "500-drop run at drop 256 on 2026-07-15 ({PR #82|" + L["overload"] + "}).",
            "Input ranges and sensitivities match table 9.2 and the calibration sheets. Compare the Recording "
            f"Setup screen with the reference (Figure {FIGS['tp4']}) and photograph it again after any change.",
            "Trigger: channel [CH5], level [150 G], pre-trigger [2 %], record time [100 ms], sample rate "
            "[1.25 MHz]. Trigger levels from 150 G to 1,000 G have been used. Set the level above the noise from "
            "raising the block and below the smallest real impact: at 500 G, 5 in drops did not trigger.",
            "Recording: name the TP4 session after the specimen and campaign (for example RW5F61_100drops). "
            "Check that there is disk space.",
            "Camera (optional): recording, framed so the specimen and the release point are both in view.",
        ],
        verify=[
            "After the first drop: an impact is in the record, peaks are near the reference values for the "
            "configuration, and no channel is flat, clipped or stepping. Example from 2026-10-17: CH4 peak "
            "at least 150 G; CH5 pulse about 3 to 4 ms long with a velocity change of about 205 to 225 "
            "in/s ({source|" + L["ch5_lab"] + "}).",
        ],
        stop=[
            "Missed triggers, or captures with no impact.",
            "A channel is clipped, flat or stepping.",
            "Settings differ from the reference. On 2026-08-18 the TP4 settings were reset and had to be "
            "re-entered ({check|" + L["calcheck"] + "}).",
        ])
    s.figure("tp4", FIG / "tp4-recording-setup-2026-08-18.jpg", 6.3,
             "TP4 Recording Setup and Analog Channels screen as re-entered on 2026-08-18: 100 ms record at "
             "1.25 MHz, 2 % pre-trigger, CH2 to CH5 active with ICP on, trigger on CH5 at 150 G.",
             "Photo: {calibration-check record|" + L["tp4_photo"] + "}, PR #86.")

    # ------------------------------------------------- 12 running a drop
    s.h1("12. Running a drop")
    s.h2("12.1 Pre-drop checklist and communication")
    s.must_cover("Assign one person control of release and require explicit readiness confirmation and an "
                 "\"all clear.\"")
    s.section_block(
        procedure=[
            "At the start of the session, name one release controller and record the name in the log. Only "
            "that person inserts the safety key, raises the drop block and releases it. A handover is said "
            "out loud and logged.",
            "The release controller completes checklist 1.2 items 1 to 5.",
            "The release controller asks \"Ready?\". Each person present answers \"Ready\". The DAQ "
            "operator answers \"Recording armed\" and the camera operator \"Camera rolling\".",
            "The release controller looks over the exclusion zone, calls \"All clear, dropping\" and "
            "releases within [10 s]. If anything changes before the release, the call is void and starts "
            "again at step 3.",
            "Anyone may call \"Stop\" at any time. The release controller does not release after a "
            "\"Stop\".",
            "Automatic repeat runs (about 40 s per drop): [define how the calls work, for example one call "
            "at the start of the run, the release controller stays at the controller for the whole run, "
            "and anyone entering the zone stops the run].",
        ],
        verify=["The log names the release controller for each session and each handover."],
        stop=[
            "Someone does not answer \"Ready\".",
            "Anyone enters the zone.",
            "Anyone calls \"Stop\".",
        ])
    s.h2("12.2 Rebound and secondary impacts")
    s.must_cover("Describe how these are controlled and when it is safe to approach.")
    s.p("In two 60 in drops onto five felt sheets filmed at 960 frames per second, the drop block bounced back "
        "at 0.35 to 0.43 times its impact speed, and the anti-rebound brakes stopped it 86 to 89 ms after "
        "impact, 130 to 150 mm above the absorber, with no second impact "
        f"(Figure {FIGS['impact']}; " + "{analysis|" + L["felts60"] + "}).")
    s.section_block(
        procedure=[
            "Keep the anti-rebound brakes [on, with air at ___ psi] for every drop.",
            "Approach only when the brakes hold the drop block, the specimen and cables have stopped moving, "
            "and [the controller shows ___]. Wait at least [5 s] after impact.",
            "If the brakes do not catch and the drop block strikes again, stop and inspect before the next "
            "drop.",
        ],
        verify=["One impact per capture in the TP4 record; the brake catch shows in video or data."],
        stop=[
            "A second impact.",
            "The brakes do not catch, or the drop block creeps down after the catch.",
        ])
    s.figure("impact", FIG / "impact-sequence-60in-9GMQYQ.jpg", 6.5,
             "Frames from a 60 in drop filmed at 960 frames per second: entry, contact, turnaround, rebound, "
             "brake catch at 86.5 ms, and hold.",
             "Figure: {60 in, 5 felt video analysis|" + L["montage"] + "}, PR #86.")
    s.h2("12.3 Increasing test severity")
    s.must_cover("Require inspection and review of the previous test before increasing height, mass, or "
                 "pressure.")
    s.section_block(
        procedure=[
            "Increase severity in steps no larger than [for example 25 % of the drop height, or one "
            "absorber layer].",
            "Before each step up: inspect after the last drop at the current level (section 15), and review "
            "its data: peaks below [80 %] of sensor range and TP4 full scale, one impact, normal brake "
            "catch.",
            "Record the review in the log with the initials of [two people].",
            "A step beyond the approved limits needs the supervisor's approval first (section 8).",
        ],
        verify=["A signed review in the log before each step up."],
        stop=["The review is not done, or the previous drop was abnormal."])

    # ---------------------------------------------------- 13 stop work
    s.h1("13. Stop-work conditions")
    s.must_cover("Include loose components, damaged cables, leaks, unexpected motion, abnormal readings, "
                 "and anyone entering the exclusion zone.")
    s.p("Anyone present may call \"Stop\". After a stop: do not release, end any automatic run [how], put "
        "the machine in the secure state (section 16.3) before investigating, and record the stop in the "
        "log. Events in section 17.2 also need the supervisor's approval to restart.")
    s.table(["Condition", "Examples", "Before restarting"], [
        ["Loose component", "Fastener, fixture, plate or sensor moves", "Fix and re-inspect (section 10)"],
        ["Damaged cable or connector", "Cut, kink, crushed jacket, strained connector",
         "Replace; slow-raise check (9.4)"],
        ["Leak", "Hissing, pressure falling", "Vent (16.2), fix, leak check"],
        ["Unexpected motion", "Drop block creeps, latch will not close, hoist moves without a command",
         "Secure state; supervisor (17.2)"],
        ["Abnormal readings", "Missing impacts, clipping, baseline steps, peaks far from reference",
         "Check sensors, cables and settings (9, 11)"],
        ["Someone in the exclusion zone", "During the call, the drop or the rebound", "Restart the call (12.1)"],
        ["No eye protection", "Anyone in the room", "Glasses on (6.2)"],
        ["Interlock failure", "Hoist or latch works with the key out", "Tag out; supervisor (7.1)"],
        ["Noise, smell or smoke", "From the hoist, controller or wiring", "Power off; supervisor"],
        ["[Add]", "", ""],
    ], [1.6, 2.7, 2.2], font=9)

    # ------------------------------------------ 14 failed release / e-stop
    s.h1("14. Failed release, interrupted test and emergency stop")
    s.must_cover("Define how to secure and unload the system before troubleshooting. Explain what the "
                 "emergency stop does, if equipped, and what hazards remain afterward.")
    s.section_block(
        procedure=[
            "If the drop block does not release: do not reach under it, and do not keep retrying. Remove the "
            "safety key.",
            "Unload the latch: lower the drop block with the hoist [describe] onto [its rest position]. If it "
            "cannot be lowered, install the mechanical restraint (section 7.2) before anyone works near it.",
            "Vent the air (section 16.2) and switch off the power (section 16.3) before troubleshooting the "
            "latch, hoist or release.",
            "Interrupted test (power loss, air loss, DAQ crash, someone in the zone): treat the drop block as "
            "raised and latched until checked, and follow steps 1 to 3.",
            "Release hook that will not fall closed: follow the {troubleshooting note|" + L["hook"] + "} "
            "(it wrongly calls the tower a custom build), with power and air off and the drop block "
            "supported. On 2026-07-22 a second lubrication fixed it ({PR #86|" + L["hook_fixed"] + "}).",
        ],
        verify=["The secure state is checked (section 16.3) before troubleshooting starts."],
        stop=["Any failed release or interrupted test. Restart needs the supervisor's approval (17.2)."])
    s.label("Emergency stop")
    s.table(["Question", "Answer"], [
        ["Is the machine equipped with one? Where is it?", f"[Is it the round button at the top left of the "
                                                            f"console in Figure {FIGS['console']}?]"],
        ["What it does", "[for example: cuts power to the hoist motor and controller]"],
        ["What it does not do", "[for example: it does not lower the drop block. A raised drop block stays "
                                "raised and can still fall. Air stays in the lines and brakes. Bungee cords "
                                "stay stretched.]"],
        ["Hazards left after an emergency stop", "[raised mass, stretched bungee cords, compressed air, "
                                                 "broken specimen pieces, others]"],
        ["How to reset it", "[ ]"],
        ["How often it is tested", "[ ]"],
    ], [2.3, 4.2], font=9.5)

    # --------------------------------------------- 15 post-test inspection
    s.h1("15. Post-test inspection")
    s.must_cover("Define what must be inspected after each drop and the conditions that must be met before "
                 "continuing.")
    s.label("After every drop")
    s.table(["Item", "Condition to continue"], [
        ["Specimen", "Still in position on the plate; tie-downs intact; damage recorded"],
        ["Sensors", "Still seated and flush; not moved"],
        ["Cables", "Intact, clamped, still clear of moving parts"],
        ["Fixture and block", "No movement, no cracks"],
        ["Absorber", "In place, not shifted"],
        ["Data", "Impact in the record; no clipping; baseline returns; peaks in the expected range"],
    ], [1.6, 4.9])
    s.label("During automatic runs")
    s.bullets(["Check the TP4 series table every [N] drops, and stop the run if a capture fails the "
               "conditions above."])
    s.label("Every [N] drops, and at the end of the session")
    s.bullets(["Repeat the section 10 checks on the guide rods, latch, hoist, brakes and hoses.",
               "Check absorber wear and replace it at [limit]."])
    s.label("Stop the test if")
    s.bullets(["Any condition above is not met (section 13)."])

    # ----------------------------------------------- 16 leaving the machine
    s.h1("16. Leaving the machine")
    s.h2("16.1 Leaving the machine during operation")
    s.must_cover("Define required operator attendance and the steps required before stepping away.")
    s.section_block(
        procedure=[
            "An authorized operator stays in CB 152A, in sight of the tower, whenever the safety key is in, "
            "the system is pressurized or the drop block is raised. This includes automatic repeat runs.",
            "Before stepping away for any length of time: stop the run, lower the drop block to [its rest "
            "position], and take the safety key.",
            "Away for more than [10 min]: leave the machine in the secure state (section 16.3).",
            "Never leave a drop block held up by the latch alone.",
            "Hand over to another authorized operator in person, and say out loud who is now the release "
            "controller.",
        ],
        verify=["Breaks and handovers are recorded in the log."],
        stop=["No authorized operator can stay with the machine."])
    s.h2("16.2 Leaving the system pressurized")
    s.must_cover("Define when depressurization is required and how residual pressure is checked.")
    s.section_block(
        procedure=[
            "Depressurize at the end of each session, before leaving the machine unattended, before work on "
            "any air component (hoses, fittings, brakes, release), and after an emergency stop or a leak.",
            f"Close the supply valve at [location] and vent through [valve]. Watch the gauge at [location; "
            f"the filter-regulators are on the wall behind the tower, Figure {FIGS['pins']} (a)] fall to zero.",
            "Check for residual pressure: the gauge reads 0 psi after [time], and [cycling the brake or "
            "release valve with the key out] releases no air.",
            "The system may stay pressurized only while an authorized operator is present.",
        ],
        verify=["The end-of-session gauge reading is recorded in the log."],
        stop=["The gauge does not fall to zero, or the pressure rises again after venting (leaking valve)."])
    s.h2("16.3 Leaving the system in a secure state")
    s.must_cover("Define the required position of the drop mass, mechanical restraints, pressure state, "
                 "power state, and safety key location.")
    s.table(["Done", "Item", "Required state"], [
        ["", "Drop mass (drop block)", "Lowered to [rest position]. Never left raised."],
        ["", "Guide-rod locking pins", "Both in their housing, counted"],
        ["", "Bungee cords", "[detached or relaxed]"],
        ["", "Air", "Supply closed and vented; gauge at 0 psi"],
        ["", "Power", "Controller off; machine [disconnect] off"],
        ["", "Safety key", "Removed and stored at [location]. Never left in the controller."],
        ["", "Sensors", "Removed from the specimen, in their cases, in the cabinet (Figure 1)"],
        ["", "Workspace", "Cleared (section 4)"],
    ], [0.5, 1.8, 4.2], font=9.5, checkbox_col=0)
    s.label("How it is verified")
    s.bullets(["The last person to leave initials checklist 1.4 in the log."])

    # ---------------------------------------------------- 17 logs
    s.h1("17. Test and incident log")
    s.must_cover("Maintain a log of test conditions and any anomalies, errors, equipment damage, near misses, "
                 "or safety incidents. Record the date, operators, description, corrective action, and "
                 "approval to resume testing when required. Define which events require immediate "
                 "notification of the supervisor.")
    s.h2("17.1 What to record")
    s.bullets([
        "The log is kept at [paper binder at the tower and/or file location]. Session data and campaign "
        "notes have also been posted on {PR #86|" + L["pr86"] + "}. [Say which one is the official log.]",
        "Every session: date, operators, release controller, specimen IDs, configuration (height, mass, "
        "absorber, bungee cords, pressure), TP4 session name, settings photo if changed, sensors and serial "
        "numbers, number of drops, start and end times, interlock check, inspections, anomalies.",
        "Every anomaly, error, damage, near miss or safety incident: date, operators, description, immediate "
        "action, corrective action, and approval to resume (name and date). Use the form in Appendix C.",
    ])
    s.h2("17.2 Events that need immediate supervisor notification")
    s.p("Notify [supervisor name, phone] at once, and do not resume testing until the supervisor approves "
        "it in the log, for:")
    s.bullets([
        "Any injury, however small.",
        "Any near miss: someone in the exclusion zone during a drop, or under a raised drop block without the "
        "restraint.",
        "Damage to the tower (latch, pins, guide rods, brakes, hoist, air system) or to a sensor or cable.",
        "A failed release, an unexpected drop, or a drop block that moves without a command.",
        "A failed safety key interlock check.",
        "An air leak that tightening a fitting does not fix.",
        "A part thrown outside the exclusion zone.",
        "[Add or remove events.]",
    ])
    s.h2("17.3 Previous incidents and preventive steps")
    s.p("Each previous incident is matched to a preventive step in this SOP. Dates are when the incident was "
        "reported. [Review each line, add any incident not listed, and confirm the preventive step.]")
    s.table(["Date", "What happened", "Preventive step", "Section"], [
        ["2026-05-26 ({issue #36|" + L["liftoff"] + "})",
         "With bungee cords pulling the drop block faster than free fall, the specimen lifted off the base "
         "and landed out of line. The cage top plate could tilt about 25\u00b0.",
         "Tie specimens to the base plate. Bungee cords only in approved configurations.", "5.3, 8, 9.1"],
        ["June 2026 ({PR #74|" + L["sens_default"] + "})",
         "Default sensitivities typed into the TP4 instead of certificate values; a channel saturated; the "
         "TP4 captured while the block was raised; 5 in drops did not trigger.",
         "Sensitivities from certificates; trigger level set between hoist noise and the smallest impact.", "11"],
        ["2026-06-23 ({PR #67|" + L["vertex_fell"] + "})",
         "A vertex accelerometer that was not fully secured fell off on the drop.",
         "Tug test after mounting; check before every drop.", "9.3, 1.2"],
        ["2026-06-29 ({record|" + L["keymount"] + "})",
         "Top-vertex accelerometer fell out of the key seat; the press fit alone was not enough.",
         "Wax inside the key-seat housing ({follow-up|" + L["keywax"] + "}).", "9.3"],
        ["2026-07-02 ({PR #67|" + L["halfseat"] + "})",
         "Tri-axis accelerometer, seated only halfway, fell out at drop 26.",
         "Housing deepened to 6.1 mm; cable tied to a rod so a pull cannot drag the sensor out; it then stayed "
         "on for 50 drops ({run 2|" + L["drift2"] + "}).", "9.3, 9.4"],
        ["2026-07-03 ({PR #67|" + L["ch5_fell"] + "})",
         "CH5 base-plate accelerometer, held with wax, fell off mid-run and caused false triggers.",
         "Approved mounting method (CH5 taped down from 2026-07-06); stop if a sensor is loose.", "9.3, 13"],
        ["2026-07-06 ({PR #35|" + L["rotate"] + "})",
         "An oversized key-seat pocket let the sensor rotate free despite the wax.",
         "Tape over the housing entrance ({2026-07-08|" + L["tape_entrance"] + "}).", "9.3"],
        ["2026-07-13 and 2026-07-15 ({PR #82|" + L["overload"] + "})",
         "Low-range channels over full scale at 10 in; one latched the TP4 and stopped a 500-drop run at "
         "drop 256.",
         "Choose sensors and ranges for the expected peak; turn off unused channels.", "9.2, 11"],
        ["2026-07-22 ({PR #86|" + L["hook_report"] + "})",
         "Release hook stuck open after more than 1,500 drops and did not re-engage the block. WD-40 did not "
         "fix it; a second lubrication did.",
         "Hook check before every raise; never close it by hand with the block unsupported.", "9.1, 10, 14"],
        ["2026-07-29 ({PR #86|" + L["reenable"] + "})",
         "A session's data were lost: sensors were not re-enabled after being disconnected and reconnected.",
         "Re-enable and check channels after any reconnection.", "11"],
        ["2026-07-30 ({issue #92|" + L["issue92"] + "})",
         "A guide-rod locking pin was left in during mat changes and snapped when the block dropped.",
         "Pins counted back into their housing before the key goes in; two-person check.", "7.1, 7.2"],
        ["2026-08-04 ({issue #92|" + L["pin_halt"] + "})",
         "A second pin broke. The tower ran with its pins out of their housing because the safety was not set "
         "up properly. Console tagged \"Do not operate\" and use halted until 2026-08-05.",
         "Interlock check (key and pins) at the start of every session.", "7.1, 10"],
        ["2026-08-18 ({PR #86|" + L["tp4_cleared"] + "})",
         "TP4 settings were cleared and had to be re-entered.",
         "Compare settings with the reference screen every session.", "11"],
        ["2026-10-17 to 2026-10-19 ({analysis|" + L["ch5"] + "})",
         "CH5 cable intermittent for an hour, then broke at the connector. Drop tower use halted.",
         "Cable routing with strain relief at both ends; slow-raise check; cable inspection after every drop; "
         "stop on missing impacts.", "9.4, 13, 15"],
        ["[date]", "[Add any incident not listed.]", "[ ]", "[ ]"],
    ], [1.2, 2.3, 2.25, 0.75], font=8.5)

    # ------------------------------------------------------ 18 training
    s.h1("18. Training and authorization")
    s.must_cover("Define who may operate the system and who approves the SOP and subsequent modifications.")
    s.numbered([
        "Authorized operators have: [completed the required BYU lab safety training (name it)], read this SOP "
        "and signed the record below, been trained on the drop tower by [the supervisor or a named trainer], "
        "and run [N] sessions under supervision.",
        "Videos: {training walkthrough|" + L["video"] + "} (Jeffrey Hill), {automatic drop setup|"
        + L["video_auto"] + "}, {TP4 databases|" + L["video_tp4db"] + "}.",
        "[The supervisor] approves this SOP and every later change. Changes are listed in section 19 and "
        "announced to all operators [and to the other teams using the tower].",
        "Operators re-read the SOP and re-sign [every year, and after every revision].",
    ])
    s.table(["Name", "Trained by", "Date", "Supervised sessions", "Authorized by", "Date"],
            [["", "", "", "", "", ""] for _ in range(5)], [1.4, 1.2, 0.8, 1.1, 1.2, 0.8], font=9.5)

    # ---------------------------------------------- 19 approval, revisions
    s.h1("19. Approval and revision history")
    s.table(["Role", "Name", "Signature", "Date"], [
        ["Supervisor", "[ ]", "", ""],
        ["SOP owner", "Marcus Madsen", "", ""],
        ["SOP owner", "Jinkwan Han", "", ""],
        ["[Lab or facility manager]", "[ ]", "", ""],
    ], [1.8, 1.9, 1.8, 1.0], font=10)
    s.table(["Revision", "Date", "Description", "By", "Approved"], [
        ["0.1", "2026-10-29", "Template drafted from the repository records ({issue #115|" + L["request"] + "})",
         "Claude Code, for M. Madsen and J. Han", "Not approved"],
        ["", "", "", "", ""],
        ["", "", "", "", ""],
    ], [0.8, 0.9, 2.6, 1.3, 0.9], font=9.5)

    # ---------------------------------------------------- appendices
    s.h1("Appendix A. Requirement coverage", page_break=True)
    s.p("Each item from the {SOP request|" + L["request"] + "} and the section that covers it.")
    s.table(["Required item", "Section"], [
        ["Secure accelerometer slack", "9.4"],
        ["Safety key procedure", "7.1"],
        ["Eye protection", "6.2"],
        ["Leaving the machine during operation", "16.1"],
        ["Leaving the system pressurized", "16.2"],
        ["Leaving the system in a secure state", "16.3, checklist 1.4"],
        ["Securing the block", "9.1"],
        ["Using proper shock accelerometers", "9.2"],
        ["Accelerometer installation and handling", "9.3"],
        ["Supporting the raised mass", "7.2"],
        ["Pre-test inspection", "10"],
        ["Approved operating limits", "8"],
        ["Guarding and personnel clearance", "6.3"],
        ["Rebound and secondary impacts", "12.2"],
        ["Pre-drop checklist and communication", "1.2, 12.1"],
        ["DAQ readiness", "11"],
        ["Increasing test severity", "12.3"],
        ["Stop-work conditions", "13"],
        ["Failed release or interrupted test, emergency stop", "14"],
        ["Post-test inspection", "15"],
        ["Test and incident log, supervisor notification", "17"],
        ["Training and authorization, SOP approval", "18, 19"],
        ["Photo of the correctly prepared setup", "5.4 (Figure 3)"],
        ["Short checklist before every drop", "1.2"],
        ["A preventive step for each previous incident", "17.3"],
    ], [5.0, 1.5], font=9.5)

    s.h1("Appendix B. Session test log")
    s.table(["Session", ""], [
        ["Date", ""], ["Operators", ""], ["Release controller (and handovers)", ""],
        ["Specimen IDs", ""], ["Configuration: height, mass, absorber, bungee cords, pressure", ""],
        ["TP4 session name", ""], ["Sensors and serial numbers", ""],
        ["Interlock check (7.1) and pre-test inspection (10)", ""],
        ["Start and end times", ""], ["End-of-session gauge reading and secure state (16)", ""],
    ], [2.6, 3.9], font=9.5)
    s.table(["Drop or TP4 signal", "Time", "Height", "Notes and anomalies", "Initials"],
            [["", "", "", "", ""] for _ in range(14)], [1.2, 0.8, 0.8, 3.0, 0.7], font=9.5)

    s.h1("Appendix C. Incident report")
    s.table(["Field", "Entry"], [
        ["Date and time", ""], ["Operators present", ""],
        ["Type (anomaly, error, damage, near miss, safety incident)", ""],
        ["What happened", ""], ["Immediate action taken", ""],
        ["Supervisor notified (name, time)", ""], ["Cause", ""],
        ["Corrective action", ""], ["Preventive step added to this SOP (section)", ""],
        ["Approval to resume testing (name, date)", ""],
    ], [2.6, 3.9], font=9.5)

    s.h1("Appendix D. Source records")
    s.bullets([
        "Drop tower use protocol and CB 152A workspace notes: {issue #115|" + L["issue115"] + "}.",
        "Drop-test protocol and troubleshooting: {drop-test-protocol.md|" + L["protocol"] + "}, "
        "{drop-test-hook-troubleshooting.md|" + L["hook"] + "}.",
        "Lansmont M23 notes and data sheets: {equipment/lansmont-m23|" + L["m23"] + "}, "
        "{M23_Data_Sheet_official.pdf|" + L["m23_sheet"] + "}.",
        "Campaign records and analyses (per-run READMEs, incidents, settings): {PR #86|" + L["pr86"] + "}.",
        "TP4 settings check: {drop-test-calibration-check-analysis.md|" + L["calcheck"] + "}.",
        "Rebound and brake catch: {drop-test-60in-5felts-analysis.md|" + L["felts60"] + "}.",
        "CH5 cable fault: {ch5-fault-and-replicates.md|" + L["ch5"] + "}.",
        "Photo provenance for Figure 3: {figures/photos/overview/README.md|" + L["photo_readme"] + "}.",
        "This template's source script and figures: docs/drop-tower-sop/ and "
        "scripts/build_drop_tower_sop.py in this repository.",
    ])


# ======================================================================
def build(pages=None):
    s = SOP()
    content(s)
    s.build_toc(pages or {})
    s.save(OUT)
    return s


def check_text(path):
    """Fail on en or em dashes anywhere in the document text (repo style rule)."""
    import zipfile

    with zipfile.ZipFile(path) as z:
        xml = "".join(z.read(n).decode("utf8") for n in z.namelist() if n.endswith(".xml"))
    bad = [ch for ch in ("\u2013", "\u2014") if ch in xml]
    if bad:
        sys.exit(f"style check failed: found {bad!r} in {path}")


def render(s):
    """Convert to PDF with LibreOffice, read heading pages, rebuild the TOC with them."""
    from pypdf import PdfReader

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("--render needs LibreOffice (soffice) on PATH")
    tmp = Path(tempfile.mkdtemp())

    def to_pdf(src):
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(src)],
                       check=True, capture_output=True)
        return tmp / (src.stem + ".pdf")

    def norm(x):
        return re.sub(r"\s+", " ", x).strip()

    pdf = to_pdf(OUT)
    texts = [norm(pg.extract_text() or "") for pg in PdfReader(str(pdf)).pages]
    first_body = next(i for i, t in enumerate(texts) if "1. Checklists Print this section" in t
                      or ("1. Checklists" in t and "Contents" not in t))
    pages = {}
    start = first_body
    for _, text in s.headings:
        for i in range(start, len(texts)):
            if norm(text) in texts[i]:
                pages[text] = str(i + 1)
                start = i
                break
    build(pages)
    pdf = to_pdf(OUT)
    shutil.copy(pdf, OUT_DIR / "drop-tower-sop-template-preview.pdf")
    missing = [t for _, t in s.headings if t not in pages]
    print(f"TOC pages filled for {len(pages)}/{len(s.headings)} headings; missing: {missing}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--render", action="store_true", help="fill TOC page numbers and write a PDF preview")
    args = ap.parse_args()
    sop = build()
    if args.render:
        render(sop)
    check_text(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")
