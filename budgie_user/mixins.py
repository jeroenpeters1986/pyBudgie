from budgie_bird.models import ColorProperty


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
            if db_field.name in ["color_property", "split_property"]:
                kwargs["queryset"] = ColorProperty.objects.filter(user=request.user)

        return super().formfield_for_manytomany(db_field, request, **kwargs)
