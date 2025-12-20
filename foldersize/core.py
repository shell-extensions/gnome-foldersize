import gi
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import GLib, Gio
import subprocess, threading, time, os, gettext, locale, configparser, logging
from collections import deque, OrderedDict

# Basisverzeichnis der Erweiterung (Repo-Root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOCALE_DIR = os.path.join(BASE_DIR, "locale")

# ===========================
# Logging Setup
# ===========================

logger = logging.getLogger('foldersize-extension')
logger.setLevel(logging.WARNING)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[FolderSize] %(levelname)s: %(message)s'))
    logger.addHandler(handler)

# ===========================
# Konfigurations-Parameter
# ===========================

MAX_CACHE_SIZE = 1000  # Maximum number of cached folder sizes

CONFIG_PATH = os.path.expanduser("~/.config/foldersize.conf")

DEFAULT_CONFIG = {
    "cache_ttl": "3600",
    "max_workers": "10",
    "du_timeout": "1800",
    "skip_mountpoints": "true",
    "queue_timeout": "300",
    "rotate_interval": "10",
    "long_job_threshold": "300",
    "decimal_places": "1",
    "binary_units": "true",
    "auto_scan": "true",
}

def _as_bool(val, default):
    if val is None:
        return default
    s = str(val).strip().lower()
    if s in ("1", "true", "yes", "on"):
        return True
    if s in ("0", "false", "no", "off"):
        return False
    return default

def _get_gsettings():
    try:
        schema_dir = os.path.join(BASE_DIR, "schemas")
        schema_source = Gio.SettingsSchemaSource.new_from_directory(
            schema_dir,
            Gio.SettingsSchemaSource.get_default(),
            False
        )
        schema = schema_source.lookup("org.gnome.shell.extensions.foldersize", True)
        if not schema:
            logger.info("GSettings schema not found, falling back to INI config")
            return None
        return Gio.Settings.new_full(schema, None, None)
    except (OSError, GLib.Error) as e:
        logger.warning(f"Failed to load GSettings: {e}")
        return None

def _load_config():
    # Vorrang: GSettings, danach Fallback auf INI-Datei
    gs = _get_gsettings()
    if gs:
        return {
            "cache_ttl": gs.get_int("cache-ttl"),
            "max_workers": gs.get_int("max-workers"),
            "du_timeout": gs.get_int("du-timeout"),
            "skip_mountpoints": gs.get_boolean("skip-mountpoints"),
            "queue_timeout": gs.get_int("queue-timeout"),
            "rotate_interval": gs.get_int("rotate-interval"),
            "long_job_threshold": gs.get_int("long-job-threshold"),
            "decimal_places": gs.get_int("decimal-places"),
            "binary_units": gs.get_boolean("binary-units"),
            "auto_scan": gs.get_boolean("auto-scan"),
            "gsettings": gs,
        }

    cfg = configparser.ConfigParser()
    cfg.read_dict({"FolderSize": DEFAULT_CONFIG})
    if os.path.exists(CONFIG_PATH):
        try:
            cfg.read(CONFIG_PATH)
        except (OSError, configparser.Error) as e:
            logger.warning(f"Failed to read config file {CONFIG_PATH}: {e}")
    section = cfg["FolderSize"]
    return {
        "cache_ttl": int(section.get("cache_ttl", DEFAULT_CONFIG["cache_ttl"])),
        "max_workers": int(section.get("max_workers", DEFAULT_CONFIG["max_workers"])),
        "du_timeout": int(section.get("du_timeout", DEFAULT_CONFIG["du_timeout"])),
        "skip_mountpoints": _as_bool(section.get("skip_mountpoints"), True),
        "queue_timeout": int(section.get("queue_timeout", DEFAULT_CONFIG["queue_timeout"])),
        "rotate_interval": int(section.get("rotate_interval", DEFAULT_CONFIG["rotate_interval"])),
        "long_job_threshold": int(section.get("long_job_threshold", DEFAULT_CONFIG["long_job_threshold"])),
        "decimal_places": int(section.get("decimal_places", DEFAULT_CONFIG["decimal_places"])),
        "binary_units": _as_bool(section.get("binary_units"), True),
        "auto_scan": _as_bool(section.get("auto_scan"), True),
        "gsettings": None,
    }

