# Folder Size (GNOME Shell + Nautilus)

![Release](https://img.shields.io/github/v/release/shell-extensions/foldersize?sort=semver) ![GNOME Shell](https://img.shields.io/badge/GNOME%20Shell-45--48-4A86CF) ![Nautilus](https://img.shields.io/badge/Nautilus-Extension-4A86CF)

![Screenshot](image/Screenshot.png)
![Schnelleinstellungen-Menue](image/Screenshot_extension.png)

[English](README.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

Zeigt Ordnergrößen in der Nautilus-Listenansicht und im Kontextmenü. Die GNOME-Shell-Erweiterung verwaltet den Nautilus-Python-Hook: beim Aktivieren wird der Symlink angelegt, beim Deaktivieren entfernt.

## Voraussetzungen
- GNOME Shell 45–48
- Nautilus mit nautilus-python
- `du` im PATH (coreutils)

## Installation (nur aktueller Benutzer)
1) Ordner nach `~/.local/share/gnome-shell/extensions/foldersize@yurij.de` kopieren.
2) Schemas kompilieren: `glib-compile-schemas ~/.local/share/gnome-shell/extensions/foldersize@yurij.de/schemas`.
3) GNOME Shell neu starten (Wayland: ab- und anmelden; X11: Alt+F2, `r`).
4) Aktivieren: `gnome-extensions enable foldersize@yurij.de` oder über die Extensions-App. Das legt den Nautilus-Symlink automatisch an.
5) Nautilus neu starten: `nautilus -q`.

## Deaktivieren und Entfernen
- Deaktivieren in Extensions oder mit `gnome-extensions disable foldersize@yurij.de`. Dadurch wird der Nautilus-Symlink gelöscht und passende `__pycache__`-Einträge bereinigt; Nautilus danach neu starten.
- Vollständig entfernen: `~/.local/share/gnome-shell/extensions/foldersize@yurij.de` löschen.

## Übersetzungen
`make -C ~/.local/share/gnome-shell/extensions/foldersize@yurij.de` ausführen, um `.po` zu `.mo` zu kompilieren.

## Aktualisieren
Erweiterungsverzeichnis ersetzen, `glib-compile-schemas` erneut ausführen, GNOME Shell neu starten, Nautilus neu starten.

## Hinweise
- Einstellungen: GSettings Schema `org.gnome.shell.extensions.foldersize`, Fallback-Datei `~/.config/foldersize.conf`.
- Der Quick-Settings-Schalter kann in den Einstellungen (Schnelleinstellungen-Schalter anzeigen) ausgeblendet werden.
- Wenn Nautilus nach Deaktivierung noch aktiv ist: `nautilus -q`.
