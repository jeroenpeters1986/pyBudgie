import json

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from budgie_user.models import BudgieUser


class Bird(models.Model):
    """Representation of a bird and all its characteristics/properties"""

    class Gender(models.TextChoices):
        """Gender of the bird"""

        UNKNOWN = "unknown", _("Unknown")
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    class Color(models.TextChoices):
        """
        The colors of the birds,
        defined by the category number on the 'Vraagprogramma'
        """

        LIGHT_GREEN = "18.001.001", _("Light Green")
        D_GREEN = "18.002.001", _("Dark Green")
        DD_GREEN = "18.002.002", _("Olive Green")
        GREY_GREEN = "18.002.003", _("Grey Green")
        VIOLET_GREEN = "18.002.004", _("Violet Green")
        BLUE = "18.004.001", _("Sky Blue")
        COBALT_BLUE = "18.004.002", _("Cobalt Blue")
        D_BLUE = "18.004.003", _("Mauve")
        DD_BLUE = "18.004.004", _("Gray")
        VIOLET_BLUE = "18.004.005", _("Violet Blue")
        UNKNOWN = "00.000.000", _("Unknown")

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    ring_number = models.CharField(
        max_length=40,
        blank=False,
        verbose_name=_("Ring number"),
        help_text=_(
            "This is to uniquely identify the bird and to determine its breeder"
        ),
    )
    gender = models.CharField(
        choices=Gender.choices,
        max_length=10,
        default=Gender.UNKNOWN,
        blank=False,
        null=False,
        verbose_name=_("Gender"),
    )
    color = models.CharField(
        choices=Color.choices,
        max_length=15,
        blank=True,
        verbose_name=_("Color"),
    )
    color_property = models.ManyToManyField(
        "ColorProperty",
        blank=True,
        related_name="color_properties",
        verbose_name=_("Color properties"),
    )
    split_property = models.ManyToManyField(
        "ColorProperty",
        blank=True,
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
        verbose_name=_("father").capitalize(),
        on_delete=models.SET_NULL,
        related_name="ancestor_father",
        limit_choices_to=Q(gender=Gender.MALE) | Q(gender=Gender.UNKNOWN),
    )
    mother = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        verbose_name=_("mother").capitalize(),
        on_delete=models.SET_NULL,
        related_name="ancestor_mother",
        limit_choices_to=Q(gender=Gender.FEMALE) | Q(gender=Gender.UNKNOWN),
    )
    breeder = models.ForeignKey(
        "Breeder",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="breeder",
    )
    owner = models.ForeignKey(
        "Breeder",
        blank=True,
        null=True,
        verbose_name=_("Owner"),
        on_delete=models.SET_NULL,
        related_name="owner",
    )
    is_owned = models.BooleanField(
        default=False,
        verbose_name=_("I own this bird"),
        help_text=_(
            "Sometimes when you are the owner, the bird is not at your disposal due to a trade"
        ),
    )
    is_for_sale = models.BooleanField(
        default=False, verbose_name=_("This bird is for sale")
    )
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))
    photo = models.ImageField(
        default=settings.BIRD_PICTURE_DEFAULT,
        upload_to=settings.BIRD_PICTURE_UPLOAD_LOCATION,
    )

    class Meta:
        ordering = ["ring_number"]
        unique_together = [["user", "ring_number"]]
        verbose_name = _("Bird")
        verbose_name_plural = _("Birds")

    def __str__(self):
        return self.ring_number

    def color_props(self):
        return " ".join(
            x.color_name for x in self.color_property.all().order_by("rank")
        )

    def split_props(self):
        return " ".join(
            x.color_name for x in self.split_property.all().order_by("rank")
        )

    def characteristic_values(self):
        return self.characteristic_selections.select_related("characteristic").order_by(
            "characteristic__name"
        )

    def characteristic_display(self):
        return [
            "{}: {}".format(value.characteristic.name, value.selected_description)
            for value in self.characteristic_values()
        ]

    def descriptive_color(self):
        return "{props} {color} {sep} {split}".format(
            props=self.color_props(),
            color=self.get_color_display(),
            sep="/" if self.split_props() else "",
            split=self.split_props(),
        ).strip()

    def get_ancestors(self):
        """Recursive method to return the family tree"""
        ancestors = {}
        tree = {
            "bird": self,
            "ancestors": {
                "father": self.father.get_ancestors() if self.father else None,
                "mother": self.mother.get_ancestors() if self.mother else None,
            },
        }
        ancestors.update(tree)
        return ancestors

    def family_tree_for_inbreed(self):
        def _get_tree(bird):
            if bird is None:
                return None

            tree = {"name": bird.ring_number}
            if bird.father:
                tree.update({"s": _get_tree(bird.father)})
            if bird.mother:
                tree.update({"d": _get_tree(bird.mother)})
            return tree

        return json.dumps(_get_tree(self))


