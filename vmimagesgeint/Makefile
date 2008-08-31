
PACKAGE_NAME=vmimagesgeint
####################################################################
# Distribution Makefile
####################################################################

.PHONY: configure install clean

all: configure

####################################################################
# Prepare
####################################################################

prepare:
	rm -f *~
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

install: 
	@echo installing ...
	@mkdir -p $(prefix)/sbin
	@mkdir -p $(prefix)/share/doc/$(PACKAGE_NAME)/
	@install -m 0755 vsi_s_prolog.sh $(prefix)/sbin
	@install -m 0755 vsi_s_starter.sh $(prefix)/sbin
	@install -m 0755 vsi_s_epilog.sh $(prefix)/sbin
	@install -m 0755 vsi_v_start.sh $(prefix)/sbin
	@install -m 0755 vsi_v_stop.sh $(prefix)/sbin
	@install -m 0644 README $(prefix)/share/doc/$(PACKAGE_NAME)/

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
	@mkdir -p build
	@tar --gzip --exclude='*CVS*' -cf build/$(PACKAGE_NAME).src.tgz *

rpm: dist
	@rpmbuild -ta build/$(PACKAGE_NAME).src.tgz 

clean:
	rm -f *~ test/*~ etc/*~ doc/*~ src/*~ build/$(PACKAGE_NAME).src.tgz 
	rm -rf build 

