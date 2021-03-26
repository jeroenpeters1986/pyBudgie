from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgieBirdConfig(AppConfig):
    name = "budgie_bird"
    verbose_name = _("Bird Administration")
