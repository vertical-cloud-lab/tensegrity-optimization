#!/usr/bin/env bash
# =============================================================================
# build.sh -- build the arXiv submission bundle for the preprint.
#
#   bash arxiv/build.sh
#
# Steps:
#   1. Build the Supplementary Information (manuscript/supplementary.tex) and
#      read every label's S-number from its .aux file.
#   2. Flatten arxiv/main.tex into arxiv/bundle/main.tex: replace each
#      \siref{label} with its S-number, inline the two generated tables from
#      manuscript/tables/, and strip LaTeX comments (arXiv publishes the
#      source).
#   3. Copy the figures that main.tex includes, and the SI PDF as the
#      ancillary file anc/supplementary.pdf.
#   4. Compile once with BibTeX to write main.bbl, then delete everything in
#      the bundle except main.tex, main.bbl, the figures, and anc/.
#   5. Pack the bundle into arxiv/tensegrity-bo-arxiv-source.tar.gz.
#   6. Unpack the tarball into an empty directory and compile it there with
#      pdflatex alone (no BibTeX, nothing from the repository), as arXiv
#      does. Fail on any error, missing file, or undefined reference or
#      citation; copy the resulting PDF to arxiv/tensegrity-bo-preprint.pdf.
#
# Requires pdflatex and bibtex (TeX Live), gawk, sed, tar, and gzip.
# SOURCE_DATE_EPOCH is pinned to the content-freeze commit (7fce855) so that
# repeated builds give byte-identical PDFs and tarballs.
# =============================================================================
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
ARX="$REPO/arxiv"
BUNDLE="$ARX/bundle"
TARBALL="$ARX/tensegrity-bo-arxiv-source.tar.gz"
PDF="$ARX/tensegrity-bo-preprint.pdf"

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1795814480}"  # commit 7fce855
export FORCE_SOURCE_DATE=1
export TZ=UTC

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
LATEX=(pdflatex -interaction=nonstopmode -halt-on-error)

# --- 1. Supplementary Information --------------------------------------------
echo "[1/6] Building the Supplementary Information"
mkdir -p "$WORK/si"
(
  cd "$REPO/manuscript"
  "${LATEX[@]}" -output-directory="$WORK/si" supplementary > "$WORK/si-1.log"
  (cd "$WORK/si" && BIBINPUTS="$REPO/manuscript:" bibtex supplementary > "$WORK/si-bib.log")
  "${LATEX[@]}" -output-directory="$WORK/si" supplementary > "$WORK/si-2.log"
  "${LATEX[@]}" -output-directory="$WORK/si" supplementary > "$WORK/si-3.log"
)
if grep -E -q 'undefined|Rerun to get' "$WORK/si/supplementary.log"; then
  grep -E 'undefined|Rerun to get' "$WORK/si/supplementary.log" | head
  echo "ERROR: the SI build left undefined references" >&2
  exit 1
fi
# \newlabel{si:mass}{{S3}{5}{...}{section.3}{}}  ->  s|\\siref{si:mass}|S3|g
sed -n 's/^\\newlabel{\([^}@]*\)}{{\([^}]*\)}.*/s|\\\\siref{\1}|\2|g/p' \
  "$WORK/si/supplementary.aux" > "$WORK/siref.sed"
echo "      $(wc -l < "$WORK/siref.sed") SI labels read"

# --- 2. Flatten main.tex -------------------------------------------------------
echo "[2/6] Flattening main.tex"
rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/anc"
# Inline \input{tables/<name>} from manuscript/tables/<name>.tex.
gawk -v tabdir="$REPO/manuscript/tables" '
  match($0, /^[ \t]*\\input\{tables\/([^}]+)\}[ \t]*$/, m) {
    f = tabdir "/" m[1] ".tex"
    while ((getline line < f) > 0) print line
    close(f)
    next
  }
  { print }
