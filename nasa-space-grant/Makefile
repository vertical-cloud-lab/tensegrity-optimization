# Makefile for the Utah NASA Space Grant Fellowship Proposal (Marcus Madsen)

TEX  = pdflatex
BIB  = bibtex
MAIN = proposal

.PHONY: all clean distclean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).toc $(MAIN).lof $(MAIN).lot $(MAIN).synctex.gz \
	      $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).run.xml $(MAIN).bcf

distclean: clean
	rm -f $(MAIN).pdf
