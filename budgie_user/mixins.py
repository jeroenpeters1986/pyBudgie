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