CFG = _load_config()

GSETTINGS = CFG.get("gsettings")

CACHE_TTL         = CFG["cache_ttl"]
MAX_WORKERS       = CFG["max_workers"]
DU_TIMEOUT        = CFG["du_timeout"]
QUEUE_STUCK_AFTER = CFG["queue_timeout"]
ROTATE_INTERVAL   = CFG["rotate_interval"]
LONG_JOB_AFTER    = CFG["long_job_threshold"]
DEC_PLACES        = CFG["decimal_places"]
BINARY_UNITS      = CFG["binary_units"]

# du-Argumente abhängig davon, ob Mountpoints übersprungen werden sollen
if CFG["skip_mountpoints"]:
    DU_ARGS_PRIMARY = ['du', '-sb', '-x']   # stay on filesystem, bytes, summary
    DU_ARGS_FALLBACK = ['du', '-sb']        # fallback if -x unsupported
else:
    DU_ARGS_PRIMARY = ['du', '-sb']
    DU_ARGS_FALLBACK = ['du', '-sb']

# ===========================
# i18n (gettext)
# ===========================

DOMAIN = "foldersize"  # passt zu foldersize.po / foldersize.mo

env_lang = (
    os.environ.get("LANGUAGE")
    or os.environ.get("LC_ALL")
    or os.environ.get("LC_MESSAGES")
    or os.environ.get("LANG")
)

languages = []
if env_lang:
    primary = env_lang.split(":")[0]
    primary = primary.split(".")[0]
    languages.append(primary)
    if "_" in primary:
        languages.append(primary.split("_")[0])

if not env_lang:
    try:
        default_locale = locale.getdefaultlocale()
    except Exception:
        default_locale = (None, None)
    if default_locale and default_locale[0]:
        primary = default_locale[0].split(".")[0]
        languages.append(primary)
        if "_" in primary:
            languages.append(primary.split("_")[0])

languages.append("en")

t = gettext.translation(DOMAIN, LOCALE_DIR, languages=languages, fallback=True)
_ = t.gettext

# ===========================

# Symbole (erst nach i18n, damit übersetzbare Teile lokalisiert werden können)
ICON_ACTIVE    = "↻"                 # aktiv laufend
ICON_WAITING   = "⏱"                 # in Queue, wartet
ICON_RECALC    = "↻"                 # manueller Recalc
ICON_ERROR     = _("⚠️ Error")
ICON_TIMEOUT   = _("⏰ Timeout")
ICON_DISABLED  = "⏻"                 # Scan deaktiviert Hinweis

# Rotations-Symbole bei langen Jobs
ROTATE_SYMBOLS  = ["⏳", "⌛", "🔄"]
SORT_WIDTH      = 20      # Stellen für die Bytezahl, damit Stringsortierung numerisch korrekt ist
DIGIT_MAP = {             # Unsichtbare Zeichen, die nach Codepoint aufsteigend sortieren
    "0": "\u200B",  # zero width space
    "1": "\u200C",  # zero width non-joiner
    "2": "\u200D",  # zero width joiner
    "3": "\u2060",  # word joiner
    "4": "\u2061",  # function application
    "5": "\u2062",  # invisible times
    "6": "\u2063",  # invisible separator
    "7": "\u2064",  # invisible plus
    "8": "\u206A",  # inhibit symmetric swapping
    "9": "\u206B",  # activate symmetric swapping
}

# ===========================
# Helper Functions
# ===========================

def _update_file_attribute(file_info, attribute, value):
    """Helper function for GLib.idle_add to update file attributes."""
    try:
        file_info.add_string_attribute(attribute, value)
    except Exception as e:
        logger.warning(f"Failed to update file attribute: {e}")
    return False  # Don't repeat


