from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from budgie_user.models import BudgieUser


class ImportFile(models.Model):
    """This represents all the import-uploads of a user, to complement/change their inventory"""

    user = models.ForeignKey(
        BudgieUser, on_delete=models.CASCADE, null=True, blank=True
    )
    import_file = models.FileField(
        verbose_name=_("Import file"),
        help_text=_(
            "Upload an Excel file (.xlsx or .csv) to import new birds or update them"
        ),
        validators=[FileExtensionValidator(["csv", "xlsx"])],
        upload_to=settings.BIRD_EXCELFILE_UPLOAD_LOCATION,
    )
    uploaded_date = models.DateTimeField(
        verbose_name=_("Upload date"), auto_now_add=True
    )
    completed = models.BooleanField(
        verbose_name=_("Completed successfully"), default=False
    )
    notes = models.TextField(
        verbose_name=_("Notes after import"),
        help_text=_(
            "This field contains information about the import process, "
            "when something special happens on import"
        ),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["uploaded_date"]
        verbose_name = _("Import file")
        verbose_name_plural = _("Import files")
