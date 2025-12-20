#!/bin/sh
set -eu

remove_link() {
    link_path="$1"
    if [ -L "$link_path" ]; then
        rm "$link_path"
    fi
}

remove_link "$HOME/.local/share/nautilus-python/extensions/foldersize.py"
remove_link "$HOME/.local/share/nemo-python/extensions/foldersize_nemo.py"
remove_link "$HOME/.local/share/caja-python/extensions/foldersize_caja.py"
