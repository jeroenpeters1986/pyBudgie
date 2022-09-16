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
