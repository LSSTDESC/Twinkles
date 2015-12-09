
# Use this shell to interpret shell commands, & pass its value to sub-make
#
export SHELL = /bin/sh
#
MAKEFLAGS =
#
# Define compilation programs:
#
TEX = pdflatex
BIB = bibtex
#
# Base name of the document:
#
DOCUMENT = TwinklesRQ
#
# All tex files used:
#
DEPENDENCIES=twinkles1/*.tex
#
# This line helps prevent make from getting confused in the case where you
# have a file named 'clean'.
#
.PHONY: clean
#
# Generic instruction for compiling tex files.
#
%.pdf: %.tex
	$(TEX) -halt-on-error $<
	$(TEX) -halt-on-error $<
#
# Main instructions, including dependencies:
#
main.pdf: $(DOCUMENT).tex $(DEPENDENCIES)
ifeq ($(wildcard doc_macros.tex),)
	$(error Science Roadmap doc_macros.tex not linked yet, set environment variable SRM_DIR and run 'make links')
else
	@echo "Got macros, compiling latex"
endif
	$(TEX) -halt-on-error $(DOCUMENT).tex
	$(TEX) -halt-on-error $(DOCUMENT).tex
	$(BIB) $(DOCUMENT)
	$(TEX) -halt-on-error $(DOCUMENT).tex
	$(TEX) -halt-on-error $(DOCUMENT).tex
#
# This will compile the document
#
all: clean $(DOCUMENT).pdf
#
# GNU make pre-defines $(RM).  The - in front of $(RM) causes make to
# ignore any errors produced by $(RM).
#
clean:
	- $(RM) *.aux *.toc *.out *.log *.bbl *.blg *.wrt *~
	- $(RM) */*.aux */*.toc */*.out */*.log */*.bbl */*.blg */*.wrt *~
#
vclean:	clean
	- $(RM) $(DOCUMENT).pdf
#
# This will make the soft links that the main document needs. The
# $SRM_DIR environment variable must be set. Note that the SRM macros
# are not to be edited here - if you want a different command, renew it.
#
testenv:
ifdef SRM_DIR
	@echo "SRM environment variable SRM_DIR = ${SRM_DIR}"
else
	$(error Science Roadmap environment variable SRM_DIR is not set)
endif
#
links: testenv
	- ln -sf ${SRM_DIR}/doc_macros.tex .
	- ln -sf ${SRM_DIR}/doc_settings.tex .
	- ln -sf ${SRM_DIR}/desc-logo.png .
	- ln -sf ${SRM_DIR}/apj.bst .
	- chmod -h a-wx doc_*.tex desc-logo.png apj.bst
