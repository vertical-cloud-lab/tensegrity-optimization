# arXiv preprint

A journal-neutral version of the manuscript for arXiv. The content, figures,
tables and numbers are those of the ASME Journal of Mechanical Design draft
at commit `7fce855` (`manuscript/`); only the layout and the journal-specific
items differ (listed below). Nothing has been submitted.

## Files

| File | What it is |
|---|---|
| [`tensegrity-bo-arxiv-source.tar.gz`](tensegrity-bo-arxiv-source.tar.gz) | **The file to upload.** `main.tex`, `main.bbl`, the six figures, and `anc/supplementary.pdf` |
| [`tensegrity-bo-preprint.pdf`](tensegrity-bo-preprint.pdf) | The PDF compiled from that tarball alone (28 pages) |
| [`METADATA.md`](METADATA.md) | Title, authors, plain-text abstract, comments line, categories, licence |
| [`bundle/`](bundle/) | The tarball's contents, unpacked for review |
| [`main.tex`](main.tex) | Source of the preprint. It cites the SI with `\siref{label}` and includes the two generated tables from `manuscript/tables/` |
| [`build.sh`](build.sh) | Builds everything above from `main.tex`, the SI source and the repository figures |
| [`journal-strings.bib`](journal-strings.bib) | Two journal-name strings that `manuscript/references.bib` otherwise takes from the ASME bibliography style |
| [`strip-todos.awk`](strip-todos.awk) | Removes `\todo{}` notes from a LaTeX file; used to port the body and to check it against the manuscript |

## Submitting

1. Get every co-author's agreement to post (arXiv's submission agreement
   asks the submitter to have it).
2. On arxiv.org, start a new submission, choose the licence and the primary
   category from `METADATA.md`, and upload
   `tensegrity-bo-arxiv-source.tar.gz` as it is.
3. Fill in the metadata from `METADATA.md`.
4. Check arXiv's compiled PDF against `tensegrity-bo-preprint.pdf` (page
   count, figures, reference list, S-numbers), and check that
   `supplementary.pdf` appears under "Ancillary files".

## Rebuilding

```bash
./arxiv/build.sh
```

Requires TeX Live (pdflatex, bibtex, and the packages `main.tex` and
`manuscript/supplementary.tex` load), gawk, sed, tar and gzip. The script:

1. builds the SI from `manuscript/supplementary.tex` and reads each label's
   S-number from its `.aux` file;
2. writes `bundle/main.tex`: every `\siref{label}` replaced by its S-number,
   the two tables from `manuscript/tables/` inlined, and comments stripped
   (arXiv publishes the source);
3. copies the figures `main.tex` includes and the SI PDF (as
   `anc/supplementary.pdf`);
4. runs pdflatex and BibTeX (style `unsrtnat`) to write `main.bbl`, then
   deletes everything else from the bundle;
5. packs the tarball;
6. unpacks the tarball into an empty directory and compiles it there with
   pdflatex only, three passes, no BibTeX and nothing from the repository,
   and fails on any error, missing file, or undefined reference or citation.
   The PDF from this step is `tensegrity-bo-preprint.pdf`.

`SOURCE_DATE_EPOCH` is pinned to the time of commit `7fce855`, so a rebuild
from unchanged sources gives byte-identical PDFs and tarball.

If the manuscript changes (for an arXiv v2), update the body of `main.tex`
from `manuscript/manuscript-body.tex`, run `strip-todos.awk` on it, and rerun
the script.

## Differences from the manuscript at `7fce855`

The body (Introduction to Conclusions) is `manuscript/manuscript-body.tex`
with its `\todo{}` review notes removed. A diff of the two, both with the
notes removed, shows only the changes in this table.

