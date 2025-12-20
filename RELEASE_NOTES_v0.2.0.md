# Release Notes v0.2.0

## Summary
- Fix: enabling folder-size scanning now queues pending scans immediately.

## Changes
- When scanning is disabled, visible folders are tracked for later.
- Re-enabling scans queues missing or stale items and updates the UI to waiting.

## Testing
- [ ] Enable scan from Nautilus context menu and observe new jobs.
- [ ] Disable scan and confirm running jobs stop.
