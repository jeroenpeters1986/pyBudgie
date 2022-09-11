from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from budgie_bird.models import Bird
from budgie_user.models import BudgieUser


class BreedingSeason(models.Model):
    """Represents a breeding season (with starting points)"""

    class Month(models.TextChoices):
        """Months"""

        JAN = 1, _("January")
        FEB = 2, _("February")
        MAR = 3, _("March")
        APR = 4, _("April")
        MAY = 5, _("May")
        JUN = 6, _("June")
        JUL = 7, _("July")
        AUG = 8, _("August")
        SEP = 9, _("September")
        OCT = 10, _("October")
        NOV = 11, _("November")
        DEC = 12, _("December")

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    starting_year = models.IntegerField(
        verbose_name=_("Starting year"),
        default=2022,
        validators=[MaxValueValidator(2100), MinValueValidator(2000)],
    )
    starting_month = models.CharField(
        verbose_name=_("Starting month"),
        max_length=15,
        choices=Month.choices,
        default=Month.JAN,
        blank=False,
        null=False,
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

    class Meta:
        ordering = ["-starting_year", "-starting_month"]
        verbose_name = _("Breeding season")
        verbose_name_plural = _("Breeding seasons")

    def __str__(self):
        return "{} {}, {} {}".format(
            _("Breeding round"),
            self.starting_year,
            self.Month.labels[int(self.starting_month) - 1],
            "({})".format(self.label) if self.label else "",
        )


class BreedingCouple(models.Model):
    """Represents two bird who are a breeding couple together"""

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    season = models.ForeignKey(
        BreedingSeason, verbose_name=_("Breeding season"), on_delete=models.CASCADE
    )
    male = models.ForeignKey(
        Bird,
        verbose_name=_("Male"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="male",
        limit_choices_to={"gender": Bird.Gender.MALE},
    )
    female = models.ForeignKey(
        Bird,
        verbose_name=_("Female"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="female",
        limit_choices_to={"gender": Bird.Gender.FEMALE},
    )
    start_date = models.DateField(verbose_name=_("Start date"), blank=True, null=True)
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))

    def __str__(self):
        return "{}".format(
            _("Breeding couple; M: {}, F: {}").format(self.male, self.female)
        )

    class Meta:
        verbose_name = _("Breeding couple")
        verbose_name_plural = _("Breeding couples")


class Egg(models.Model):
    """Represents an egg laid in a breeding season by a breeding couple of birds"""

    class Status(models.TextChoices):
        """Gender of the bird"""

        FERTILIZED = "fertilized", _("Fertilized")
        UNFERTILIZED = "unfertilized", _("Unfertilized")
        DIED_OFF = "died_off", _("Died off")
        BROKEN = "broken", _("Broken")

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    couple = models.ForeignKey(
        BreedingCouple, on_delete=models.CASCADE, verbose_name=_("Breeding couple")
    )
    date = models.DateField(verbose_name=_("Date found"))
    status = models.CharField(
        choices=Status.choices,
        max_length=15,
        default=Status.UNFERTILIZED,
        blank=False,
        null=False,
        verbose_name=_("Status"),
    )

    def __str__(self):
        return "{} #{}".format(_("Egg"), self.id)

    class Meta:
        verbose_name = _("Egg")
        verbose_name_plural = _("Eggs")
