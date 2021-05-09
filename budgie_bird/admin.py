from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
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
        "family_tree",
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

    fieldsets = (
        (
            _("General information"),
            {
                "fields": (
                    "user",
                    "ring_number",
                    "gender",
                    "date_of_birth",
                    "date_of_death",
                )
            },
        ),
        (
            _("Color properties"),
            {
                "fields": ("color", "color_property", "split_property"),
            },
        ),
        (
            _("Family tree"),
            {
                "fields": ("father", "mother", "breeder"),
            },
        ),
        (
            _("Other information"),
            {
                "fields": ("owner", "is_owned", "is_for_sale"),
            },
        ),
        (None, {"fields": ("photo", "notes")}),
    )

    autocomplete_fields = ["father", "mother", "breeder", "owner"]
    save_on_top = True
    save_as = True
    actions = ["export_as_csv", "mark_as_owned", "mark_as_for_sale"]

    change_list_template = "budgie_bird/admin/bird_changelist.html"

    def get_urls(self):
        """ Extend the urls of the Django admin with new views """
        urls = super().get_urls()
        additional_bird_admin_urls = [
            path(
                "<path:object_id>/family_tree/",
                self.admin_site.admin_view(self.family_tree_view, cacheable=True),
                name="budgie_bird_bird_familytree",
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

    def family_tree(self, obj):
        return mark_safe(
            '<a class="grp-button" href="{}">{}</a>'.format(
                reverse("admin:budgie_bird_bird_familytree", args=[obj.pk]), _("View")
            )
        )

    family_tree.short_description = _("Family tree")

    def color_props(self, obj):
        return obj.color_props()

    color_props.short_description = _("Color properties")

    def split_props(self, obj):
        return obj.split_props()

    split_props.short_description = _("Split properties")

    def mark_as_owned(self, request, queryset):
        queryset.update(is_owned=True)
        messages.add_message(
            request, messages.SUCCESS, _("Selected birds are marked as owned")
        )

    mark_as_owned.short_description = _("Mark as owned")

    def mark_as_for_sale(self, request, queryset):
        queryset.update(is_for_sale=True)
        messages.add_message(
            request, messages.SUCCESS, _("Selected birds are marked as for sale")
        )

    mark_as_for_sale.short_description = _("Mark as for sale")

    def get_ancestors_graphviz(self, generation):
        """ Generate digraph notation, don't really think it should live here..?! """
        graphviz_notation = ""
        for parent_type in ["father", "mother"]:
            if generation["ancestors"][parent_type]:
                graphviz_notation += '\n  "{}" -> "{}"'.format(
                    generation["bird"].__str__(),
                    generation["ancestors"][parent_type]["bird"].__str__(),
                )
                graphviz_notation += self.get_ancestors_graphviz(
                    generation["ancestors"][parent_type]
                )

        return graphviz_notation

    def family_tree_view(self, request, *args, **kwargs):
        """ Custom admin view to show the family tree """
        try:
            bird = Bird.objects.get(pk=kwargs["object_id"])
        except Bird.DoesNotExist:
            messages.add_message(request, messages.ERROR, _("That bird does not exist"))
            return redirect(reverse("admin:budgie_bird_bird_changelist"))

        family_tree = bird.get_ancestors()

        graphviz_format = "digraph G {"
        graphviz_format += self.get_ancestors_graphviz(family_tree)
        graphviz_format += "}"

        context = dict(
            self.admin_site.each_context(request),  # Common admin things
            bird=bird,
            family_tree=family_tree,
            family_tree_graphviz=graphviz_format,
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
