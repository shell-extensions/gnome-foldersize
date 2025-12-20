# Makefile für foldersize Übersetzungen

DOMAIN = foldersize
LOCALEDIR = locale
PACK_DIR ?= dist

LANGS = de en es

all: compile

compile:
	@for lang in $(LANGS); do \
	  echo "Compiling $$lang..."; \
	  msgfmt $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).po \
	    -o $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo; \
	done
	@echo "Fertig: Alle Übersetzungen kompiliert."

pack: compile
	@uuid=$$(python3 -c "import json; print(json.load(open('metadata.json', 'r', encoding='utf-8'))['uuid'])"); \
	mkdir -p "$(PACK_DIR)"; \
	glib-compile-schemas schemas; \
	zip -qr "$(PACK_DIR)/$$uuid.shell-extension.zip" . \
	  -x ".git/*" -x ".github/*" -x "$(PACK_DIR)/*" -x ".gitignore"; \
	echo "Created $(PACK_DIR)/$$uuid.shell-extension.zip"

clean:
	@for lang in $(LANGS); do \
	  rm -f $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo; \
	done
	@rm -f schemas/gschemas.compiled
	@echo "Aufgeräumt."
