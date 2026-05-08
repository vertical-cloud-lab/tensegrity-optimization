# Makefile for BYU Mentored Research Tensegrity Proposal

TEX = pdflatex
BIB = bibtex
MAIN = proposal

SECTIONS = sections/coverpage.tex sections/budget.tex sections/biosketch.tex

# Journal manuscript (ASME JMD scaffold) lives in manuscript/
MANU_DIR = manuscript
MANU     = manuscript

.PHONY: all clean distclean manuscript clean-manuscript distclean-manuscript

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib $(SECTIONS)
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

# --- Journal manuscript (ASME JMD; see manuscript/README.md) ----------------
manuscript: $(MANU_DIR)/$(MANU).pdf

$(MANU_DIR)/$(MANU).pdf: $(MANU_DIR)/$(MANU).tex $(MANU_DIR)/references.bib
	cd $(MANU_DIR) && $(TEX) $(MANU)
	cd $(MANU_DIR) && $(BIB) $(MANU)
	cd $(MANU_DIR) && $(TEX) $(MANU)
	cd $(MANU_DIR) && $(TEX) $(MANU)

clean-manuscript:
	cd $(MANU_DIR) && rm -f $(MANU).aux $(MANU).bbl $(MANU).blg \
	      $(MANU).log $(MANU).out $(MANU).toc $(MANU).lof $(MANU).lot \
	      $(MANU).synctex.gz $(MANU).fdb_latexmk $(MANU).fls \
	      $(MANU).run.xml $(MANU).bcf

distclean-manuscript: clean-manuscript
	rm -f $(MANU_DIR)/$(MANU).pdf

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).toc $(MAIN).lof $(MAIN).lot $(MAIN).synctex.gz \
	      $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).run.xml $(MAIN).bcf

distclean: clean
	rm -f $(MAIN).pdf
