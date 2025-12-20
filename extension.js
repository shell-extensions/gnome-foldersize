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
const NEMO_EXT_DIR = GLib.build_filenamev([
    GLib.get_home_dir(),
    '.local',
    'share',
    'nemo-python',
    'extensions',
]);
const CAJA_EXT_DIR = GLib.build_filenamev([
    GLib.get_home_dir(),
    '.local',
    'share',
    'caja-python',
    'extensions',
]);
const PYTHON_FILENAMES = ['foldersize', 'folder_size', 'foldersize_nemo', 'foldersize_caja'];
const FILE_MANAGER_HOOKS = [
    {
        id: 'Nautilus',
        extDir: NAUTILUS_EXT_DIR,
        linkName: 'foldersize.py',
        targetName: 'foldersize.py',
    },
    {
        id: 'Nemo',
        extDir: NEMO_EXT_DIR,
        linkName: 'foldersize_nemo.py',
        targetName: 'foldersize_nemo.py',
    },
    {
        id: 'Caja',
        extDir: CAJA_EXT_DIR,
        linkName: 'foldersize_caja.py',
        targetName: 'foldersize_caja.py',
    },
];

export default class FolderSizeExtension extends Extension {
    enable() {
        this._installHooks();
    }

    disable() {
        this._removeHooks();
    }

    _installHooks() {
        for (const hook of FILE_MANAGER_HOOKS) {
            this._installHook(hook);
        }
    }

    _installHook({ id, extDir, linkName, targetName }) {
        try {
            GLib.mkdir_with_parents(extDir, 0o755);
        } catch (e) {
            logError(e, `FolderSize: Failed to create ${id} extension directory`);
            return;
        }

        const target = GLib.build_filenamev([this.path, targetName]);
        const linkPath = GLib.build_filenamev([extDir, linkName]);
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
            logError(e, `FolderSize: Failed to clean up existing ${id} link`);
        }

        try {
            linkFile.make_symbolic_link(target, null);
        } catch (e) {
            logError(e, `FolderSize: Failed to link ${id} extension`);
        }
    }

    _removeHooks() {
        for (const hook of FILE_MANAGER_HOOKS) {
            this._removeHook(hook);
        }
    }

    _removeHook({ id, extDir, linkName }) {
        const linkPath = GLib.build_filenamev([extDir, linkName]);
        const linkFile = Gio.File.new_for_path(linkPath);

        try {
            if (linkFile.query_exists(null)) {
                linkFile.delete(null);
            }
        } catch (e) {
            logError(e, `FolderSize: Failed to remove ${id} link`);
        }

        this._cleanupPyCache(extDir, id);
    }

    _cleanupPyCache(extDir, id) {
        const cacheDirPath = GLib.build_filenamev([extDir, '__pycache__']);
        const cacheDir = Gio.File.new_for_path(cacheDirPath);

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
            logError(e, `FolderSize: Failed to list ${id} pycache`);
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
                    logError(deleteError, `FolderSize: Failed to delete ${id} pycache ${name}`);
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
