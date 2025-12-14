from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import BudgieUser


@admin.register(BudgieUser)
class BudgieUserAdmin(UserAdmin):
    model = BudgieUser

    list_display = (
        "username",
        "email",
        "breeding_reg_nr",
        "is_staff",
        "is_active",
    )
    search_fields = ("breeding_reg_nr", "email", "first_name")

    fieldsets = UserAdmin.fieldsets + (
        (_("PyBudgie properties"), {"fields": ("breeding_reg_nr", "notes")}),
    )
