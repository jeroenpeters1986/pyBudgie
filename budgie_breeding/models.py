from django.db import models
from django.utils.translation import gettext_lazy as _

from budgie_bird.models import Bird
from budgie_user.models import BudgieUser


class BreedingSeason(models.Model):
    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    year = models.DateField(verbose_name=_("Year"))
    month = models.DateField(
        verbose_name=_("Starting month"),
        help_text=_(
            "This allows you to distinguish breeding rounds if you have multiple per year"
        ),
    )
    label = models.TextField(
        max_length=255,
        verbose_name=_("Label"),
        help_text=_("Optional label to find it quicker"),
        blank=True,
        null=True,
    )


class BreedingCouple(models.Model):
    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    season = models.ForeignKey(BreedingSeason, _("Breeding season"))
    male = models.ForeignKey(Bird, _("Male"))
    female = models.ForeignKey(Bird, _("Female"))
    start_date = models.DateField(verbose_name=_("Start date"), blank=True, null=True)
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))


class Egg(models.Model):
    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    couple = models.ForeignKey(BreedingCouple)
    date = models.DateField(verbose_name=_("Date found"))
    status = models.TextChoices(blank=True, null=True)
