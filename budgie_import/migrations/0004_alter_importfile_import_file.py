# Generated by Django 4.1.5 on 2023-01-29 11:08

import django.core.files.storage
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("budgie_import", "0003_alter_importfile_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="importfile",
            name="import_file",
            field=models.FileField(
                help_text="Upload an Excel file (.xlsx or .csv) to import new birds or update them",
                storage=django.core.files.storage.FileSystemStorage,
                upload_to="assets/uploads/import",
                validators=[
                    django.core.validators.FileExtensionValidator(["csv", "xlsx"])
                ],
                verbose_name="Import file",
            ),
        ),
    ]