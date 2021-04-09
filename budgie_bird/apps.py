from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgieBirdConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "budgie_bird"
    verbose_name = _("Bird Administration")
