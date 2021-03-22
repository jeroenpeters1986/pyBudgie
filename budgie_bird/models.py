from django.db import models
from django.utils.translation import gettext_lazy as _

from budgie_account.models import Account


class Bird(models.Model):
    class Sex(models.TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    class Color(models.TextChoices):
        LIGHT_GREEN = "18.001.001", _("Light Green")
        D_GREEN = "18.002.001", _("Dark Green")
        DD_GREEN = "18.002.002", _("Olive Green")
        GREY_GREEN = "18.002.003", _("Grey Green")
        VIOLET_GREEN = "18.002.004", _("Violet Green")
        BLUE = "18.004.001", _("Sky Blue")
        D_BLUE = "18.004.002", _("Mauve")
        DD_BLUE = "18.004.003", _("Gray")
        GREY_BLUE = "18.004.004", _("Violet Blue")
        VIOLET_BLUE = "18.004.005", _("Violet Blue")

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    ring_number = models.CharField(
        max_length=20,
        blank=False,
        unique=True,
        verbose_name=_("Ring number to identify the bird"),
    )
    sex = models.CharField(
        choices=Sex.choices,
        max_length=6,
        blank=False,
        null=False,
        verbose_name=_("Sex of the bird"),
    )
    color = models.CharField(
        choices=Color.choices,
        max_length=15,
        blank=False,
        null=False,
        verbose_name=_("Color of the bird"),
    )
    color_property = models.ManyToManyField(
        "ColorProperty",
        related_name="color_properties",
        verbose_name=_("Color properties"),
    )
    split_property = models.ManyToManyField(
        "ColorProperty",
        related_name="split_properties",
        verbose_name=_("Split properties"),
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name=_("Date of birth")
    )
    date_of_death = models.DateField(
        null=True, blank=True, verbose_name=_("Date of death")
    )
    father = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        verbose_name=_("Father"),
        on_delete=models.SET_NULL,
        related_name="ancestor_father",
    )
    mother = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        verbose_name=_("Mother"),
        on_delete=models.SET_NULL,
        related_name="ancestor_mother",
    )
    breeder = models.ForeignKey(
        "Breeder", null=True, on_delete=models.SET_NULL, related_name="breeder"
    )
    owner = models.ForeignKey(
        "Breeder", null=True, on_delete=models.SET_NULL, related_name="owner"
    )
    is_owned = models.BooleanField(default=False, verbose_name=_("I own this bird"))
    is_for_sale = models.BooleanField(
        default=False, verbose_name=_("This bird is for sale")
    )
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))
    photo = models.ImageField()


class Breeder(models.Model):

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=60, verbose_name=_("First name"))
    last_name = models.CharField(max_length=60, verbose_name=_("Last name"))
    breeding_reg_nr = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("Breeding registration number"),
    )
    address = models.TextField(blank=True, null=True, verbose_name=_("Home address"))
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Phone number")
    )
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))


class ColorProperty(models.Model):
    color_name = models.CharField(
        max_length=100, blank=False, verbose_name=_("Colorproperty name")
    )
    rank = models.IntegerField(
        verbose_name=_("Matter of importance"),
        help_text=_("1 is very important, 1000 is " "not important"),
    )
