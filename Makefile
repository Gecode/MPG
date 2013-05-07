VERSION = 4.0.1
YEAR    = 2013

CHAPSRC = \
	intro \
	m-started m-comfy m-integer m-set m-float m-minimodel \
	m-branch m-search m-gist m-driver \
	p-started p-avoid p-reified p-views \
	p-domain p-advisors p-memory p-sets p-floats \
	b-started \
	s-started s-recomputation s-engine \
	v \
	c-knights c-nonogram c-magic-sequence c-warehouses \
	c-golf c-golomb c-kakuro c-crossword c-photo \
	c-bin-packing

INSRC = ${CHAPSRC} \
	changelog acks titles

INTEXSRC = \
	${INSRC:%=%.tex}

MODELCPP = \
	send-more-money-de-mystified \
	send-more-money-with-gist \
	send-more-money-with-gist-inspection \
	send-more-money \
	send-most-money-with-cost \
	send-most-money-with-driver \
	send-most-money \
	knights nonogram magic-sequence magic-sequence-gcc \
	warehouses golf golomb kakuro kakuro-naive crossword \
	crossword-optimized photo photo-without-modeling-support \
	bin-packing-naive bin-packing-propagation \
	bin-packing-branching \
	latin-square-ldsb
TESTCPP = \
	less-even-better less-better less-concise less \
	disequality \
	equal-naive equal equal-idempotent \
	equal-idempotent-using-modification-events \
	or-true or-true-concise \
	or-true-with-dynamic-subscriptions \
	less-or-equal-reified-full less-or-equal-reified-half \
	max-using-rewriting \
	or-true-using-rewriting \
	min-and-max less-for-integer-and-Boolean-variables \
	domain-equal-with-and-without-offset \
	or-and-and-from-or \
	naive-domain-equal non-shared-domain-equal \
	domain-equal-using-bounds-propagation \
	domain-equal-using-staging \
	domain-equal-with-offset \
	samedom samedom-using-predefined-view-advisors or \
	intersection \
	linear
NOTESTCPP = \
	shared-object-and-handle local-object-and-handle \
	local-object-with-external-resources \
	none-min none-min-improved size-min assign-min none-min-and-none-max \
	dfs-binary dfs bab \
	dfs-using-full-recomputation dfs-using-full-recomputation-and-lao \
	dfs-using-hybrid-recomputation dfs-using-adaptive-recomputation \
	bab-using-full-recomputation \
	dfs-engine

MSVCEXE		= $(MODELCPP:%=%.exe)
MSVCTESTEXE	= $(TESTCPP:%=test-%.exe)
MSVCNOTESTEXE	= $(NOTESTCPP:%=notest-%.exe)
#MSVCCPPOPT	= -nologo -EHsc -MDd -wd4355	
MSVCCPPOPT	= -DNDEBUG -nologo -EHsc -MD -Ox -fp:fast -GS- -wd4355
MSVCINCL	= -I"../../gecode/trunk"
MSVCLINK	= /link /LIBPATH:"../../gecode/trunk"

GCCEXE = $(MODELCPP)
GCCTESTEXE = $(TESTCPP:%=test-%)
GCCNOTESTEXE = $(NOTESTCPP:%=notest-%)
GCCCPPOPT = -NDEBUG -fvisibility=hidden -ffast-math -fno-strict-aliasing \
	-pthread -O3 -ggdb
#GCCCPPOPT = -pthread -ggdb
GCCINCL = -I../../gecode/trunk
GCCLINK = -L../../gecode/trunk -lgecodedriver -lgecodegist -lgecodesearch \
	-lgecodeminimodel -lgecodeset \
	-lgecodeint -lgecodekernel -lgecodesupport

MAIN = MPG

TEXSRC = \
	${MAIN}.tex macros.tex ${INTEXSRC}

PS2PDF	= ps2pdf
DVIPS	= dvips -K -Ppdf
DVIPDF	= dvipdf
BIBTEX	= bibtex
LATEX	= latex
GL	= perl bin/gl.perl $(YEAR)

all: quick

acks.tex: changelog.tex.in
	perl bin/gen-ack.perl < changelog.tex.in > acks.tex

titles.tex.in: ${CHAPSRC:%=%.tex.in} bin/gen-titles.perl
	perl bin/gen-titles.perl ${CHAPSRC:%=%.tex.in} > titles.tex.in

MPG.tex.in: MPG.tex.in.in ${INTEXSRC}
	sed "s|@VERSION@|$(VERSION)|g" < MPG.tex.in.in | \
	sed "s|@YEAR@|$(YEAR)|g" | \
	perl bin/include.perl | \
	perl bin/shorten.perl > MPG.tex.in

#MPG.tex.in: MPG.tex.in.in ${INTEXSRC}
#	sed "s|@VERSION@|$(VERSION)|g" < MPG.tex.in.in | \
#	sed "s|@YEAR@|$(YEAR)|g" > MPG.tex.in

quick: MPG.tex references.bib
	$(LATEX) MPG
	$(BIBTEX) MPG
	mv MPG.out MPG.out.in
	perl bin/fixout.perl < MPG.out.in > MPG.out
	$(LATEX) MPG
	$(DVIPS) MPG.dvi
	$(PS2PDF) MPG.ps

