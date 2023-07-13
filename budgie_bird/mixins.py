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
        model_fields = list(meta.fields + meta.many_to_many)
        del model_fields[1]
        print(",".join(name.name for name in model_fields))

        field_names = [field.name for field in model_fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for row in self.model.objects.filter(user=request.user):
            values = []
            for field in field_names:
                value = getattr(row, field)
                if callable(value):
                    try:
                        value = ", ".join(color.color_name for color in value.all())
                    except Exception as error:
                        print(error)
                        value = "Error retrieving value"
                if value is None:
                    value = ""
                values.append(value)
            writer.writerow(values)

        return response

    export_all_as_csv.short_description = _("Export all to .csv")
