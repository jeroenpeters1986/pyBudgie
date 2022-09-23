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

DEFAULT_FILE_STORAGE = "storages.backends.sftpstorage.SFTPStorage"
SFTP_STORAGE_HOST = "web0083.zxcs.nl"
SFTP_STORAGE_ROOT = "/home/uwvogelcdn/public_html"
SFTP_STORAGE_INTERACTIVE = False
SFTP_STORAGE_PARAMS = {
    "username": "uwvogelcdn",
    "port": 7685,
}
MEDIA_URL = "https://cdn.uwvogels.nl/"
