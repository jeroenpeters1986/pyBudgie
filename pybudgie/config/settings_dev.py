from pybudgie.config.base import *

DEBUG = True
SECRET_KEY = "develop"
ALLOWED_HOSTS = [
    "*",
]
X_FRAME_OPTIONS = "sameorigin"


DEFAULT_FILE_STORAGE = "storages.backends.sftpstorage.SFTPStorage"
SFTP_STORAGE_HOST = "web0083.zxcs.nl"
SFTP_STORAGE_ROOT = "/home/uwvogelcdn/public_html"
SFTP_STORAGE_INTERACTIVE = False
SFTP_STORAGE_PARAMS = {
    "username": "uwvogelcdn",
    "port": 7685,
}
MEDIA_URL = "https://cdn.uwvogels.nl/"


# #ddev-generated code to import DDEV settings
import os

if os.environ.get("IS_DDEV_PROJECT") == "true":
    from pathlib import Path
    import importlib.util
    import sys

    s = Path("/mnt/ddev_config/settings/settings.ddev.py")
    if s.is_file():
        spec = importlib.util.spec_from_file_location("ddev_settings", s)
        ddev_settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ddev_settings)

        # Get the current module to set attributes
        current_module = sys.modules[__name__]

        # Add or update attributes from the ddev_settings module
        for name, value in vars(ddev_settings).items():
            if not name.startswith("__"):  # Exclude special attributes
                setattr(current_module, name, value)
# End DDEV-generated code