| Item | JMD draft (`manuscript/`) | Preprint (`arxiv/`) |
|---|---|---|
| Layout | `asmejour` class, two columns, line numbers, "Journal of Mechanical Design / PREPRINT FOR REVIEW" footers, PDF/A metadata | `article` class, one column, 11 pt, 1 in margins, Latin Modern; no running journal name, line numbers or paper-number fields |
| Author block | One ASME block per author; "Corresponding Author" footnote | One author line and one affiliation (as in the SI); a footnote for the equal-contribution marks and the two corresponding authors' e-mail addresses |
| Keywords | Terms from JMD's keyword list | Bayesian optimization, tensegrity, multi-material 3D printing, drop testing, design of experiments, data-driven design |
| Abstract | | Unchanged |
| SI pointer | SI cited as a separate document | A note after the abstract says the SI is the ancillary file `anc/supplementary.pdf`. S-numbers are typed in by the build, since arXiv has no SI `.aux` file |
| Figures | Column-width overview and trace figures; `[t]` floats | Overview at 0.52 and trace at 0.55 of the text width; three-print figure at full width; floats may also go at the bottom or on a float page, so Tables 3 and 4 do not drift past the references |
| Use of AI Tools (Methods 3.6) | Last sentence points to the Acknowledgment | Points to the new AI Use Statement |
| Acknowledgment | Funding and thanks, then a long AI-disclosure paragraph | "Acknowledgments": funding and thanks only |
| AI Use Statement | | New short section, from `manuscript/AI-USE.md`: tools, models, access routes, date ranges, what they were used for, and the authors' responsibility |
| Funding Data | ASME's itemized list with the Funder ID | Removed; the funding sentence stays in the Acknowledgments |
| Data Availability Statement | Repository link, contents list, "a Zenodo DOI will be minted at acceptance" | The public repository with each part cited by a fixed commit (below), and a list of what is not public yet |
| Nomenclature | ASME `nomenclature` environment | Plain two-column list, same entries, before the references |
| References | `asmejour.bst` (ASME style) | `unsrtnat`; same 57 entries in the same citation order. `journal-strings.bib` supplies the two journal names (Journal of Mechanical Design, Journal of Applied Mechanics) that `references.bib` abbreviates |
| Review notes | `\todo{}` notes, hidden in `manuscript.pdf` | Removed from the source, since arXiv publishes it |

The caveats the 2026-11-27 fresh-eyes read added are unchanged: the four
rebound fractions bounded by the second-contact search window (Methods 3.3,
Results 4.2, Limitations) and the retrospective seat-gauge flags (Results
4.2, Limitations).

## Data availability: the commits cited

The repository is public and has no tags, so the statement cites commits.
Each resolves at `https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/<commit>`.

| Content | Commit | Branch |
|---|---|---|
| Data snapshot behind every table and figure, regeneration scripts, cross-validation folds, surrogate re-analysis, `manuscript/AI-USE.md` | `7fce855` | `copilot/vertical-cloud-labtensegrity-optimization` (PR #76) |
| BO campaign code, per-round experiment state, recommendations and predictions, slicer projects, parametric CAD | `65ff978` | `claude/issue-98-20260821-0103` (PR #102) |
| Drop-test pipeline and per-drop session records | `f6471ad` | `copilot/add-drop-test-protocol-again` (PR #86) |
| Simulation study and simulation-only campaign | `94e53a8` | `copilot/explore-simulations-for-tensegrity` (PR #33) |
| Video tracking for the rebound check | `4e4c0c2` | `claude/issue-134-20261116-1959` |
| Joint-design study | `2a644f5` | `copilot/explore-joint-design-for-petg-tpu` (PR #39) |

Not public yet, as the statement says: the raw high-speed videos, a licence
file, and a versioned archive with a DOI.

A commit stays reachable while some branch, tag or pull-request ref
contains it. Five of the six commits are pull-request heads or their
ancestors (PRs #76, #102, #86, #33 and #39), and GitHub keeps a pull
request's head ref after its branch is deleted. `4e4c0c2` (the video
branch) has no pull request, so a tag or a pull request for that branch
would keep it reachable if the branch is ever deleted.
