# Generated by Django 4.1 on 2022-10-02 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("budgie_breeding", "0009_alter_breedingcouple_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="current_breeding_couple",
            field=models.ForeignKey(
                blank=True,
                help_text="This is the couple that is currently breeding here, can also be empty",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="current_couple",
                to="budgie_breeding.breedingcouple",
                verbose_name="Current breeding couple",
            ),
        ),
    ]