from django.db import models
from django.utils.translation import gettext_lazy as _

from budgie_user.models import BudgieUser


class Bird(models.Model):
    """ Respresentation of a bird and all its characteristics/properties """

    class Sex(models.TextChoices):
        """ Sex of the bird """

        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    class Color(models.TextChoices):
        """ The colors of the birds, defined by the category number on the 'Vraagprogramma' """

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

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    ring_number = models.CharField(
        max_length=20,
        blank=False,
        unique=True,
        verbose_name=_("Ring number"),
        help_text=_(
            "This is to uniquely identify the bird and to determine its breeder"
        ),
    )
    sex = models.CharField(
        choices=Sex.choices,
        max_length=6,
        blank=False,
        null=False,
        verbose_name=_("Sex"),
    )
    color = models.CharField(
        choices=Color.choices,
        max_length=15,
        blank=False,
        null=False,
        verbose_name=_("Color"),
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
    photo = models.ImageField(default="bird_pics/default.jpg", upload_to="bird_pics")

    class Meta:
        ordering = ["ring_number"]

    def __str__(self):
        return self.ring_number

    #
    # def image_tag(self):
    #     return mark_safe('<img src="/directory/{}}" width="150" height="150" />'.format(
    #     self.photo))
    #
    # image_tag.short_description = 'Image'


class Breeder(models.Model):
    """ Breeder (contacts) model """

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
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

    def __str__(self):
        """ Represent a breed with his name and regnumber """
        return "{} {} ({})".format(
            self.first_name, self.last_name, self.breeding_reg_nr
        )


class ColorProperty(models.Model):
    """Color properties, which include a rank of importance,
    for when the items should be displayed"""

    color_name = models.CharField(
        max_length=100, blank=False, verbose_name=_("Colorproperty name")
    )
    rank = models.IntegerField(
        verbose_name=_("Matter of importance"),
        help_text=_("1 is very important, 1000 is " "not important"),
    )

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        """ Use the color name as the field representation"""
        return self.color_name
