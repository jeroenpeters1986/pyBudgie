from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgieBreedingConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "budgie_breeding"
    verbose_name = _("Breeding administration")
