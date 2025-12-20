# TODO (Folder Size)

## Implementation approach
Unify file manager integrations behind a shared core, then add Nemo and Caja adapters that use the same size computation and caching logic. Keep per-file-manager entry points small and focused on hooking into their APIs, while the core remains free of UI/toolkit specifics. Restructure the repository so each integration has its own module plus shared utilities, install scripts, and packaging metadata.

## TODO
1) Document target versions and extension APIs for Nemo and Caja.
2) Define the new module layout (core/, nautilus/, nemo/, caja/, shared/, install/).
3) Extract size computation, caching, and formatting into core/.
4) Migrate Nautilus integration to the new structure.
5) Implement Nemo integration (list view and context menu, hook lifecycle).
6) Implement Caja integration (list view and context menu, hook lifecycle).
7) Update build/install scripts for all three file managers.
8) Refresh README files with new installation paths and screenshots.
