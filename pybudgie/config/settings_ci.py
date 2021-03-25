from pybudgie.config.base import *

DEBUG = True
SECRET_KEY = "CIciCIciCIciCIciCI"
ALLOWED_HOSTS = [
    "*",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "ci.sqlite3",
    }
}
