# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.


PREFIX ?= /usr
BIN ?= /bin
DATA ?= /share
BINDIR ?= $(PREFIX)$(BIN)
DATADIR ?= $(PREFIX)$(DATA)
LICENSEDIR ?= $(DATADIR)/licenses
LOCALEDIR ?= $(DATADIR)/locale
ICONDIR ?= $(DATADIR)/icons

SHEBANG ?= /usr/bin/env python2
COMMAND ?= blueshift-tray
PKGNAME ?= blueshift-tray

ICONS = blueshift blueshift-on blueshift-off


.PHONY: all
all: command shell

.PHONY: command
command: bin/blueshift-tray

.PHONY: shell
shell: bash zsh fish

.PHONY: bash
bash: bin/blueshift-tray.bash

.PHONY: zsh
zsh: bin/blueshift-tray.zsh

.PHONY: fish
fish: bin/blueshift-tray.fish


bin/blueshift-tray: src/blueshift-tray.py
	@mkdir -p bin
	cp $< $@
	sed -i '/^LOCALEDIR *= /s#^.*$$#LOCALEDIR = '\''$(LOCALEDIR)'\''#' $@
	sed -i 's:^#!/usr/bin/env python2$$:#!$(SHEBANG):' $@

bin/blueshift-tray.bash: src/completion
	@mkdir -p bin
	auto-auto-complete bash --output $@ --source $<

bin/blueshift-tray.zsh: src/completion
	@mkdir -p bin
	auto-auto-complete zsh --output $@ --source $<

bin/blueshift-tray.fish: src/completion
	@mkdir -p bin
	auto-auto-complete fish --output $@ --source $<


.PHONY: install
install: install-base install-shell

.PHONY: install-base
install-base: install-command install-license

.PHONY: install-command
install-command: bin/blueshift-tray $(foreach I,$(ICONS),icons/$(I).svg)
	install -dm755 -- "$(DESTDIR)$(BINDIR)"
	install -m755 bin/blueshift-tray -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	install -dm755 -- "$(DESTDIR)$(ICONDIR)/hicolor/scalable/apps"
	install -m644 $(foreach I,$(ICONS),icons/$(I).svg) -- "$(DESTDIR)$(ICONDIR)/hicolor/scalable/apps"

.PHONY: install-license
install-license:
	install -dm755 -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	install -m644 COPYING LICENSE -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"

.PHONY: install-shell
install-shell: install-bash install-zsh install-fish

.PHONY: install-bash
install-bash: bin/blueshift-tray.bash
	install -dm755 -- "$(DESTDIR)$(DATADIR)/bash-completion/completions"
	install -m644 $< -- "$(DESTDIR)$(DATADIR)/bash-completion/completions/$(COMMAND)"

.PHONY: install-zsh
install-zsh: bin/blueshift-tray.zsh
	install -dm755 -- "$(DESTDIR)$(DATADIR)/zsh/site-functions"
	install -m644 $< -- "$(DESTDIR)$(DATADIR)/zsh/site-functions/_$(COMMAND)"

.PHONY: install-fish
install-fish: bin/blueshift-tray.fish
	install -dm755 -- "$(DESTDIR)$(DATADIR)/fish/completions"
	install -m644 $< -- "$(DESTDIR)$(DATADIR)/fish/completions/$(COMMAND).fish"


.PHONY: uninstall
uninstall:
	-rm -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	-rm -- $(foreach I,$(ICONS),"$(DESTDIR)$(ICONDIR)/hicolor/scalable/apps/$(I).svg")
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	-rm -- "$(DESTDIR)$(DATADIR)/fish/completions/$(COMMAND).fish"
	-rmdir -- "$(DESTDIR)$(DATADIR)/fish/completions"
	-rmdir -- "$(DESTDIR)$(DATADIR)/fish"
	-rm -- "$(DESTDIR)$(DATADIR)/zsh/site-functions/_$(COMMAND)"
	-rmdir -- "$(DESTDIR)$(DATADIR)/zsh/site-functions"
	-rmdir -- "$(DESTDIR)$(DATADIR)/zsh"
	-rm -- "$(DESTDIR)$(DATADIR)/bash-completion/completions/$(COMMAND)"
	-rmdir -- "$(DESTDIR)$(DATADIR)/bash-completion/completions"
	-rmdir -- "$(DESTDIR)$(DATADIR)/bash-completion"


.PHONY: all
clean:
	-rm -r bin

