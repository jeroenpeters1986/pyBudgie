from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from budgie_user.mixins import BudgieUserMixin
from .models import BreedingSeason, BreedingCouple, Egg


class EggInline(BudgieUserMixin, admin.TabularInline):
    model = Egg
    exclude = ["user"]


class BreedingCoupleInline(BudgieUserMixin, admin.TabularInline):
    model = BreedingCouple
    exclude = ["user", "notes"]


@admin.register(BreedingSeason)
class BreedingSeasonAdmin(BudgieUserMixin, admin.ModelAdmin):
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
    list_display = ["full_name", "male", "female", "start_date", "season_link"]
    list_filter = ["season"]
    date_hierarchy = "start_date"
    inlines = [
        EggInline,
    ]

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

    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []

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
    list_display = ["couple", "date", "status"]
    list_filter = ["couple", "status"]
