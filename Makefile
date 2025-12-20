# Makefile für foldersize Übersetzungen

DOMAIN = foldersize
LOCALEDIR = locale

LANGS = de en es

all: compile

compile:
	@for lang in $(LANGS); do \
	  echo "Compiling $$lang..."; \
	  msgfmt $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).po \
	    -o $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo; \
	done
	@echo "Fertig: Alle Übersetzungen kompiliert."

clean:
	@for lang in $(LANGS); do \
	  rm -f $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo; \
	done
	@echo "Aufgeräumt."
