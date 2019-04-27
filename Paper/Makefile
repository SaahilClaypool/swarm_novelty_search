#
# Makefile for document
#
# uses latexmk for building
#
# type "make" to build and view dvi
# type "make ps" to build postscript
# type "make pdf" to build adobe pdf
# type "make clean" to remove aux and logs and such
# type "make very-clean" to remove all but source files
#

MASTER= paper
SOURCES= $(MASTER).tex
LATEXMK= latexmk
FLAGS= -pdf # to use "pdflatex"

all: pdf

pdf: $(SOURCES)
	$(LATEXMK) $(FLAGS) -f $(MASTER).tex

very-clean: clean
	$(LATEXMK) -C -f $(MASTER).tex
	/bin/rm -f $(MASTER).pdf
	/bin/rm -f $(MASTER).out
	/bin/rm -f $(MASTER).out
	/bin/rm -f __latexindent_temp.tex

clean:
	$(LATEXMK) -c -f $(MASTER).tex
	/bin/rm -f core *~
	/bin/rm -f $(MASTER).xcp
	/bin/rm -f $(MASTER).bbl
