# Folder Size (GNOME Shell + Nautilus)

![Release](https://img.shields.io/github/v/release/shell-extensions/foldersize?sort=semver)

Zeigt Ordnergroessen in der Nautilus Listenansicht und im Kontextmenue. Die GNOME-Shell-Erweiterung verwaltet den Nautilus-Python-Hook: beim Aktivieren wird der Symlink angelegt, beim Deaktivieren entfernt.

## Voraussetzungen
- GNOME Shell 45–48
- Nautilus mit nautilus-python
- `du` im PATH (coreutils)

## Installation (nur aktueller Benutzer)
1) Ordner nach `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` kopieren.
2) Schemas kompilieren: `glib-compile-schemas ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com/schemas`.
3) GNOME Shell neu starten (Wayland: ab- und anmelden; X11: Alt+F2, `r`).
4) Aktivieren: `gnome-extensions enable foldersize@pappmann.com` oder ueber die Extensions-App. Das legt den Nautilus-Symlink automatisch an.
5) Nautilus neu starten: `nautilus -q`.

## Deaktivieren und Entfernen
- Deaktivieren in Extensions oder mit `gnome-extensions disable foldersize@pappmann.com`. Dadurch wird der Nautilus-Symlink geloescht und passende `__pycache__`-Eintraege bereinigt; Nautilus danach neu starten.
- Vollstaendig entfernen: `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` loeschen.

## Uebersetzungen
`make -C ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` ausfuehren, um `.po` zu `.mo` zu kompilieren.

## Aktualisieren
Erweiterungsverzeichnis ersetzen, `glib-compile-schemas` erneut ausfuehren, GNOME Shell neu starten, Nautilus neu starten.

## Hinweise
- Einstellungen: GSettings Schema `org.gnome.shell.extensions.foldersize`, Fallback-Datei `~/.config/foldersize.conf`.
- Wenn Nautilus nach Deaktivierung noch aktiv ist: `nautilus -q`.
