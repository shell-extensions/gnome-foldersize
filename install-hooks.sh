#!/bin/sh
set -eu

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

install_hook() {
    ext_dir="$1"
    target="$2"
    link_name="$3"

    mkdir -p "$ext_dir"
    ln -sfn "$target" "$ext_dir/$link_name"
}

install_hook "$HOME/.local/share/nautilus-python/extensions" \
    "$BASE_DIR/foldersize.py" \
    "foldersize.py"

install_hook "$HOME/.local/share/nemo-python/extensions" \
    "$BASE_DIR/foldersize_nemo.py" \
    "foldersize_nemo.py"

install_hook "$HOME/.local/share/caja-python/extensions" \
    "$BASE_DIR/foldersize_caja.py" \
    "foldersize_caja.py"
