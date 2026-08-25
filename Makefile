# Makefile for BYU Mentored Research Tensegrity Proposal

TEX = pdflatex
BIB = bibtex
MAIN = proposal

SECTIONS = sections/coverpage.tex sections/budget.tex sections/biosketch.tex

# Journal manuscript (ASME JMD scaffold) lives in manuscript/
MANU_DIR = manuscript

.PHONY: all clean distclean manuscript manuscript-todos manuscript-all manuscript-si clean-manuscript distclean-manuscript

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib $(SECTIONS)
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

# --- Journal manuscript (ASME JMD; see manuscript/README.md) ----------------
# Two builds share manuscript-body.tex via thin wrappers:
#   manuscript.tex          -- todonotes disabled (clean PDF)
#   manuscript-todos.tex    -- todonotes enabled (review PDF with margin
#                              annotations and \listoftodos)
MANU_BODY = $(MANU_DIR)/manuscript-body.tex $(MANU_DIR)/references.bib

manuscript:        $(MANU_DIR)/manuscript.pdf
manuscript-todos:  $(MANU_DIR)/manuscript-todos.pdf
manuscript-si:     $(MANU_DIR)/supplementary.pdf
manuscript-all:    manuscript manuscript-todos manuscript-si

$(MANU_DIR)/supplementary.pdf: $(MANU_DIR)/supplementary.tex
	cd $(MANU_DIR) && $(TEX) supplementary
	cd $(MANU_DIR) && $(TEX) supplementary

$(MANU_DIR)/manuscript.pdf: $(MANU_DIR)/manuscript.tex $(MANU_BODY)
	cd $(MANU_DIR) && $(TEX) manuscript
	cd $(MANU_DIR) && $(BIB) manuscript
	cd $(MANU_DIR) && $(TEX) manuscript
	cd $(MANU_DIR) && $(TEX) manuscript

$(MANU_DIR)/manuscript-todos.pdf: $(MANU_DIR)/manuscript-todos.tex $(MANU_BODY)
	cd $(MANU_DIR) && $(TEX) manuscript-todos
	cd $(MANU_DIR) && $(BIB) manuscript-todos
	cd $(MANU_DIR) && $(TEX) manuscript-todos
	cd $(MANU_DIR) && $(TEX) manuscript-todos

clean-manuscript:
	cd $(MANU_DIR) && rm -f \
	      manuscript.aux manuscript.bbl manuscript.blg manuscript.log \
	      manuscript.out manuscript.toc manuscript.lof manuscript.lot \
	      manuscript.tdo manuscript.synctex.gz manuscript.fdb_latexmk \
	      manuscript.fls manuscript.run.xml manuscript.bcf \
	      manuscript-todos.aux manuscript-todos.bbl manuscript-todos.blg \
	      manuscript-todos.log manuscript-todos.out manuscript-todos.toc \
	      manuscript-todos.lof manuscript-todos.lot manuscript-todos.tdo \
	      manuscript-todos.synctex.gz manuscript-todos.fdb_latexmk \
	      manuscript-todos.fls manuscript-todos.run.xml manuscript-todos.bcf

distclean-manuscript: clean-manuscript
	rm -f $(MANU_DIR)/manuscript.pdf $(MANU_DIR)/manuscript-todos.pdf

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).toc $(MAIN).lof $(MAIN).lot $(MAIN).synctex.gz \
	      $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).run.xml $(MAIN).bcf

distclean: clean
	rm -f $(MAIN).pdf
