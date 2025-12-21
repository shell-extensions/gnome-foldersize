import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as QuickSettings from 'resource:///org/gnome/shell/ui/quickSettings.js';
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
const QS_TOGGLE_ICON = 'folder-symbolic';

const FolderSizeQuickSettings = GObject.registerClass(
class FolderSizeQuickSettings extends QuickSettings.SystemIndicator {
    _init(settings, toggleLabel) {
        super._init();

        this._settings = settings;
        this._indicator = this._addIndicator();
        this._indicator.icon_name = QS_TOGGLE_ICON;

        this._toggle = new QuickSettings.QuickToggle({
            title: toggleLabel || 'Folder Size: Auto scan',
            iconName: QS_TOGGLE_ICON,
            toggleMode: true,
        });

        this._settings.bind(
            'auto-scan',
            this._toggle,
            'checked',
            Gio.SettingsBindFlags.DEFAULT,
        );
        this._settings.bind(
            'auto-scan',
            this._indicator,
            'visible',
            Gio.SettingsBindFlags.DEFAULT,
        );

        this.quickSettingsItems.push(this._toggle);
    }

    destroy() {
        this.quickSettingsItems.forEach(item => {
            if (item?.destroy)
                item.destroy();
        });

        super.destroy();
    }
});

export default class FolderSizeExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        this._indicator = null;
        this._settings = null;
        this._settingsSignals = [];
    }

    enable() {
        this._installNautilusHook();
        this._settings = this.getSettings();
        this._settingsSignals = [
            this._settings.connect('changed::show-quick-settings', () => {
                this._syncQuickSettings();
            }),
        ];
        this._syncQuickSettings();
    }

    disable() {
        if (this._settings) {
            this._settingsSignals.forEach(id => this._settings.disconnect(id));
        }
        this._settingsSignals = [];
        this._removeQuickSettings();
        this._settings = null;
        this._removeNautilusHook();
    }

    _syncQuickSettings() {
        if (!this._settings) {
            return;
        }

        const shouldShow = this._settings.get_boolean('show-quick-settings');

        if (shouldShow) {
            if (!this._indicator) {
                const toggleLabel = this.gettext('Folder Size: Auto scan');
                this._indicator = new FolderSizeQuickSettings(this._settings, toggleLabel);
                Main.panel.statusArea.quickSettings.addExternalIndicator(this._indicator);
            }
            return;
        }

        this._removeQuickSettings();
    }

    _removeQuickSettings() {
        if (!this._indicator) {
            return;
        }

        const qs = Main.panel?.statusArea?.quickSettings;
        if (qs?.removeExternalIndicator)
            qs.removeExternalIndicator(this._indicator);

        this._indicator.destroy();
        this._indicator = null;
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
