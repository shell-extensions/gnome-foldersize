import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';
import Gio from 'gi://Gio';
import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

const SCHEMA_ID = 'org.gnome.shell.extensions.foldersize';

export default class FolderSizePrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const _ = this.gettext.bind(this);
        const settings = this.getSettings(SCHEMA_ID);

        const page = new Adw.PreferencesPage();
        window.add(page);

        const generalGroup = new Adw.PreferencesGroup({ title: _('General') });
        page.add(generalGroup);

        generalGroup.add(this._spinRow(settings, _('Cache TTL (s)'), 'cache-ttl', 60, 86400, 60));
        generalGroup.add(this._spinRow(settings, _('Max workers'), 'max-workers', 1, 64, 1));
        generalGroup.add(this._spinRow(settings, _('du timeout (s)'), 'du-timeout', 30, 7200, 30));
        generalGroup.add(this._spinRow(settings, _('Queue timeout (s)'), 'queue-timeout', 60, 7200, 30));

        const displayGroup = new Adw.PreferencesGroup({ title: _('Display') });
        page.add(displayGroup);

        displayGroup.add(this._spinRow(settings, _('Decimal places'), 'decimal-places', 0, 3, 1));
        displayGroup.add(this._switchRow(settings, _('Binary units (KiB/MiB)'), 'binary-units'));

        const behaviorGroup = new Adw.PreferencesGroup({ title: _('Behavior') });
        page.add(behaviorGroup);

        behaviorGroup.add(this._switchRow(settings, _('Auto scan'), 'auto-scan'));
        behaviorGroup.add(this._switchRow(settings, _('Skip other mountpoints'), 'skip-mountpoints'));
        behaviorGroup.add(this._spinRow(settings, _('Rotate interval (s)'), 'rotate-interval', 2, 60, 1));
        behaviorGroup.add(this._spinRow(settings, _('Long job threshold (s)'), 'long-job-threshold', 10, 3600, 10));

        window.set_default_size(520, 560);
    }

    _switchRow(settings, label, key) {
        const row = new Adw.ActionRow({ title: label });
        const sw = new Gtk.Switch({
            active: settings.get_boolean(key),
            valign: Gtk.Align.CENTER,
        });
        settings.bind(key, sw, 'active', Gio.SettingsBindFlags.DEFAULT);
        row.add_suffix(sw);
        row.activatable_widget = sw;
        return row;
    }

    _spinRow(settings, label, key, min, max, step) {
        const row = new Adw.ActionRow({ title: label });
        const adj = new Gtk.Adjustment({
            lower: min,
            upper: max,
            step_increment: step,
            page_increment: step * 2,
            value: settings.get_int(key),
        });
        const spin = new Gtk.SpinButton({
            adjustment: adj,
            digits: 0,
            valign: Gtk.Align.CENTER,
        });
        settings.bind(key, adj, 'value', Gio.SettingsBindFlags.DEFAULT);
        row.add_suffix(spin);
        row.activatable_widget = spin;
        return row;
    }
}
