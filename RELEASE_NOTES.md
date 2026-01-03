# Release Notes

## v0.3.1

### Summary
- Move the Quick Settings toggle visibility control out of the Nautilus menu and into Preferences.
- Change the extension UUID to `foldersize@yurij.de`.

### Changes
- Remove the "Show/Hide Folder Size Quick Settings toggle" items from Nautilus context menus.
- Use Preferences > Behavior (Show Quick Settings toggle) to show or hide the Quick Settings toggle.
- Update the extension UUID and install paths to `foldersize@yurij.de`.

### Testing
- [ ] Right-click folders/background in Nautilus and confirm no Quick Settings toggle item appears.
- [ ] Open Preferences > Behavior and toggle "Show Quick Settings toggle" to show/hide it in GNOME Shell.

## v0.3.0

### Summary
- Add a preferences UI and Quick Settings controls for folder-size scanning.

### Changes
- New Preferences window to tune cache TTL, worker limits, timeouts, and display format (decimal places, binary units).
- Settings now persist in the GSettings schema `org.gnome.shell.extensions.foldersize`, with fallback to `~/.config/foldersize.conf`.
- Quick Settings auto-scan toggle can be shown or hidden from Preferences or the Nautilus extension menu.

### Testing
- [ ] Open Preferences, adjust cache/worker/unit settings, and confirm size display updates.
- [ ] Toggle auto-scan in Quick Settings and confirm list view updates.
- [ ] Show/hide the Quick Settings toggle from Nautilus and confirm it appears or disappears.

## v0.2.0

### Summary
- Fix: enabling folder-size scanning now queues pending scans immediately.

### Changes
- When scanning is disabled, visible folders are tracked for later.
- Re-enabling scans queues missing or stale items and updates the UI to waiting.

### Testing
- [ ] Enable scan from Nautilus context menu and observe new jobs.
- [ ] Disable scan and confirm running jobs stop.

## v0.1.0

### Summary
- Initial public release of the Folder Size GNOME Shell + Nautilus extension.

### Features
- Show folder sizes in Nautilus list view and context menu.
- GNOME Shell extension manages the Nautilus Python hook (symlink creation/removal).
- Async size calculation to keep the UI responsive.
- Translations: DE/EN/ES.

### Requirements
- GNOME Shell 45-48
- Nautilus with nautilus-python
- `du` available in PATH (coreutils)

### Install Notes
- Run `glib-compile-schemas` after copying the extension directory.
- Run `make` to regenerate translations after modifying `.po` files.
