#!/bin/sh
set -eu

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXTENSION_UUID="foldersize@pappmann.com"
EXTENSIONS_DIR="$HOME/.local/share/gnome-shell/extensions"
TARGET_DIR="$EXTENSIONS_DIR/$EXTENSION_UUID"

DO_DISABLE=1
DO_HOOKS=1
DO_NAUTILUS=1
DO_REMOVE=1

usage() {
    cat <<'EOF'
Usage: ./uninstall.sh [options]

Options:
  --no-disable   Skip disabling the GNOME Shell extension
  --no-hooks     Skip removing Nautilus/Nemo/Caja python hooks
  --no-nautilus  Skip restarting Nautilus
  --no-remove    Skip removing the extension directory
  -h, --help     Show this help
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --no-disable) DO_DISABLE=0 ;;
        --no-hooks) DO_HOOKS=0 ;;
        --no-nautilus) DO_NAUTILUS=0 ;;
        --no-remove) DO_REMOVE=0 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
    shift
done

if [ "$DO_DISABLE" -eq 1 ]; then
    if command -v gnome-extensions >/dev/null 2>&1; then
        if ! gnome-extensions disable "$EXTENSION_UUID"; then
            echo "Warning: could not disable extension; use Extensions app instead." >&2
        fi
    else
        echo "Warning: gnome-extensions not found; disable manually." >&2
    fi
fi

if [ "$DO_HOOKS" -eq 1 ]; then
    if [ -x "$BASE_DIR/uninstall-hooks.sh" ]; then
        "$BASE_DIR/uninstall-hooks.sh"
    else
        echo "Warning: uninstall-hooks.sh not found or not executable; skipping hooks." >&2
    fi
fi

if [ "$DO_REMOVE" -eq 1 ]; then
    if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
    elif [ -e "$TARGET_DIR" ]; then
        echo "Refusing to remove non-directory target: $TARGET_DIR" >&2
        exit 1
    fi
fi

if [ "$DO_NAUTILUS" -eq 1 ]; then
    if command -v nautilus >/dev/null 2>&1; then
        nautilus -q || true
    else
        echo "Warning: nautilus not found; restart your file manager manually." >&2
    fi
fi

echo "Done."
