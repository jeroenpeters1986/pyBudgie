from django.contrib import admin

from budgie_user.mixins import BudgieUserMixin
from .models import ImportFile

import budgie_import.services.import_from_file


@admin.register(ImportFile)
class ImportFileAdmin(BudgieUserMixin, admin.ModelAdmin):
    list_display = ["user", "import_file", "completed", "uploaded_date", "notes"]

    def get_readonly_fields(self, request, obj=None):
        """
        This makes sure the admin doesn't give away the other usernames to non-admins.
        """
        if request.user.is_superuser:
            return {}

        return ["user"]

    def save_model(self, request, obj, form, change):

        form.save()

        if not request.user.is_superuser:
            obj.user = request.user

        # ?? Somehow this is needed for tests.??
        if not obj.user:
            obj.user = request.user

        if not obj.completed:
            budgie_import.services.import_from_file.import_from_file(
                obj.import_file.path, obj.user
            )
            obj.completed = True

        obj.save()