MPG.bib: MPG.bib.in
	sed "s|@VERSION@|$(VERSION)|g" < MPG.bib.in | \
	sed "s|@YEAR@|$(YEAR)|g" > MPG.bib

gecode.pl: ${CHAPSRC:%=%.tex.in}
	perl bin/gccat.perl ${VERSION} ${YEAR} prolog ${CHAPSRC:%=%.tex.in} > \
		gecode.pl

gecode.xml: ${CHAPSRC:%=%.tex.in}
	perl bin/solver.perl ${VERSION} ${CHAPSRC:%=%.tex.in} > \
		gecode.xml

distzip: MPG.bib MPG.tex.in MPG.pdf gecode.pl gecode.xml
	rm -rf dist
	mkdir dist
	mkdir dist/MPG
	(cd dist/MPG; \
	 perl ../../bin/gen-files.perl '../..' < ../../MPG.tex.in; \
	 cd ..; \
	 tar cf - MPG | gzip -9 > MPG.tar.gz; \
	 7z a MPG.7z MPG; \
	 rm -rf MPG)
	mkdir dist/MPG
	cp MPG.pdf MPG.bib gecode.pl gecode.xml dist
	cp *.cpp int.vis int.hh template.vis dist/MPG
	(cd dist;zip -9 -r ../MPG.zip gecode.pl MPG.pdf MPG.bib MPG.tar.gz MPG.7z MPG)
	rm -rf dist

.SUFFIXES: .dvi .ps .pdf .aux .bbl .tex.in .tex .cpp .exe
.PRECIOUS: .obj .cpp

%.tex: %.tex.in bin/gl.perl
	$(GL) < $< > $@

test-%.cpp: %.cpp test/%.cpp
	cat $< test/$< > test-$<
notest-%.cpp: %.cpp notest/%.cpp
	cat $< notest/$< > notest-$<

%.obj: %.cpp
	cl $(MSVCINCL) $(MSVCCPPOPT) -c -Fo$@ -Tp$<

test-%.exe: test-%.obj
	cl $(MSVCCPPOPT) $(MSVCINCL) -Fe$@ \
		../../gecode/trunk/test/test.obj \
		../../gecode/trunk/test/int.obj \
		../../gecode/trunk/test/float.obj \
		../../gecode/trunk/test/set.obj \
		$< $(MSVCLINK)
%.exe: %.obj
	cl $(MSVCCPPOPT) $(MSVCINCL) -Fe$@ $< $(MSVCLINK)

$(TESTCPP:%=test-%): test-%: test-%.o
	$(CXX) $(GCCCPPOPT) $(GCCINCL) -o $@ \
		../gecode/trunk/test/test.o \
		../gecode/trunk/test/int.o \
		../gecode/trunk/test/float.o \
		../gecode/trunk/test/set.o \
		$< $(GCCLINK)

$(TESTCPP:%=test-%.o): test-%.o: test-%.cpp
	$(CXX) $(GCCCPPOPT) $(GCCINCL) -c $< -o $@

$(NOTESTCPP:%=notest-%.o): notest-%.o: notest-%.cpp
	$(CXX) $(GCCCPPOPT) $(GCCINCL) -c $< -o $@

$(MODELCPP:%=%.o): %.o: %.cpp
	$(CXX) $(GCCCPPOPT) $(GCCINCL) -c $< -o $@

$(MODELCPP) $(NOTESTCPP:%=notest-%): %: %.o
	$(CXX) $(GCCCPPOPT) -o $@ $< $(GCCLINK)

msvc: msvc-programs msvc-test msvc-notest

msvc-programs: $(INTEXSRC) $(MSVCEXE)

msvc-test: $(INTEXSRC) $(MSVCTESTEXE) $(TESTCPP:%=%.cpp)

msvc-notest: $(INTEXSRC) $(MSVCNOTESTEXE) $(NOTESTCPP:%=%.cpp)

gcc: gcc-programs gcc-test gcc-notest

gcc-programs: $(INTEXSRC) $(GCCEXE)

gcc-test: $(INTEXSRC) $(GCCTESTEXE) $(TESTCPP:%=%.cpp)

gcc-notest: $(INTEXSRC) $(GCCNOTESTEXE) $(NOTESTCPP:%=%.cpp)

tex: $(INTEXSRC)

clean::
	rm -f MPG.warns MPG.out MPG.out.in
	rm -f *.aux *.lo[gftp] *.bbl *.blg *~ *.toc *.bak *.ilg *.ind *.idx *.idxx *.brf *.ps.bz2 *.pdf.bz2 *.top 
	rm -f *.obj *.exe *.manifest
	rm -f ${INTEXSRC} titles.tex.in
	rm -f MPG.tex MPG.tex.in

realclean:: clean
	rm -f MPG.ps MPG.dvi MPG.pdf MPG.zip MPG.bib
	rm -f gecode.pl gecode.xml
	rm -f *.cpp int.hh

veryclean:: realclean

