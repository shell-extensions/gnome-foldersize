import gi
gi.require_version('Nemo', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import Nemo, GObject

from core import FolderSizeCore, _


class FolderSize(GObject.GObject,
                 Nemo.ColumnProvider,
                 Nemo.InfoProvider,
                 Nemo.MenuProvider,
                 FolderSizeCore):

    def __init__(self):
        GObject.GObject.__init__(self)
        FolderSizeCore.__init__(self)

    def get_columns(self):
        return [Nemo.Column(
            name="FolderSize::size",
            attribute="folder_size",
            label=_("Folder size"),
            description=_("Async folder size calculation with cache, queue and status icons")
        )]

    def get_file_items(self, *args):
        if not args:
            return []

        files = args[0] if len(args) == 1 else args[1]

        dir_files = []
        for f in files:
            try:
                if f.is_directory():
                    dir_files.append(f)
            except Exception:
                continue

        items = []

        if dir_files:
            label = (_("Recalculate folder size")
                     if len(dir_files) == 1
                     else _("Recalculate folder sizes"))

            item = Nemo.MenuItem(
                name="FolderSize::Recalc",
                label=label,
                tip=_("Abort running calculation and start immediately (priority)")
            )
            item.connect("activate", self._recalc_selected, dir_files)
            items.append(item)

        toggle_label = (_("Disable folder size scanning")
                        if self._scan_enabled
                        else _("Enable folder size scanning"))
        toggle_item = Nemo.MenuItem(
            name="FolderSize::ToggleScan",
            label=toggle_label,
            tip=_("Toggle automatic folder size calculation")
        )
        toggle_item.connect("activate", self._toggle_scan)
        items.append(toggle_item)

        return items

    def get_background_items(self, *args):
        toggle_label = (_("Disable folder size scanning")
                        if self._scan_enabled
                        else _("Enable folder size scanning"))
        toggle_item = Nemo.MenuItem(
            name="FolderSize::ToggleScanBackground",
            label=toggle_label,
            tip=_("Toggle automatic folder size calculation")
        )
        toggle_item.connect("activate", self._toggle_scan)
        return [toggle_item]
