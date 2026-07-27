import django.core.files.storage.filesystem
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("budgie_import", "0005_alter_importfile_import_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="importfile",
            name="import_file",
            field=models.FileField(
                help_text="Upload an Excel file (.xlsx or .csv), ZooEasy file (.zoo), "
                "or photographed breeding card (.jpg, .jpeg, or .png) "
                "to import new birds or update them",
                storage=django.core.files.storage.filesystem.FileSystemStorage,
                upload_to="assets/uploads/import",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["csv", "xlsx", "zoo", "jpg", "jpeg", "png"]
                    )
                ],
                verbose_name="Import file",
            ),
        ),
    ]
