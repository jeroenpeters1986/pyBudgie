from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from budgie_user.mixins import BudgieUserMixin
from .forms import BirdForm
from .mixins import AdminExportCsvMixin
from .models import Bird, Breeder, ColorProperty


@admin.register(Bird)
class BirdAdmin(BudgieUserMixin, admin.ModelAdmin, AdminExportCsvMixin):

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

    autocomplete_fields = ["father", "mother", "breeder", "owner"]
    save_on_top = True
    save_as = True
    actions = ["export_as_csv"]

    change_list_template = "budgie_bird/admin/bird_changelist.html"

    def get_urls(self):
        """ Extend the urls of the Django admin with new views """
        urls = super().get_urls()
        additional_bird_admin_urls = [
            path(
                "<path:object_id>/family_tree/",
                self.admin_site.admin_view(self.family_tree_view, cacheable=True),
            )
        ]
        return additional_bird_admin_urls + urls

    def get_readonly_fields(self, request, obj=None):
        """ This makes sure the admin doesn't give away the other usernames to non-admins """
        if not request.user.is_superuser:
            return ["user"]
        return {}

    def image_tag(self, obj):
        """ Render the image tag of the birds photo """
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

    def family_tree_view(self, request, *args, **kwargs):
        context = dict(
            self.admin_site.each_context(request),  # Common admin things

            bird_id=kwargs['object_id'],
            family_tree=Bird.objects.get(pk=kwargs['object_id']).get_ancestors()
        )
        return TemplateResponse(request, "budgie_bird/admin/family_tree.html", context)


@admin.register(Breeder)
class BreederAdmin(BudgieUserMixin, admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "breeding_reg_nr", "notes", "address"]
    list_display = ["display_name", "breeding_reg_nr", "phone_number"]

    def display_name(self, obj):
        # We wouldn't need this if it wasn't for translations...
        return obj.display_name()

    display_name.short_description = _("Full name")


@admin.register(ColorProperty)
class ColorPropertyAdmin(BudgieUserMixin, admin.ModelAdmin):
    search_fields = ["color_name"]
    list_display = ["color_name", "rank"]
