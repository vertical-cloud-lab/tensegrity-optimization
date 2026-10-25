# Journal Manuscript Template

Lorem-ipsum LaTeX scaffold for the journal manuscript that will report the
results of the BYU MRG project on multi-material 3D-printed tensegrity
structures for energy absorption.

> **Status:** template only -- no technical content yet.
> See repository issue *"Manuscript venues and template."*

## Primary target venue: ASME Journal of Mechanical Design (JMD)

- Companion site: <https://asmejmd.org/>
- Submission instructions: <https://asmejmd.org/resources-2/submission-instructions/>
- ASME Author Templates landing page: <https://www.asme.org/publications-submissions/proceedings/author-guidelines/elements-of-a-paper/author-templates>
- Submission portal: <https://journaltool.asme.org>

### Article categories and length limits

| Category                  | Recommended length |
|---------------------------|--------------------|
| Research Paper            | up to 9,000 words (≈ 9 journal pages); FAQ allows up to ~12,000 words with overlength charges |
| Technical Brief           | ~4,000 words       |
| Design Innovation Paper   | ~7,000 words       |
| Review Article            | by prior arrangement with the editor |

### Required elements (per JMD submission instructions)

1. **Title** -- concise, in upper- and lower-case; spell out acronyms on first
   use.
2. **Author list** with affiliations and a designated corresponding author.
3. **Abstract** -- 150--200 words, Latin characters only (no math/special
   symbols), structured as background, approach, results, conclusions.
4. **Keywords** -- multiple relevant terms.
5. **Body** -- typical IMRaD structure (Introduction, Methods, Results,
   Discussion, Conclusions); section headings at the author's discretion.
6. **Acknowledgments**, **Funding Data** (with grant numbers), and
   **Conflict of Interest** statement.
7. **References** -- ASME numeric style.
8. **Tables and Figures** -- numbered, captioned, cited in order.

### LaTeX template

