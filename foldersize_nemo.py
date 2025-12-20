import os
import sys

# Nemo loads this entry point; keep it minimal and defer logic to modules.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MODULE_DIR = os.path.join(BASE_DIR, "foldersize")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from nemo import FolderSize

__all__ = ["FolderSize"]
