# Release Notes v0.3.0

## Summary
- Add Nemo and Caja hooks plus unified install/uninstall helpers.

## Changes
- Refactor Python entry points into a shared module with Nautilus/Nemo/Caja adapters.
- GNOME Shell extension now manages hooks for Nautilus, Nemo, and Caja.
- Add `install.sh` and `uninstall.sh` for local setup and cleanup.

## Testing
- [ ] Run `./install.sh` and verify schemas compile and extension enables.
- [ ] In Nautilus, confirm folder sizes appear and context menu works.
- [ ] In Nemo/Caja, confirm hooks load if installed (optional).
