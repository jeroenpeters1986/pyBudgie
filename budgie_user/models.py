from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class BudgieUser(AbstractUser):
    breeding_reg_nr = models.CharField(
        max_length=20, blank=True, verbose_name=_("Breeding registration number")
    )
    notes = models.TextField(
        max_length=500, blank=True, verbose_name=_("Remarks / Notes")
    )
