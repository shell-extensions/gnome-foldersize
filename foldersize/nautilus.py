import gi
gi.require_version('Nautilus', '4.0')
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import Nautilus, GObject

from core import FolderSizeCore, _


class FolderSize(GObject.GObject,
                 Nautilus.ColumnProvider,
                 Nautilus.InfoProvider,
                 Nautilus.MenuProvider,
                 FolderSizeCore):

    def __init__(self):
        GObject.GObject.__init__(self)
        FolderSizeCore.__init__(self)

    def get_columns(self):
        return [Nautilus.Column(
            name="FolderSize::size",
            attribute="folder_size",
            label=_("Folder size"),
            description=_("Async folder size calculation with cache, queue and status icons")
        )]

    def get_file_items(self, *args):
        """
        Show context menu entry only when at least one folder is selected.
        Files are ignored.
        """
        if not args:
            return []

        # Nautilus passes either files or (window, files)
        files = args[0] if len(args) == 1 else args[1]

        # Filter only directories
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

            item = Nautilus.MenuItem(
                name="FolderSize::Recalc",
                label=label,
                tip=_("Abort running calculation and start immediately (priority)")
            )
            item.connect("activate", self._recalc_selected, dir_files)
            items.append(item)

        toggle_label = (_("Disable folder size scanning")
                        if self._scan_enabled
                        else _("Enable folder size scanning"))
        toggle_item = Nautilus.MenuItem(
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
        toggle_item = Nautilus.MenuItem(
            name="FolderSize::ToggleScanBackground",
            label=toggle_label,
            tip=_("Toggle automatic folder size calculation")
        )
        toggle_item.connect("activate", self._toggle_scan)
        return [toggle_item]
