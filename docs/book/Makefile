######## Configuration
#


#
#  This makefile supports multiple targets.  Currently we have only one.
#
#  SOURCES must end ".xml" and must be DocBook files.
#
SOURCES = Book.xml

#  The extension for all HTML output (e.g. html or shtml).  Must NOT
#  start with a dot.
HTML_EXT = html


# All stylesheets used by various outputs
#
STYLESHEETS_TITLEPAGE := xsl/fo-titlepage.xsl
STYLESHEETS_CHUNK := xsl/html-chunk.xsl xsl/html-common.xsl xsl/common.xsl
STYLESHEETS_HTML := xsl/html-single.xsl xsl/html-common.xsl xsl/common.xsl
STYLESHEETS_FO := xsl/fo.xsl $(STYLESHEETS_TITLEPAGE) xsl/common.xsl 
STYLESHEETS_MAN := xsl/man.xsl xsl/common.xsl
STYLESHEETS_EPUB := xsl/epub.xsl xsl/common.xsl


#########  Some derived locations: output files
#

FO_FILES  = $(SOURCES:%.xml=%-a4.fo) $(SOURCES:%.xml=%-letter.fo)
PDF_FILES = $(FO_FILES:%.fo=%.pdf)

HTML_SINGLE_FILES = $(SOURCES:%.xml=%.$(HTML_EXT))
HTML_CHUNK_FILES = $(SOURCES:%.xml=%/index.$(HTML_EXT))
HTML_ALL_CHUNK_FILES = $(SOURCES:%.xml=%) # used only for rm -rf.

TXT_FILES = $(SOURCES:%.xml=%.txt)

FO_DEPS = $(FO_FILES:%=.%.d)
HTML_SINGLE_DEPS = $(HTML_SINGLE_FILES:%=.%.d)
HTML_CHUNK_DEPS = $(SOURCES:%.xml=.%-chunk.d)

EPUB_FILES = $(SOURCES:%.xml=%.epub)

GFX_FILES = images/important.png images/warning.png images/caution.png images/note.png images/tip.png

# Used by deploy target
ALL = $(HTML_SINGLE_FILES) $(PDF_FILES) $(HTML_ALL_CHUNK_FILES) $(EPUB_FILES) book.css $(GFX_FILES)
ALL_INSTALLED = $(ALL:%=%__INSTALL__)
ALL_TEST_INSTALLED = $(ALL:%=%__TEST_INSTALL__)


WWW_SERVER = www.dcache.org
WWW_SERVER_BASE_DIR = /data/www/dcache.org
WWW_LOCATION = /manuals/Book-1.9.11/
WWW_TEST_LOCATION = /manuals/Book-1.9.11-test/

# NB we don't do deps on txt as it depends on html-single output.  This
#    is cheating, but hey, it works.

DEP_FILES = $(FO_DEPS) $(HTML_SINGLE_DEPS) $(HTML_CHUNK_DEPS)


######### Common options
#

XSLT_FLAGS = --nonet --xinclude


######### Software Configs
#

# Default value for binaries
#
SVN ?= svn
FOP ?= fop
XSLTPROC ?= xsltproc


###### Docbook targets. Pure DocBook is generated from the sources first
#

.PHONY: info
info:
	@echo
	@echo "  The dCache Book"
	@echo "  ---------------"
	@echo
	@echo "Available main build targets:"
	@echo
	@echo "  all         -- build everything"
	@echo "  pdf         -- build PDF versions"
	@echo "  html        -- build HTML pages"
	@echo "  txt         -- build text version"
	@echo "  man         -- build man pages"
	@echo "  epub        -- build EPUB version"
	@echo "  deploy      -- use scp to deploy files to http://${WWW_SERVER}${WWW_LOCATION}"
	@echo "  test-deploy -- use scp to deploy files to http://${WWW_SERVER}${WWW_TEST_LOCATION}"
	@echo
	@echo "More specific build targets:"
	@echo
	@echo "  html-single --  Build single-page HTML pages"
	@echo "  html-chunk  --  Build multi-page HTML pages"
	@echo
	@echo "Cleaning targets:"
	@echo "  clean       -- remove backup files"
	@echo "  distclean   -- remove all generated files"
	@echo

all: pdf html txt man epub


###### HTML targets
#

#  Plain chunked HTML
#
html:  html-single html-chunk

html-single: $(HTML_SINGLE_FILES)
html-chunk: $(HTML_CHUNK_FILES)


%.$(HTML_EXT): %.xml $(STYLESHEETS_HTML) shared-entities.xml
	$(XSLTPROC) $(XSLT_FLAGS) --stringparam html.ext ".$(HTML_EXT)" -o $@ xsl/html-single.xsl $<

%/index.$(HTML_EXT): %.xml $(STYLESHEETS_CHUNK) shared-entities.xml
#	$(XSLTPROC) $(XSLT_FLAGS) -o $(@:%/index.$(HTML_EXT)=%)/ xsl/html-chunk.xsl $<
	$(XSLTPROC) $(XSLT_FLAGS) --stringparam html.ext ".$(HTML_EXT)" --stringparam base.dir $(@:%/index.$(HTML_EXT)=%)/ xsl/html-chunk.xsl $<

