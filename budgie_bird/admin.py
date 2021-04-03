from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin
from import_export import resources

from budgie_user.mixins import BudgieUserMixin
from .forms import BirdForm
from .models import Bird, Breeder, ColorProperty


class BirdResource(resources.ModelResource):
    """ This resource is used for the Import/Export functionality """

    class Meta:
        model = Bird
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("ring_number",)
        export_order = (
            "ring_number",
            "color",
            "father",
            "mother",
            "date_of_birth",
            "breeder",
            "owner",
            "gender",
            "is_owned",
        )
        fields = (
            "ring_number",
            "color",
            "father",
            "mother",
            "date_of_birth",
            "breeder",
            "owner",
            "gender",
            "is_owned",
        )
        widgets = {
            "date_of_birth": {"format": "%d-%m-%Y"},
        }


class BirdAdmin(BudgieUserMixin, ImportExportModelAdmin):

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
    list_filter = [
        "gender",
        "color",
        "color_property",
        "split_property",
        "is_owned",
        "is_for_sale",
    ]
    search_fields = ["ring_number", "gender"]
    date_hierarchy = "date_of_birth"
    ordering = ["ring_number"]
    resource_class = BirdResource

    autocomplete_fields = ["father", "mother", "breeder", "owner"]
    save_on_top = True
    save_as = True

    def image_tag(self, obj):
        return mark_safe(
            '<img src="{}" height="48" class="birdpreview" />'.format(obj.photo.url)
        )

    image_tag.short_description = _("Photo")

    def color_props(self, obj):
        return obj.color_props()

    color_props.short_description = _("Color properties")

    def split_props(self, obj):
        return obj.split_props()

    split_props.short_description = _("Split properties")


class BreederAdmin(BudgieUserMixin, admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "breeding_reg_nr", "notes", "address"]
    list_display = ["display_name", "breeding_reg_nr", "phone_number"]

    def display_name(self, obj):
        return obj.display_name()

    display_name.short_description = _("Full name")


class ColorPropertyAdmin(BudgieUserMixin, admin.ModelAdmin):
    search_fields = ["color_name"]
    list_display = ["color_name", "rank"]


admin.site.register(Bird, BirdAdmin)
admin.site.register(Breeder, BreederAdmin)
admin.site.register(ColorProperty, ColorPropertyAdmin)
