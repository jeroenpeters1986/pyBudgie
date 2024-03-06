import datetime

from django.contrib import admin, messages
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from budgie_bird.models import Bird
from budgie_user.mixins import BudgieUserMixin
from .models import BreedingSeason, BreedingCouple, Egg, Location


class EggInline(BudgieUserMixin, admin.TabularInline):
    model = Egg
    exclude = ["user"]


class BreedingCoupleInline(BudgieUserMixin, admin.TabularInline):
    model = BreedingCouple
    exclude = ["user", "notes"]


@admin.register(BreedingSeason)
class BreedingSeasonAdmin(BudgieUserMixin, admin.ModelAdmin):
    show_facets = True
    list_display = ["starting_year", "starting_month", "label", "couple_count"]
    list_filter = ["starting_year"]
    inlines = [
        BreedingCoupleInline,
    ]

    def couple_count(self, obj):
        return obj.couple_count

    couple_count.short_description = _("Number of couples")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(couple_count=Count("breedingcouple"))
        return queryset

    def save_formset(self, request, form, formset, change):
        # Just be normal on everything that isn't our inline model
        if formset.model != BreedingCouple:
            return super().save_formset(request, form, formset, change)

        # Add users for the breeding couples
        instances = formset.save(commit=False)
        for instance in instances:
            instance.user = request.user
            instance.save()
        formset.save_m2m()


@admin.register(BreedingCouple)
class BreedingCoupleAdmin(BudgieUserMixin, admin.ModelAdmin):
    list_display = [
        "full_name",
        "male",
        "female",
        "start_date",
        "egg_count",
        "eggs_fertilized",
    ]
    list_filter = ["location", "season"]
    date_hierarchy = "start_date"
    inlines = [
        EggInline,
    ]
    autocomplete_fields = ["male", "female"]

    def full_name(self, obj):
        return obj.__str__()

    full_name.short_description = _("Breeding couple")

    def season_link(self, obj):
        link = reverse(
            "admin:budgie_breeding_breedingseason_change", args=[obj.season.id]
        )
        return format_html(
            '<a href="{}" title="{}" style="text-decoration: underline;">{}</a>',
            link,
            _("View"),
            obj.season,
        )

    season_link.short_description = _("(Current) Breeding season")

    def egg_count(self, obj):
        return obj.eggs.count()

    egg_count.short_description = _("Eggs")

    def eggs_fertilized(self, obj):
        return obj.eggs.filter(status=Egg.Status.FERTILIZED).count()

    eggs_fertilized.short_description = _("Fertilized")

    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "male" or db_field.name == "female":
            kwargs["queryset"] = Bird.objects.filter(is_owned=True, user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        # Just be normal on everything that isn't our inline model
        if formset.model != Egg:
            return super().save_formset(request, form, formset, change)

        # Add users for the eggs
        instances = formset.save(commit=False)
        for instance in instances:
            instance.user = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Egg)
class EggAdmin(BudgieUserMixin, admin.ModelAdmin):
    list_display = ["couple", "date", "status", "expected_hatch_date"]
    list_filter = ["couple", "status", "couple__season"]
    ordering = ["couple", "date"]

    change_list_template = "budgie_breeding/admin/egg_changelist.html"

    def get_urls(self):
        # Add our bulk-add view to the urls of Django Admin
        urls = super().get_urls()
        custom_url = [
            path(
                "bulk_add/",
                self.admin_site.admin_view(self.bulk_add),
                name="budgie_breeding_egg_bulk_add",
            )
        ]
        return custom_url + urls

    def bulk_add(self, request):
        """Bulk add view for eggs"""

        if request.POST:
            if not request.POST.get("status") or not request.POST.get("couples[]"):
                messages.error(request, _("Some fields were empty, please retry"))
                return HttpResponseRedirect(
                    reverse("admin:budgie_breeding_egg_bulk_add")
                )

            for couple_id in request.POST.getlist("couples[]"):
                if BreedingCouple.objects.filter(
                    user=request.user, pk=couple_id
                ).exists():
                    found_date = datetime.datetime.strptime(
                        request.POST["date"], "%d-%m-%Y"
                    )
                    Egg.objects.create(
                        user=request.user,
                        status=request.POST["status"],
                        couple_id=couple_id,
                        date=found_date,
                    )

            messages.info(
                request, _("Added an egg for the selected couples succeeded!")
            )
            return HttpResponseRedirect(reverse("admin:budgie_breeding_egg_changelist"))

        context = dict(
            self.admin_site.each_context(request),
            breeding_couples=BreedingCouple.objects.filter(user=request.user),
            statusses=Egg.Status.choices,
        )

        return TemplateResponse(
            request, "budgie_breeding/admin/egg_bulk_add.html", context
        )


@admin.register(Location)
class LocationAdmin(BudgieUserMixin, admin.ModelAdmin):
    list_display = ["code", "notes", "is_taken", "current_breeding_couple_url"]
    ordering = ["code"]

    @admin.display(description=_("Taken"), boolean=True)
    def is_taken(self, obj):
        if obj.current_breeding_couple:
            return True
        return False

    def current_breeding_couple_url(self, obj):
        if not obj.current_breeding_couple:
            return _("None")
        link = reverse(
            "admin:budgie_breeding_breedingcouple_change",
            args=[obj.current_breeding_couple.pk],
        )
        return format_html(
            '<a href="{}" title="{}" style="text-decoration: underline;">{}</a>',
            link,
            _("View"),
            obj.current_breeding_couple,
        )

    current_breeding_couple_url.short_description = _("Current breeding couple")
