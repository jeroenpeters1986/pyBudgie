# Generated by Django 4.1 on 2022-09-02 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("budgie_bird", "0004_alter_bird_owner"),
    ]

    operations = [
        migrations.CreateModel(
            name="BreedingCouple",
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
                    "start_date",
                    models.DateField(blank=True, null=True, verbose_name="Start date"),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Remarks / Notes")),
                (
                    "female",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="female",
                        to="budgie_bird.bird",
                        verbose_name="Female",
                    ),
                ),
                (
                    "male",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="male",
                        to="budgie_bird.bird",
                        verbose_name="Male",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Egg",
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
                ("date", models.DateField(verbose_name="Date found")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("fertilized", "Fertilized"),
                            ("unfertilized", "Unfertilized"),
                            ("died_off", "Died off"),
                            ("broken", "Broken"),
                        ],
                        default="unfertilized",
                        max_length=15,
                        verbose_name="Status",
                    ),
                ),
                (
                    "couple",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="budgie_breeding.breedingcouple",
                        verbose_name="Breeding couple",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BreedingSeason",
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
                ("year", models.DateField(verbose_name="Year")),
                (
                    "month",
                    models.DateField(
                        help_text="This allows you to distinguish breeding rounds if you have multiple per year",
                        verbose_name="Starting month",
                    ),
                ),
                (
                    "label",
                    models.TextField(
                        blank=True,
                        help_text="Optional label to find it quicker",
                        max_length=255,
                        null=True,
                        verbose_name="Label",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="breedingcouple",
            name="season",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="budgie_breeding.breedingseason",
                verbose_name="Breeding season",
            ),
        ),
        migrations.AddField(
            model_name="breedingcouple",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