class BirdPhoto(models.Model):
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE, related_name="birdphotos")
    notes = models.CharField(max_length=255, blank=True, verbose_name=_("Notes"))
    image = models.ImageField(
        default=settings.BIRD_PICTURE_DEFAULT,
        upload_to=settings.BIRD_PICTURE_UPLOAD_LOCATION,
    )
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["uploaded_at"]
        verbose_name = _("Additional bird photo")
        verbose_name_plural = _("Additional bird photos")


class BirdCharacteristic(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    description_0 = models.CharField(
        max_length=255, verbose_name=_("Description for level 0")
    )
    description_1 = models.CharField(
        max_length=255, verbose_name=_("Description for level 1")
    )
    description_2 = models.CharField(
        max_length=255, verbose_name=_("Description for level 2")
    )
    description_3 = models.CharField(
        max_length=255, verbose_name=_("Description for level 3")
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Bird characteristic")
        verbose_name_plural = _("Bird characteristics")

    def __str__(self):
        return self.name

    def description_for_level(self, level):
        return getattr(self, f"description_{level}")


class BirdCharacteristicSelection(models.Model):
    bird = models.ForeignKey(
        Bird, on_delete=models.CASCADE, related_name="characteristic_selections"
    )
    characteristic = models.ForeignKey(
        BirdCharacteristic,
        on_delete=models.CASCADE,
        related_name="bird_selections",
        verbose_name=_("Characteristic"),
    )
    selected_grade = models.PositiveSmallIntegerField(
        choices=[(level, str(level)) for level in range(4)],
        verbose_name=_("Selected grade"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bird", "characteristic"],
                name="unique_bird_characteristic",
            )
        ]
        verbose_name = _("Bird characteristic selection")
        verbose_name_plural = _("Bird characteristic selections")

    def clean(self):
        if self.selected_grade not in range(4):
            raise ValidationError(
                {"selected_grade": _("The selected grade is invalid.")}
            )

    @property
    def selected_description(self):
        return self.characteristic.description_for_level(self.selected_grade)

    def __str__(self):
        return "{}: {}".format(self.characteristic, self.selected_description)


class Breeder(models.Model):
    """Breeder (contacts) model"""

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=60, verbose_name=_("First name"))
    last_name = models.CharField(max_length=60, verbose_name=_("Last name"))
    breeding_reg_nr = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_("Breeding registration number"),
    )
    address = models.TextField(blank=True, null=True, verbose_name=_("Home address"))
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Phone number")
    )
    notes = models.TextField(blank=True, verbose_name=_("Remarks / Notes"))

    class Meta:
        ordering = [Lower("last_name")]
        verbose_name = _("Breeder")
        verbose_name_plural = _("Breeders")

    def __str__(self):
        """Represent a breeder with his name and regnumber"""
        return "{}, {} ({})".format(
            self.last_name, self.first_name, self.breeding_reg_nr
        )

    def display_name(self):
        return "{}, {}".format(self.last_name, self.first_name)


class ColorProperty(models.Model):
    """Color properties, which include a rank of importance,
    for when the items should be displayed"""

    user = models.ForeignKey(BudgieUser, on_delete=models.CASCADE)
    color_name = models.CharField(
        max_length=100, blank=False, verbose_name=_("Colorproperty name")
    )
    rank = models.IntegerField(
        verbose_name=_("Matter of importance"),
        help_text=_("1 is very important, 1000 is not important"),
    )

    class Meta:
        ordering = ["rank"]
        verbose_name = _("Color property")
        verbose_name_plural = _("Color properties")

    def __str__(self):
        """Use the color name as the field representation"""
        return self.color_name


class BirdProxy(Bird):
    # This proxy is necessary to facilitate the ExportBirdAdmin view
    class Meta:
        proxy = True
        verbose_name = "{} {}".format(_("Not in use:"), _("Bird"))
        verbose_name_plural = "{} {}".format(_("Not in use:"), _("Birds"))
