# Utah NASA Space Grant Consortium Fellowship Proposal — Marcus Madsen

LaTeX scaffold for the 3–5 page proposal narrative submitted as part of
Marcus Madsen's application (undergraduate) to the Utah NASA Space Grant
Consortium Fellowship (cycle 2026–2027, due 8 May 2026 to `lissa@byu.edu`).
Faculty advisor: Sterling G. Baird, BYU Mechanical Engineering.

This directory contains **only** the proposal narrative.  The other required
materials (application form, two letters of recommendation, transcript) are
handled separately and are not part of this scaffold.

## Files

- `proposal.tex` — the proposal narrative (lorem-ipsum scaffold)
- `references.bib` — BibTeX bibliography (scaffold)
- `Makefile` — `pdflatex` → `bibtex` → `pdflatex` × 2 build pipeline
- `../nasa-26.pdf` — the official application instructions / form (committed
  at the repository root)

## Building

This project is built with **MiKTeX**, which installs required LaTeX packages
on demand the first time the document is built (faster than installing a
full TeX Live distribution up front).

```bash
make            # builds proposal.pdf
make clean      # removes LaTeX build artifacts
make distclean  # also removes proposal.pdf
```

### Installing MiKTeX

On Ubuntu / Debian:

```bash
# Add the MiKTeX repository (replace 'noble' with your Ubuntu codename if needed)
curl -fsSL https://miktex.org/download/key | \
    sudo gpg --dearmor -o /usr/share/keyrings/miktex.gpg
echo "deb [signed-by=/usr/share/keyrings/miktex.gpg] https://miktex.org/download/ubuntu noble universe" | \
    sudo tee /etc/apt/sources.list.d/miktex.list
sudo apt-get update
sudo apt-get install -y miktex

# Per-user setup and enable on-demand package installation
miktexsetup finish
initexmf --set-config-value='[MPM]AutoInstall=1'
export PATH="$HOME/bin:$PATH"
```

On Windows / macOS, install MiKTeX from <https://miktex.org/download> and
ensure on-demand package installation is enabled in the MiKTeX Console.

## Page-limit notes

Per the Utah NASA Space Grant Consortium guidelines, the proposal narrative
is limited to **3–5 pages**.  References do not count toward the page limit.
The current scaffold uses `\lipsum` placeholder text and `\todo{...}` markers
that should be replaced with real content (and the `lipsum` package removed)
before submission.
