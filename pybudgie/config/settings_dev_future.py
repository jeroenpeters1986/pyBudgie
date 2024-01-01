from pybudgie.config.base import *

DEBUG = True
SECRET_KEY = "develop"
ALLOWED_HOSTS = [
    "*",
]
X_FRAME_OPTIONS = "sameorigin"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "pybudgie__app",
        "USER": "root",
        "PASSWORD": "jeroen",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "web0083.zxcs.nl",
            "root_path": "/home/uwvogelcdn/public_html",
            "interactive": False,
            "params": {
                "hostname": "web0083.zxcs.nl",
                "username": "uwvogelcdn",
                "port": 7685,
            },
            "base_url": "https://cdn.uwvogels.nl/",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = "https://cdn.uwvogels.nl/"
# Set the static root to the media root


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
