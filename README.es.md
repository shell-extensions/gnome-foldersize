# Folder Size (GNOME Shell + Nautilus)

![Release](https://img.shields.io/github/v/release/shell-extensions/foldersize?sort=semver) ![GNOME Shell](https://img.shields.io/badge/GNOME%20Shell-45--48-4A86CF) ![Nautilus](https://img.shields.io/badge/Nautilus-Extension-4A86CF)

![Screenshot](image/Screenshot.png)

[English](README.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

Muestra el tamano de carpetas en la vista de lista y menus de Nautilus, con hooks de Python opcionales para Nemo y Caja. La parte de GNOME Shell administra los hooks: al activar crea los symlinks y al desactivar los elimina.

## Requisitos
- GNOME Shell 45–48
- Nautilus con nautilus-python
- Nemo con nemo-python (opcional)
- Caja con caja-python (opcional)
- `du` en PATH (coreutils)

## Instalacion (usuario actual)
Recomendado:
```
./install.sh
```
Por defecto usa un symlink; para copiar usa `./install.sh --copy`.

Pasos manuales:
1) Copiar la carpeta a `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.
2) Compilar esquemas: `glib-compile-schemas ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com/schemas`.
3) Reiniciar GNOME Shell (Wayland: cerrar sesion; X11: Alt+F2, `r`).
4) Activar: `gnome-extensions enable foldersize@pappmann.com` o usar la app Extensions. Al activar se crea el symlink de Nautilus de forma automatica.
5) Reiniciar Nautilus: `nautilus -q`.
6) Opcional (Nemo/Caja): ejecutar `./install-hooks.sh` para instalar symlinks de `foldersize_nemo.py` y `foldersize_caja.py` (rutas: `~/.local/share/nemo-python/extensions` y `~/.local/share/caja-python/extensions`).

## Desactivar y eliminar
Recomendado:
```
./uninstall.sh
```
Usa `--no-disable`, `--no-hooks`, `--no-remove` o `--no-nautilus` para omitir pasos.

Pasos manuales:
- Desactivar en Extensions o con `gnome-extensions disable foldersize@pappmann.com`. Esto borra el symlink de Nautilus y limpia `__pycache__`; reiniciar Nautilus para descargarlo.
- Para desinstalar: eliminar `~/.local/share/gnome-shell/extensions/foldersize@pappmann.com`.
- Opcional (Nemo/Caja): ejecutar `./uninstall-hooks.sh` para quitar los links de la extension de Python.

## Traducciones
Ejecutar `make -C ~/.local/share/gnome-shell/extensions/foldersize@pappmann.com` para compilar `.po` a `.mo`.

## Actualizacion
Reemplazar el directorio, ejecutar `glib-compile-schemas`, reiniciar GNOME Shell y Nautilus.

## Notas
- Ajustes en el esquema GSettings `org.gnome.shell.extensions.foldersize`. Fallback: `~/.config/foldersize.conf`.
- Si Nautilus sigue mostrando la extension tras desactivarla, ejecutar `nautilus -q`.
