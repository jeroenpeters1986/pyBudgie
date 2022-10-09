from budgie_user.models import BudgieUser


class BudgieUserMixin:
    def save_model(self, request, obj, form, change):
        # For non-superusers, always save as own user instance
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # For non-superusers, always show own instances
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            return queryset.filter(user=request.user)
        return queryset

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # For non-superusers, always show own instances
        if not request.user.is_superuser:
            if db_field.is_relation:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    user=request.user
                )

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # For non-superusers, always show own instances
        if not request.user.is_superuser and db_field.related_model != BudgieUser:
            if "queryset" in kwargs:
                kwargs["queryset"] = kwargs.get("queryset").filter(user=request.user)
            else:
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    user=request.user
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """Hide the user field in the admin when a non-superuser adds/edits forms"""
        if not request.user.is_superuser:
            self.exclude = ["user"]

        form = super().get_form(request, obj, **kwargs)

        return form
