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
two-column ASME final layout. See the comments at the top of `manuscript.tex`
and `asmejour-template.pdf` for the full list of supported options.

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
# Full BibTeX build (pdflatex / bibtex / pdflatex / pdflatex)
make manuscript

# Clean intermediates / output
make clean-manuscript
make distclean-manuscript
```

A LaTeX distribution (MiKTeX or TeX Live) with `pdflatex` and `bibtex` is
required; MiKTeX will install `asmejour` automatically the first time you
build.

## Files

```
manuscript/
├── manuscript.tex   # Main LaTeX source (lorem-ipsum scaffold)
├── references.bib   # BibTeX database (placeholder entry only)
└── README.md        # This file -- venue notes and author guidelines
```
