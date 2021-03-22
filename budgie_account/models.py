from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

    
class BudgieUser(AbstractUser):
    breeding_reg_nr = models.CharField(max_length=20, blank=True,
                                       verbose_name=_('Breeding registration number'))
    notes = models.TextField(max_length=500, blank=True,
                             verbose_name=_('Remarks / Notes'))


class Account(models.Model):
    name = models.CharField(max_length=120, verbose_name=_('Account name'),
                            help_text=_('Typically, this could be the surname'
                                        'of the client'))
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.SET_NULL)
