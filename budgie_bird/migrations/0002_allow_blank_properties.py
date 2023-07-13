# Generated by Django 3.1.7 on 2021-03-25 21:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("budgie_bird", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bird",
            name="color_property",
            field=models.ManyToManyField(
                blank=True,
                related_name="color_properties",
                to="budgie_bird.ColorProperty",
                verbose_name="Color properties",
            ),
        ),
        migrations.AlterField(
            model_name="bird",
            name="gender",
            field=models.CharField(
                choices=[
                    ("unknown", "Unknown"),
                    ("male", "Male"),
                    ("female", "Female"),
                ],
                default="unknown",
                max_length=10,
                verbose_name="Gender",
            ),
        ),
        migrations.AlterField(
            model_name="bird",
            name="split_property",
            field=models.ManyToManyField(
                blank=True,
                related_name="split_properties",
                to="budgie_bird.ColorProperty",
                verbose_name="Split properties",
            ),
        ),
    ]