ASME points authors to the third-party `asmejour` LaTeX class (by John H.
Lienhard, IV; published with ASME's permission) for journal manuscripts:

- CTAN: <https://ctan.org/pkg/asmejour>
- Zip:  <https://mirrors.ctan.org/macros/latex/contrib/asmejour.zip>
- Documentation/example: `asmejour-template.pdf` inside the package.

The class is included in modern TeX Live and is auto-installed on demand by
MiKTeX, so we do **not** vendor `asmejour.cls` / `asmejour.bst` in this repo.
The template uses the `[lineno,singlecolumn,nocopyright,upint,varvw,hyphenate]`
class options for a single-column, line-numbered draft suitable for review and
co-author markup; drop `singlecolumn` (and eventually `nocopyright`) for the
two-column ASME final layout. See the comments at the top of
`manuscript-body.tex` and `asmejour-template.pdf` for the full list of
supported options.

### Two builds (todonotes toggle)

The body of the manuscript lives in `manuscript-body.tex` and is included
by two thin wrapper files that flip a single flag:

| Wrapper                | `\TODOOPTS`  | Use case                                     | Output                  |
|------------------------|--------------|----------------------------------------------|-------------------------|
| `manuscript.tex`       | `disable`    | Reader-friendly clean PDF (todonotes hidden) | `manuscript.pdf`        |
| `manuscript-todos.tex` | (empty)      | Review PDF with margin TODOs and `\listoftodos` | `manuscript-todos.pdf`  |

The `\todo{...}` and `\figplaceholder{...}` / `\tabplaceholder{...}` macros
in the body are emitted by `todonotes` and vanish automatically when the
flag is `disable`, so both PDFs share the same numbered structure but
differ only in the visibility of the placeholder annotations.

## Aside: backup venue -- Smart Materials and Structures (SMS, IOP Publishing)

- Journal page: <https://iopscience.iop.org/journal/0964-1726>
- Author guidance: <https://publishingsupport.iopscience.iop.org/journals/smart-materials-and-structures/>
- LaTeX templates: <https://publishingsupport.iopscience.iop.org/questions/article-format-and-templates/>

Highlights:

- No strict word limit; "length should be appropriate to the content."
- Abstract typically 200--300 words.
- IOP provides the `iopart` LaTeX class
  (`\documentclass[12pt]{iopart}`); use is recommended but not mandatory.
- Submit a single PDF with figures/tables embedded inline (no separate
  uploads at initial submission).
- IMRaD-style structure expected.

If we end up retargeting to SMS, swap the class line and bibliography style
(`iopart-num.bst` for numeric references) and adjust the front-matter macros.

## Building

The manuscript is wired into the top-level `Makefile`:

```bash
# Clean PDF (todonotes disabled): manuscript/manuscript.pdf
make manuscript

# Review PDF (todonotes enabled, with \listoftodos): manuscript/manuscript-todos.pdf
make manuscript-todos

# Supplementary Information (its own reference list): manuscript/supplementary.pdf
make manuscript-si

# Both manuscript builds plus the SI
make manuscript-all

# Clean intermediates / output
make clean-manuscript
make distclean-manuscript
```

**Build the SI before the manuscript** (the Makefile does this). The main
text cites SI sections, tables and figures by their S-numbers through the
`xr` package, which reads `supplementary.aux`; the `\siref{}` macro in
`manuscript-body.tex` prints those numbers without a hyperlink. The SI
carries its own `natbib`/`unsrtnat` reference list, numbered independently
of the main text, because several tables moved there for length cite
literature. If an S-number prints as `??`, rebuild the SI and then the
manuscript again.

A LaTeX distribution (MiKTeX or TeX Live) with `pdflatex` and `bibtex` is
required; MiKTeX will install `asmejour` and `todonotes` automatically the
first time you build.

### Word version (`manuscript.docx`)

`manuscript.docx` is an editable Word copy of `manuscript.pdf`, generated
from the same source by `scripts/docx/build_manuscript_docx.py`
(`make manuscript-docx`). It is a one-way export: edits made in Word do not
flow back into `manuscript-body.tex`, so carry them back by hand and rerun
the script after the LaTeX changes.

It keeps the PDF's figure, table, equation, section and citation numbers
(read from the LaTeX `.aux` file), the reference list (from the `.bbl`),
Word equations and tables, the page size, fonts and two columns, the
footers, and the violet placeholder text. Known differences from the PDF:

- Word draws the right column's line numbers in the gutter, so the gutter is
  24 pt instead of 12 pt, and the abstract is not line-numbered.
- Wide figures and tables sit where they are first cited, between
  full-width section breaks, instead of floating to the top of a page.
- Cross-reference and citation numbers are plain text (linked to their
  targets), so they do not renumber if figures or references are added in
  Word.

Requirements: TeX Live with `asmejour`, pandoc 3.1 or newer, and
`pip install python-docx lxml pymupdf`. LibreOffice is optional; when it is
installed, the script uses it to fill in the page numbers of the lists of
figures and tables.

## Files

```
manuscript/
├── manuscript-body.tex   # Shared body (\input{} by both wrappers)
├── manuscript.tex        # Wrapper -- todonotes disabled (clean build)
├── manuscript-todos.tex  # Wrapper -- todonotes enabled (review build)
├── manuscript.pdf        # Built output, todos hidden
├── manuscript-todos.pdf  # Built output, todos visible
├── manuscript.docx       # Editable Word copy of manuscript.pdf (generated)
├── references.bib        # Curated BibTeX database used by the asmejour
│                         #   build (proposal + Edison literature PRs)
├── references-full.bib   # MASTER synthesized library (every Edison query +
│                         #   committed .bib across all branches; see below)
└── README.md             # This file -- venue notes and author guidelines
```

### `references-full.bib` -- master synthesized library

`references-full.bib` is an auto-generated superset library aggregating **every**
reference Edison surfaced across the whole project: every `LITERATURE_HIGH`
(PaperQA) and `ANALYSIS` trajectory plus every committed project `.bib`, from
**all** branches. It currently holds **813 unique entries** (deduplicated by
citation key then DOI), each tagged with a leading `% source:` comment recording
the Edison task id(s) or committed file it came from, and carrying an `abstract`
field wherever the trajectory data provided one.

It is **not** wired into the `pdflatex` build -- the manuscript cites from the
curated `references.bib` to keep the bibliography focused. `references-full.bib`
is the working pool to draw additional citations from as the manuscript grows.

Regenerate it with:

```bash
python scripts/edison/build_master_bib.py \
    --json-dir /tmp/edison_all --bib-dir /tmp/bibsrc \
    --out manuscript/references-full.bib
```

where `/tmp/edison_all` holds every `edison-trajectories/**/*.json` blob and
`/tmp/bibsrc` every committed `.bib`, gathered (content-deduplicated) from all
branches. See the module docstring in `scripts/edison/build_master_bib.py` for
the collection commands and for re-fetching `*-SUBMITTED` placeholder tasks via
the Edison API.

#### DOI verification / abstract enrichment

After generation, every DOI is checked **one-by-one against its authoritative
registered metadata** (CSL JSON from `https://doi.org/<doi>` content
negotiation) by `scripts/edison/verify_bib_dois.py`. For each entry it:

* confirms the stored title matches the title the DOI actually resolves to,
  flagging DOIs that point at an unrelated paper (e.g. `fraternali2015tensegrity`,
  `wang2022bayesian`, `witze2023osirisrex`) or that 404;
* adds the **registered abstract** (taken from that exact DOI's Crossref record,
  JATS/HTML stripped, `&` escaped) to matching entries that lacked one;
* applies a small table of hand-verified corrections -- a wrong DOI fixed
  (`zhang2015tensegrity` &rarr; `10.1063/1.5040850`, the real APL 2018 article)
  and twelve DOIs found via Crossref for entries that previously had none
  (author + title confirmed); and
* writes `edison-trajectories/bib-doi-verification/needs-list.md`: the entries
  whose DOI is wrong/unresolved or that still have no DOI, which is sent to
  Edison (`scripts/edison/submit_bib_doi_verification.py`) for the references
  the public DOI APIs could not settle.

```bash
python scripts/edison/verify_bib_dois.py \
    --bib manuscript/references-full.bib --apply
```

Network results are cached under `--cache-dir` (default `/tmp/verify`) so
re-runs are cheap and offline.