' "$ARX/main.tex" \
  | sed -f "$WORK/siref.sed" -e '/^\\providecommand{\\siref}/d' \
  | gawk '
      # Strip comments. A line that is only a comment is dropped; a trailing
      # comment keeps its "%" so that no space appears where the line ended.
      # The first line (\pdfoutput=1) is kept as arXiv expects it there.
      NR == 1 { print; next }
      /^[ \t]*%/ { next }
      {
        out = ""; n = length($0)
        for (i = 1; i <= n; i++) {
          c = substr($0, i, 1)
          if (c == "\\") { out = out substr($0, i, 2); i++; continue }
          if (c == "%") { out = out "%"; break }
          out = out c
        }
        print out
      }
    ' \
  | cat -s > "$BUNDLE/main.tex"
if grep -n '\\siref{' "$BUNDLE/main.tex"; then
  echo "ERROR: unresolved \\siref pointers (label missing from the SI)" >&2
  exit 1
fi

# --- 3. Figures and the ancillary SI -------------------------------------------
echo "[3/6] Copying figures and the ancillary SI"
grep -o -E '\\includegraphics(\[[^]]*\])?\{[^}]+\}' "$BUNDLE/main.tex" \
  | sed -E 's/.*\{([^}]+)\}$/\1/' | sort -u > "$WORK/figures.txt"
while read -r fig; do
  mkdir -p "$BUNDLE/$(dirname "$fig")"
  cp "$REPO/$fig" "$BUNDLE/$fig"
  echo "      $fig"
done < "$WORK/figures.txt"
cp "$WORK/si/supplementary.pdf" "$BUNDLE/anc/supplementary.pdf"

# --- 4. Write main.bbl ----------------------------------------------------------
echo "[4/6] Compiling once with BibTeX to write main.bbl"
(
  cd "$BUNDLE"
  "${LATEX[@]}" main > "$WORK/main-1.log"
  BIBINPUTS="$ARX:$REPO/manuscript:" bibtex main > "$WORK/main-bib.log"
  "${LATEX[@]}" main > "$WORK/main-2.log"
  "${LATEX[@]}" main > "$WORK/main-3.log"
)
if grep -E -q 'Warning--|error message' "$BUNDLE/main.blg"; then
  grep -E 'Warning--|error message' "$BUNDLE/main.blg"
  echo "(BibTeX warnings above; check the reference list)"
fi
find "$BUNDLE" -maxdepth 1 -type f ! -name main.tex ! -name main.bbl -delete

# --- 5. Tarball -----------------------------------------------------------------
echo "[5/6] Packing $(basename "$TARBALL")"
(
  cd "$BUNDLE"
  find . -type f | sed 's|^\./||' | LC_ALL=C sort > "$WORK/files.txt"
  tar --format=gnu --owner=0 --group=0 --numeric-owner \
      --mtime="@$SOURCE_DATE_EPOCH" --no-recursion -cf - -T "$WORK/files.txt" \
    | gzip -n -9 > "$TARBALL"
)
sed 's/^/      /' "$WORK/files.txt"

# --- 6. Clean-room compile ------------------------------------------------------
echo "[6/6] Compiling the tarball alone in an empty directory (pdflatex only)"
CLEAN="$WORK/clean"
mkdir -p "$CLEAN"
tar -xzf "$TARBALL" -C "$CLEAN"
(
  cd "$CLEAN"
  # No BibTeX run and no access to the repository: main.bbl must suffice.
  export TEXINPUTS=".:" BIBINPUTS="." BSTINPUTS="."
  for pass in 1 2 3; do
    "${LATEX[@]}" main > "$WORK/clean-$pass.log"
  done
)
LOG="$CLEAN/main.log"
fail=0
grep -q '(./main.bbl' "$LOG" || { echo "ERROR: main.bbl was not read" >&2; fail=1; }
if grep -E -n '^! |LaTeX Error|not found|undefined|Rerun to get' "$LOG"; then
  echo "ERROR: the clean-room build has errors or undefined references" >&2
  fail=1
fi
[ "$fail" -eq 0 ] || exit 1
cp "$CLEAN/main.pdf" "$PDF"
pages=$(grep -o -E 'Output written on main.pdf \([0-9]+ pages' "$LOG" | grep -o -E '[0-9]+ pages')
over=$(grep -c 'Overfull' "$LOG" || true)
echo "Done: $(basename "$PDF") ($pages, $over overfull boxes),"
echo "      $(basename "$TARBALL") ($(du -h "$TARBALL" | cut -f1)), bundle in arxiv/bundle/"
