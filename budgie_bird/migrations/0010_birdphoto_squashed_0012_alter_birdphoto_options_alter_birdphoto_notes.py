# Generated by Django 5.0.4 on 2024-04-13 21:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("budgie_bird", "0010_birdphoto"),
        ("budgie_bird", "0011_alter_birdphoto_bird_alter_birdphoto_notes"),
        ("budgie_bird", "0012_alter_birdphoto_options_alter_birdphoto_notes"),
    ]

    dependencies = [
        ("budgie_bird", "0009_alter_birdproxy_options_alter_bird_father_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BirdPhoto",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "notes",
                    models.CharField(blank=True, max_length=255, verbose_name="Notes"),
                ),
                (
                    "image",
                    models.ImageField(
                        default="assets/budgie-silhouette.png",
                        upload_to="assets/uploads/bird_pics",
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now=True)),
                (
                    "bird",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="birdphotos",
                        to="budgie_bird.bird",
                    ),
                ),
            ],
            options={
                "ordering": ["uploaded_at"],
                "verbose_name": "Bird photo",
                "verbose_name_plural": "Bird photos",
            },
        ),
    ]