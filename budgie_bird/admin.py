from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .forms import BirdForm
from .models import Bird, Breeder, ColorProperty


class BirdAdmin(admin.ModelAdmin):

    form = BirdForm

    list_display = [
        "ring_number",
        "gender",
        "color",
        "color_props",
        "split_props",
        "date_of_birth",
        "image_tag",
    ]

    def image_tag(self, obj):
        return mark_safe('<img src="{}" height="75" />'.format(obj.photo.url))

    image_tag.short_description = "Image"

    def color_props(self, obj):
        return " ".join(x.color_name for x in obj.color_property.all().order_by("rank"))

    color_props.short_description = _("Color properties")

    def split_props(self, obj):
        return " ".join(x.color_name for x in obj.split_property.all().order_by("rank"))

    split_props.short_description = _("Split properties")


class ColorPropertyAdmin(admin.ModelAdmin):
    list_display = ["color_name", "rank"]


admin.site.register(Bird, BirdAdmin)
admin.site.register(Breeder)
admin.site.register(ColorProperty, ColorPropertyAdmin)
