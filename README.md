# Folder Size (GNOME Shell + Nautilus)

![Release](https://img.shields.io/github/v/release/shell-extensions/foldersize?sort=semver) ![GNOME Shell](https://img.shields.io/badge/GNOME%20Shell-45--48-4A86CF) ![Nautilus](https://img.shields.io/badge/Nautilus-Extension-4A86CF)

![Screenshot](image/Screenshot.png)

[English](README.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

Shows folder sizes in Nautilus list view and context menus, with optional Python hooks for Nemo and Caja. The GNOME Shell part manages the file manager hooks so they appear when the Shell extension is enabled and are removed when it is disabled.

## Requirements
- GNOME Shell 45–48
- Nautilus with nautilus-python support
- Nemo with nemo-python support (optional)
- Caja with caja-python support (optional)
- `du` available in PATH (coreutils)

## Installation (local user)
Recommended:
```
./install.sh
```
Defaults to a symlink for easy updates; use `./install.sh --copy` for a full copy.

Manual steps:
1) Copy this folder to `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.
2) Compile schemas: `glib-compile-schemas ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com/schemas`.
3) Restart GNOME Shell (Wayland: log out/in; X11: Alt+F2, `r`).
4) Enable: `gnome-extensions enable foldersize@pappmann.com` or use the Extensions app. Enabling creates the Nautilus symlink automatically.
5) Restart Nautilus to load the extension: `nautilus -q`.
6) Optional (Nemo/Caja): run `./install-hooks.sh` to install symlinks for `foldersize_nemo.py` and `foldersize_caja.py` (paths: `~/.local/share/nemo-python/extensions` and `~/.local/share/caja-python/extensions`).

## Disable and remove
Recommended:
```
./uninstall.sh
```
Use `--no-disable`, `--no-hooks`, `--no-remove`, or `--no-nautilus` to skip steps.

Manual steps:
- Disable in Extensions or with `gnome-extensions disable foldersize@pappmann.com`. This removes the Nautilus symlink and cleans matching `__pycache__` entries; restart Nautilus for it to unload.
- To uninstall fully: delete `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.
- Optional (Nemo/Caja): run `./uninstall-hooks.sh` to remove Python extension links.

## Translations
Run `make -C ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` to compile `.po` files into `.mo`.

## Updating
Replace the extension directory with the new version, re-run `glib-compile-schemas`, restart GNOME Shell, and restart Nautilus.

## Notes
- Settings are stored in GSettings schema `org.gnome.shell.extensions.foldersize`. Fallback config file: `~/.config/foldersize.conf`.
- If Nautilus still shows the old version after disable/enable, run `nautilus -q`.
