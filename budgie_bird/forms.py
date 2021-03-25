from django import forms
from django.utils.translation import gettext_lazy as _

from budgie_bird.models import Bird


class BirdForm(forms.ModelForm):
    class Meta:
        model = Bird
        exclude = []

    def clean_father(self):
        return self.clean_descendant("father")

    def clean_mother(self):
        return self.clean_descendant("mother")

    def clean_descendant(self, parent):
        """ Make sure a bird can't be it's own parent """
        cleaned_data = self.cleaned_data

        if cleaned_data[parent]:
            if cleaned_data[parent].pk == self.instance.pk:
                raise forms.ValidationError(
                    _("Bird cannot be it's own {parent}").format(parent=_(parent))
                )

        return cleaned_data[parent]