###### Text only

HTML_TO_TXT := /usr/bin/w3m -T text/html -dump
#HTML_TO_TXT := /usr/bin/lynx -force_html -dump -nolist -width=72
#HTML_TO_TXT : = /usr/bin/links -dump

txt: $(TXT_FILES)

%.txt: %.$(HTML_EXT)
	$(HTML_TO_TXT) $< > $@

# (should we also produce install instructions as separate txt file?)


###### man page targets
#

## TODO: we should autogenerate dependencies, like with other targets
man: Book.xml $(STYLESHEETS_MAN) shared-entities.xml
	@[ ! -d man ] && mkdir man || :
	$(XSLTPROC) $(XSLT_FLAGS) --output man/ xsl/man.xsl $<


###### EPUB targets
#

## TODO: we should autogenerate dependencies, like with other targets
epub: $(EPUB_FILES)

%.epub: %.xml $(STYLESHEETS_EPUB) shared-entities.xml
	$(XSLTPROC) $(XSLT_FLAGS) xsl/epub.xsl $<
	echo application/epub+zip > mimetype
	zip -rn mimetype $@ mimetype META-INF OEBPS
	rm -rf mimetype META-INF OEBPS

###### FO-based targets
#

# PDF from XSL-FO
#
pdf: $(PDF_FILES)

%-a4.fo: %.xml $(STYLESHEETS_FO) shared-entities.xml
	$(XSLTPROC) $(XSLT_FLAGS) --output $@ --stringparam paper.type A4  xsl/fo.xsl $<

%-letter.fo: %.xml $(STYLESHEETS_FO) shared-entities.xml
	$(XSLTPROC) $(XSLT_FLAGS) --output $@ --stringparam paper.type letter xsl/fo.xsl $<

%.pdf: %.fo
	$(FOP) -fo $< -pdf $@

# The title page is FO-specific; the format is derived from an XML file.
%.xsl: %.xml
	$(XSLTPROC) $(XSLT_FLAGS) --output $@ http://docbook.sourceforge.net/release/xsl/current/template/titlepage.xsl $<

###### Deployment targets
#

deploy: $(ALL_INSTALLED)
	@echo
	@echo "Book now updated at http://${WWW_SERVER}${WWW_LOCATION}"
	@echo

test-deploy: $(ALL_TEST_INSTALLED)
	@echo
	@echo "Book now updated at http://${WWW_SERVER}${WWW_TEST_LOCATION}"
	@echo

%__INSTALL__: %
	chmod a+r,g+w $<
	scp -p $< $(WWW_SERVER):$(WWW_SERVER_BASE_DIR)$(WWW_LOCATION)

%__TEST_INSTALL__: %
	chmod a+r,g+w $<
	scp -p $< $(WWW_SERVER):$(WWW_SERVER_BASE_DIR)$(WWW_TEST_LOCATION)

#  Unfortunately, we need a special case here.
Book__INSTALL__: Book/index.$(HTML_EXT)
	chmod -R a+Xr,g+w Book/*
	chmod g+s Book
	find Book -type d -exec chmod g+s \{\} \;
	scp -pr Book/* $(WWW_SERVER):$(WWW_SERVER_BASE_DIR)$(WWW_LOCATION)

Book__TEST_INSTALL__: Book/index.$(HTML_EXT)
	chmod -R a+Xr,g+w Book/*
	chmod g+s Book
	find Book -type d -exec chmod g+s \{\} \;
	scp -pr Book/* $(WWW_SERVER):$(WWW_SERVER_BASE_DIR)$(WWW_TEST_LOCATION)



###### Cleaning targets
#

clean:
	rm -rf *~ *.bak

distclean: clean
	rm -rf $(WEB_LOCATION) $(TXT_FILES) $(PDF_FILES) $(FO_FILES) $(DEP_FILES) $(HTML_SINGLE_FILES) $(HTML_ALL_CHUNK_FILES) $(STYLESHEETS_TITLEPAGE) $(EPUB_FILES)


###### Create (dynamic) Makefile dependencies
#

.%-letter.fo.d .%-a4.fo.d: %.xml
	$(XSLTPROC) --nonet -stringparam output-file $(@:.%.d=%) --stringparam initial-file $< --stringparam graphics SVG  --stringparam dep-file $@ dependency.xsl $< > $@

.%.html.d: %.xml
	$(XSLTPROC) --nonet -stringparam output-file $(@:.%.d=%) --stringparam initial-file $< --stringparam graphics none --stringparam dep-file $@ dependency.xsl $< > $@

.%-chunk.d: %.xml
	$(XSLTPROC) --nonet -stringparam output-file $(@:.%-chunk.d=%/index.$(HTML_EXT)) --stringparam initial-file $< --stringparam graphics none --stringparam dep-file $@ dependency.xsl $< > $@

.PHONY:	all pdf html html-single html-chunked
.PHONY: clean distclean
.PRECIOUS: $(FO_FILES)

-include $(DEP_FILES)
