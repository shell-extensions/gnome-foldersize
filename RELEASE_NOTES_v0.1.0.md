# Release Notes v0.1.0

## Summary
- Initial public release of the Folder Size GNOME Shell + Nautilus extension.

## Features
- Show folder sizes in Nautilus list view and context menu.
- GNOME Shell extension manages the Nautilus Python hook (symlink creation/removal).
- Async size calculation to keep the UI responsive.
- Translations: DE/EN/ES.

## Requirements
- GNOME Shell 45–48
- Nautilus with nautilus-python
- `du` available in PATH (coreutils)

## Install Notes
- Run `glib-compile-schemas` after copying the extension directory.
- Run `make` to regenerate translations after modifying `.po` files.
