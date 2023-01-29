import csv
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


class AdminExportCsvMixin:
    def export_as_csv(self, request, queryset):
        """Export a model as CSV"""

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = _("Export selected to .csv")


class AdminExportAllCsvMixin:
    def export_all_as_csv(self, request, queryset):
        """Export all objects for a model to CSV"""

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in self.model.objects.filter(user=request.user):
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_all_as_csv.short_description = _("Export all to .csv")
