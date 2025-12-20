#!/bin/sh
set -eu

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXTENSION_UUID="foldersize@pappmann.com"
EXTENSIONS_DIR="$HOME/.local/share/gnome-shell/extensions"
TARGET_DIR="$EXTENSIONS_DIR/$EXTENSION_UUID"

DO_COPY=0
DO_HOOKS=1
DO_ENABLE=1
DO_NAUTILUS=1
DO_SCHEMAS=1

usage() {
    cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --copy         Copy files instead of creating a symlink
  --no-hooks     Skip installing Nautilus/Nemo/Caja python hooks
  --no-enable    Skip enabling the GNOME Shell extension
  --no-nautilus  Skip restarting Nautilus
  --no-schemas   Skip compiling GSettings schemas
  -h, --help     Show this help
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --copy) DO_COPY=1 ;;
        --no-hooks) DO_HOOKS=0 ;;
        --no-enable) DO_ENABLE=0 ;;
        --no-nautilus) DO_NAUTILUS=0 ;;
        --no-schemas) DO_SCHEMAS=0 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
    shift
done

mkdir -p "$EXTENSIONS_DIR"

if [ -e "$TARGET_DIR" ] || [ -L "$TARGET_DIR" ]; then
    if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
    else
        echo "Refusing to replace non-directory target: $TARGET_DIR" >&2
        exit 1
    fi
fi

if [ "$DO_COPY" -eq 1 ]; then
    cp -a "$BASE_DIR" "$TARGET_DIR"
else
    ln -sfn "$BASE_DIR" "$TARGET_DIR"
fi

if [ "$DO_SCHEMAS" -eq 1 ]; then
    if command -v glib-compile-schemas >/dev/null 2>&1; then
        glib-compile-schemas "$TARGET_DIR/schemas"
    else
        echo "Warning: glib-compile-schemas not found; skipping schema compile." >&2
    fi
fi

if [ "$DO_ENABLE" -eq 1 ]; then
    if command -v gnome-extensions >/dev/null 2>&1; then
        if ! gnome-extensions enable "$EXTENSION_UUID"; then
            echo "Warning: could not enable extension; use Extensions app instead." >&2
        fi
    else
        echo "Warning: gnome-extensions not found; enable manually." >&2
    fi
fi

if [ "$DO_HOOKS" -eq 1 ]; then
    if [ -x "$BASE_DIR/install-hooks.sh" ]; then
        "$BASE_DIR/install-hooks.sh"
    else
        echo "Warning: install-hooks.sh not found or not executable; skipping hooks." >&2
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
if [ "${XDG_SESSION_TYPE:-}" = "x11" ]; then
    echo "Restart GNOME Shell: Alt+F2, r, Enter"
else
    echo "Restart GNOME Shell: log out and back in"
fi
