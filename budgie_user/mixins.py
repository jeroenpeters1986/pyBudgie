from budgie_bird.models import ColorProperty, Bird


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        # For non-superusers, always show own instances
        if not request.user.is_superuser:

            if db_field.name == "male":
                kwargs["queryset"] = Bird.objects.filter(
                    user=request.user, gender=Bird.Gender.MALE
                )

        #
        #
        # print(db_field)
        # print(db_field.is_relation)
        # print(db_field._limit_choices_to)
        # print(kwargs)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """Hide the user field in the admin when a non-superuser adds/edits forms"""
        if not request.user.is_superuser:
            self.exclude = ["user"]

        form = super().get_form(request, obj, **kwargs)

        return form
