import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

const NAUTILUS_EXT_DIR = GLib.build_filenamev([
    GLib.get_home_dir(),
    '.local',
    'share',
    'nautilus-python',
    'extensions',
]);
const NAUTILUS_LINK_NAME = 'foldersize.py';
const PYTHON_FILENAMES = ['foldersize', 'folder_size'];
const PY_CACHE_DIR = GLib.build_filenamev([NAUTILUS_EXT_DIR, '__pycache__']);

export default class FolderSizeExtension extends Extension {
    enable() {
        this._installNautilusHook();
    }

    disable() {
        this._removeNautilusHook();
    }

    _installNautilusHook() {
        try {
            GLib.mkdir_with_parents(NAUTILUS_EXT_DIR, 0o755);
        } catch (e) {
            logError(e, 'FolderSize: Failed to create Nautilus extension directory');
            return;
        }

        const target = GLib.build_filenamev([this.path, NAUTILUS_LINK_NAME]);
        const linkPath = GLib.build_filenamev([NAUTILUS_EXT_DIR, NAUTILUS_LINK_NAME]);
        const linkFile = Gio.File.new_for_path(linkPath);

        try {
            if (linkFile.query_exists(null)) {
                const info = linkFile.query_info(
                    'standard::type,standard::symlink-target',
                    Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
                    null
                );

                const isSymlink = info.get_file_type() === Gio.FileType.SYMBOLIC_LINK;
                const isSameTarget = info.get_symlink_target() === target;

                if (isSymlink && isSameTarget) {
                    return;
                }

                linkFile.delete(null);
            }
        } catch (e) {
            logError(e, 'FolderSize: Failed to clean up existing Nautilus link');
        }

        try {
            linkFile.make_symbolic_link(target, null);
        } catch (e) {
            logError(e, 'FolderSize: Failed to link Nautilus extension');
        }
    }

    _removeNautilusHook() {
        const linkPath = GLib.build_filenamev([NAUTILUS_EXT_DIR, NAUTILUS_LINK_NAME]);
        const linkFile = Gio.File.new_for_path(linkPath);

        try {
            if (linkFile.query_exists(null)) {
                linkFile.delete(null);
            }
        } catch (e) {
            logError(e, 'FolderSize: Failed to remove Nautilus link');
        }

        this._cleanupPyCache();
    }

    _cleanupPyCache() {
        const cacheDir = Gio.File.new_for_path(PY_CACHE_DIR);

        if (!cacheDir.query_exists(null)) {
            return;
        }

        let enumerator;

        try {
            enumerator = cacheDir.enumerate_children(
                'standard::name',
                Gio.FileQueryInfoFlags.NONE,
                null
            );
        } catch (e) {
            logError(e, 'FolderSize: Failed to list Nautilus pycache');
            return;
        }

        try {
            let info;

            while ((info = enumerator.next_file(null)) !== null) {
                const name = info.get_name();
                const matchesPrefix = PYTHON_FILENAMES.some((prefix) => name.startsWith(prefix));

                if (!matchesPrefix) {
                    continue;
                }

                try {
                    cacheDir.get_child(name).delete(null);
                } catch (deleteError) {
                    logError(deleteError, `FolderSize: Failed to delete pycache ${name}`);
                }
            }
        } finally {
            try {
                enumerator.close(null);
            } catch (e) {
                // ignore close errors
            }
        }
    }
}
