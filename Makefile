PACKAGE_NAME=vmimagemanager
####################################################################
# Distribution Makefile
####################################################################

ifeq ($(runprefix),"")
runprefix=$(prefix)
endif
name=$(shell echo ${runprefix} | sed -e 's/\//\\\//g')
.PHONY: configure install clean

all: configure

####################################################################
# Prepare
####################################################################

jam:
	echo jam

prepare:
	rm -f *~ src/*~ 
	@mkdir -p build/
	

####################################################################
# Configure
####################################################################

configure: 
	@echo "No configuration required, use either 'make install' or 'make rpm'."

####################################################################
# Compile
####################################################################

compile: 
	@echo "No compiling required, use either 'make install' or 'make rpm'."

####################################################################
# Install
####################################################################


install: installprefixset
	@echo installing ...
	@python setup.py  install  --root  $(prefix)


####################################################################
# Documentation
####################################################################

doc: man html

man: prepare

html: prepare

web: html

####################################################################
# Install Doc
####################################################################

install-doc: doc
	@echo installing  docs...

####################################################################
# Build Distribution
####################################################################

dist: prepare 
	python setup.py sdist


rpm: clean dist
	python setup.py bdist_rpm

clean::
	rm -f *~ etc/*~ doc/*~ src/*~ $(PACKAGE_NAME).src.tgz 
	rm -rf build 

