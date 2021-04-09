from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgieUserConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = "budgie_user"
    verbose_name = _("PyBudgie User Administration")
