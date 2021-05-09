from django.utils.dateparse import parse_date
from django import forms
from django.utils.translation import gettext_lazy as _

from budgie_bird.models import Bird


def make_date(date):
    try:
        return parse_date(date)
    except TypeError:
        return date


def validate_birth_date_with_descendans(bird, parent):
    if all([bird.date_of_birth, parent.date_of_birth]):
        return make_date(bird.date_of_birth) > make_date(parent.date_of_birth)
    return True


def validate_bird_descendant(bird, parent):
    if parent:
        if parent.pk == bird.pk:
            return False
    return True


class BirdForm(forms.ModelForm):
    class Meta:
        model = Bird
        exclude = []

    def clean_father(self):
        return self.clean_descendant("father")

    def clean_mother(self):
        return self.clean_descendant("mother")

    def clean(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        date_of_death = self.cleaned_data.get("date_of_death")
        if all([date_of_birth, date_of_death]):
            if make_date(date_of_birth) > make_date(date_of_death):
                raise forms.ValidationError(
                        _("Bird cannot die before it's born."),
                        code="invalid")
        return super().clean()

    def clean_descendant(self, parent):
        """Make sure a bird can't be it's own parent"""
        cleaned_data = self.cleaned_data
        bird = self.instance
        parent_cleaned = cleaned_data[parent]
        if parent_cleaned:
            if not validate_bird_descendant(bird, parent_cleaned):
                raise forms.ValidationError(
                    _("Bird cannot be it's own {parent}").format(parent=_(parent))
                )
            if not validate_birth_date_with_descendans(bird, parent_cleaned):
                raise forms.ValidationError(
                        _("Bird cannot be older than {parent}.").format(
                            parent=_(parent)))

        return parent_cleaned