class FolderSizeCore:

    _queue = deque()
    _queue_condition = threading.Condition()  # For worker notification
    _cache_lock = threading.Lock()            # Protects _cache
    _queue_lock = threading.Lock()            # Protects _queue
    _file_refs_lock = threading.Lock()        # Protects _file_refs

    _workers_started = False
    _scan_enabled = CFG["auto_scan"]
    _cache = OrderedDict()  # LRU cache: { path: (timestamp, size, running, process, queued, start_time) }
    _file_refs = {}         # { path: file info object }

    def __init__(self):
        if not FolderSizeCore._workers_started:
            for _ in range(MAX_WORKERS):
                t = threading.Thread(target=self._worker_loop, daemon=True)
                t.start()
            FolderSizeCore._workers_started = True

        GLib.timeout_add_seconds(ROTATE_INTERVAL, self._rotate_symbols)

    def _evict_cache_if_needed(self):
        """Remove oldest cache entries if cache size exceeds limit (LRU)."""
        # Caller must hold _cache_lock
        while len(FolderSizeCore._cache) > MAX_CACHE_SIZE:
            try:
                oldest_path, _ = FolderSizeCore._cache.popitem(last=False)
                logger.debug(f"Evicted cache entry: {oldest_path}")
            except KeyError:
                break

    def update_file_info(self, file):
        if not file.is_directory():
            return
        gfile = file.get_location()
        if not gfile:
            return
        path = gfile.get_path()
        if not path:
            return

        if not FolderSizeCore._scan_enabled:
            display = self._disabled_display(path)
            with FolderSizeCore._file_refs_lock:
                FolderSizeCore._file_refs[path] = file
            with FolderSizeCore._cache_lock:
                if path not in FolderSizeCore._cache:
                    FolderSizeCore._cache[path] = (time.time(), "", False, None, False, None)
                    self._evict_cache_if_needed()
            file.add_string_attribute('folder_size', display)
            return

        now = time.time()
        needs_enqueue = False
        display_value = ICON_WAITING

        with FolderSizeCore._cache_lock:
            if path in FolderSizeCore._cache:
                # Move to end for LRU
                FolderSizeCore._cache.move_to_end(path)
                ts, size, running, proc, queued, start_time = FolderSizeCore._cache[path]

                if running:
                    display_value = size if size in ROTATE_SYMBOLS else ICON_ACTIVE
                elif queued:
                    display_value = ICON_WAITING
                elif size and (now - ts) < CACHE_TTL:
                    display_value = size
                else:
                    # Wert fehlt oder ist veraltet -> neu einreihen
                    del FolderSizeCore._cache[path]
                    needs_enqueue = True
            else:
                needs_enqueue = True

        file.add_string_attribute('folder_size', display_value)

        if needs_enqueue:
            self._enqueue_job(path, file, priority=False)

    def _enqueue_job(self, path, file, priority=False, force=False, override_disabled=False):
        if not FolderSizeCore._scan_enabled and not override_disabled:
            # Keine neuen Jobs, stattdessen Disabled-Indikator setzen
            with FolderSizeCore._cache_lock:
                FolderSizeCore._cache[path] = (time.time(), "", False, None, False, None)
                self._evict_cache_if_needed()
            if file:
                GLib.idle_add(_update_file_attribute, file, 'folder_size', self._disabled_display(path))
            return

        # Handle force: terminate running process if any
        if force:
            with FolderSizeCore._cache_lock:
                if path in FolderSizeCore._cache:
                    ts, size, running, proc, queued, st = FolderSizeCore._cache[path]
                    if running and proc and proc.poll() is None:
                        try:
                            proc.terminate()
                            time.sleep(0.1)
                            if proc.poll() is None:
                                proc.kill()
                        except Exception as e:
                            logger.warning(f"Failed to terminate process for {path}: {e}")

        with FolderSizeCore._cache_lock:
            FolderSizeCore._cache[path] = (time.time(), "", False, None, True, None)
            self._evict_cache_if_needed()

        if file:
            with FolderSizeCore._file_refs_lock:
                FolderSizeCore._file_refs[path] = file

        # Add to queue and notify workers
        with FolderSizeCore._queue_condition:
            with FolderSizeCore._queue_lock:
                if priority:
                    FolderSizeCore._queue.appendleft((path, file))
                else:
                    FolderSizeCore._queue.append((path, file))
            FolderSizeCore._queue_condition.notify()

    def _worker_loop(self):
        while True:
            # Wait for queue items with condition variable
            with FolderSizeCore._queue_condition:
                while True:
                    with FolderSizeCore._queue_lock:
                        if FolderSizeCore._queue:
                            path, file = FolderSizeCore._queue.popleft()
                            break
                    # Wait for notification
                    FolderSizeCore._queue_condition.wait(timeout=1.0)

            start_time = time.time()
            with FolderSizeCore._cache_lock:
                FolderSizeCore._cache[path] = (start_time, "", True, None, False, start_time)

            proc = None
            size = ICON_ERROR
            try:
                args_to_use = DU_ARGS_PRIMARY
                tried_fallback = False
                while True:
                    try:
                        proc = subprocess.Popen(
                            args_to_use + ['--', path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL
                        )
                    except (OSError, ValueError) as e:
                        logger.error(f"Failed to start subprocess for {path}: {e}")
                        size = ICON_ERROR
                        break

                    with FolderSizeCore._cache_lock:
                        FolderSizeCore._cache[path] = (start_time, ICON_ACTIVE, True, proc, False, start_time)

                    try:
                        out, _ = proc.communicate(timeout=DU_TIMEOUT)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        logger.warning(f"du timeout for {path}")
                        size = ICON_TIMEOUT
                        break

                    if proc.returncode == 0:
                        try:
                            size_bytes = int(out.split()[0].decode('utf-8'))
                            size = self._format_size(size_bytes)
                        except (ValueError, IndexError, UnicodeDecodeError) as e:
                            logger.error(f"Failed to parse du output for {path}: {e}")
                            size = ICON_ERROR
                        break

                    if tried_fallback:
                        logger.warning(f"du failed for {path} with both primary and fallback args")
                        size = ICON_ERROR
                        break

                    args_to_use = DU_ARGS_FALLBACK
                    tried_fallback = True

            except Exception as e:
                logger.error(f"Unexpected error in worker for {path}: {e}")
                size = ICON_ERROR

            # Update cache with result
            with FolderSizeCore._cache_lock:
                FolderSizeCore._cache[path] = (time.time(), size, False, None, False, None)

            # Update UI
            target_file = file
            if not target_file:
                with FolderSizeCore._file_refs_lock:
                    target_file = FolderSizeCore._file_refs.get(path)
                    FolderSizeCore._file_refs.pop(path, None)

            if target_file:
                GLib.idle_add(_update_file_attribute, target_file, 'folder_size', size)

    def _rotate_symbols(self):
        now = time.time()
        stuck_jobs = []  # Jobs that need re-queuing

        with FolderSizeCore._cache_lock:
            for path, (ts, size, running, proc, queued, start_time) in list(FolderSizeCore._cache.items()):
                if running and start_time and (now - start_time) > LONG_JOB_AFTER:
                    if size in ROTATE_SYMBOLS:
                        idx = ROTATE_SYMBOLS.index(size)
                    else:
                        idx = 0
                    new_symbol = ROTATE_SYMBOLS[(idx + 1) % len(ROTATE_SYMBOLS)]
                    FolderSizeCore._cache[path] = (ts, new_symbol, running, proc, queued, start_time)

                # Falls Jobs zu lange in Queue hängen, erneut einreihen
                if queued and (now - ts) > QUEUE_STUCK_AFTER:
                    FolderSizeCore._cache[path] = (time.time(), "", False, None, True, None)
                    stuck_jobs.append(path)

        # Re-queue stuck jobs outside of lock to avoid deadlock
        if stuck_jobs:
            with FolderSizeCore._file_refs_lock:
                for path in stuck_jobs:
                    ref_file = FolderSizeCore._file_refs.get(path)
                    with FolderSizeCore._queue_condition:
                        with FolderSizeCore._queue_lock:
                            FolderSizeCore._queue.appendleft((path, ref_file))
                        FolderSizeCore._queue_condition.notify()

        return True

    def _stop_all_jobs(self):
        # Queue leeren
        with FolderSizeCore._queue_lock:
            FolderSizeCore._queue.clear()

        # Laufende Prozesse abbrechen
        with FolderSizeCore._cache_lock:
            for path, (ts, size, running, proc, queued, start_time) in list(FolderSizeCore._cache.items()):
                if running and proc and proc.poll() is None:
                    try:
                        proc.terminate()
                        time.sleep(0.1)
                        if proc.poll() is None:
                            proc.kill()
                    except Exception as e:
                        logger.warning(f"Failed to stop process for {path}: {e}")
                FolderSizeCore._cache[path] = (ts, size, False, None, False, start_time)

    def _queue_pending_scans(self):
        now = time.time()
        pending = []

        with FolderSizeCore._cache_lock:
            for path, (ts, size, running, proc, queued, start_time) in list(FolderSizeCore._cache.items()):
                if running or queued:
                    continue
                if not size or (now - ts) >= CACHE_TTL:
                    pending.append(path)

        for path in pending:
            with FolderSizeCore._file_refs_lock:
                ref_file = FolderSizeCore._file_refs.get(path)
            if not ref_file:
                continue
            GLib.idle_add(_update_file_attribute, ref_file, 'folder_size', ICON_WAITING)
            self._enqueue_job(path, ref_file, priority=False)

    def _is_mountpoint(self, path):
        if not CFG["skip_mountpoints"]:
            return False
        try:
            st_path = os.stat(path)
            parent = os.path.dirname(path) or path
            st_parent = os.stat(parent)
            return st_path.st_dev != st_parent.st_dev
        except (OSError, ValueError) as e:
            logger.debug(f"Failed to check if {path} is mountpoint: {e}")
            return False

    def _hidden_prefix(self, size_bytes):
        prefix = f"{size_bytes:0{SORT_WIDTH}d}"
        return "".join(DIGIT_MAP.get(ch, ch) for ch in prefix)

    def _toggle_scan(self, *_args):
        FolderSizeCore._scan_enabled = not FolderSizeCore._scan_enabled
        if GSETTINGS:
            try:
                GSETTINGS.set_boolean("auto-scan", FolderSizeCore._scan_enabled)
            except Exception as e:
                logger.warning(f"Failed to save auto-scan setting: {e}")
        if not FolderSizeCore._scan_enabled:
            self._stop_all_jobs()
        else:
            self._queue_pending_scans()

    def _disabled_display(self, path):
        with FolderSizeCore._cache_lock:
            cached = FolderSizeCore._cache.get(path)
            if cached:
                _, size, running, proc, queued, start_time = cached
                if size:
                    if size.endswith(ICON_DISABLED):
                        return size
                    return f"{size}{ICON_DISABLED}"
        return f"{self._hidden_prefix(0)}{ICON_DISABLED}"

    def _format_size(self, size_bytes):
        try:
            size = float(size_bytes)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to format size {size_bytes}: {e}")
            return ICON_ERROR

        if BINARY_UNITS:
            units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
            step = 1024.0
        else:
            units = ["B", "kB", "MB", "GB", "TB", "PB"]
            step = 1000.0
        unit_idx = 0
        while size >= step and unit_idx < len(units) - 1:
            size /= step
            unit_idx += 1

        human = f"{size:.{DEC_PLACES}f}".rstrip("0").rstrip(".") + units[unit_idx]
        return f"{self._hidden_prefix(int(size_bytes))}{human}"

    # ========= Menu callbacks =========

    def _recalc_selected(self, _menu, dir_files):
        """
        Wird nur mit Verzeichnissen aufgerufen.
        """
        for f in dir_files:
            gfile = f.get_location()
            if not gfile:
                continue
            path = gfile.get_path()
            if not path:
                continue

            # UI-Symbol setzen
            f.add_string_attribute('folder_size', ICON_RECALC)
            # Job mit Priorität starten
            self._enqueue_job(path, f, priority=True, force=True, override_disabled=True)
