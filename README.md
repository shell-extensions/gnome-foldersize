# Folder Size (GNOME Shell + Nautilus)

![Release](https://img.shields.io/github/v/release/shell-extensions/foldersize?sort=semver) ![GNOME Shell](https://img.shields.io/badge/GNOME%20Shell-45--48-4A86CF) ![Nautilus](https://img.shields.io/badge/Nautilus-Extension-4A86CF)

![Screenshot](image/Screenshot.png)

[English](README.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

Shows folder sizes in Nautilus list view and context menus. The GNOME Shell part manages the Nautilus Python hook so the file manager extension appears when the Shell extension is enabled and is removed when it is disabled.

## Requirements
- GNOME Shell 45–48
- Nautilus with nautilus-python support
- `du` available in PATH (coreutils)

## Installation (local user)
1) Copy this folder to `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.
2) Compile schemas: `glib-compile-schemas ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com/schemas`.
3) Restart GNOME Shell (Wayland: log out/in; X11: Alt+F2, `r`).
4) Enable: `gnome-extensions enable foldersize@pappmann.com` or use the Extensions app. Enabling creates the Nautilus symlink automatically.
5) Restart Nautilus to load the extension: `nautilus -q`.

## Disable and remove
- Disable in Extensions or with `gnome-extensions disable foldersize@pappmann.com`. This removes the Nautilus symlink and cleans matching `__pycache__` entries; restart Nautilus for it to unload.
- To uninstall fully: delete `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.

## Translations
Run `make -C ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` to compile `.po` files into `.mo`.

## Updating
Replace the extension directory with the new version, re-run `glib-compile-schemas`, restart GNOME Shell, and restart Nautilus.

## Notes
- Settings are stored in GSettings schema `org.gnome.shell.extensions.foldersize`. Fallback config file: `~/.config/foldersize.conf`.
- If Nautilus still shows the old version after disable/enable, run `nautilus -q`.
