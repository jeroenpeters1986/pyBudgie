# Generated by Django 4.1 on 2022-09-10 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("budgie_bird", "0004_alter_bird_owner"),
        ("budgie_breeding", "0002_alter_breedingcouple_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="breedingcouple",
            name="female",
            field=models.ForeignKey(
                limit_choices_to={"gender": "female"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="female",
                to="budgie_bird.bird",
                verbose_name="Female",
            ),
        ),
        migrations.AlterField(
            model_name="breedingcouple",
            name="male",
            field=models.ForeignKey(
                limit_choices_to={"gender": "male"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="male",
                to="budgie_bird.bird",
                verbose_name="Male",
            ),
        ),
        migrations.AlterField(
            model_name="breedingseason",
            name="starting_month",
            field=models.CharField(
                choices=[
                    ("1", "January"),
                    ("2", "February"),
                    ("3", "March"),
                    ("4", "April"),
                    ("5", "May"),
                    ("6", "June"),
                    ("7", "July"),
                    ("8", "August"),
                    ("9", "September"),
                    ("10", "October"),
                    ("11", "November"),
                    ("12", "December"),
                ],
                default="1",
                help_text="This allows you to distinguish breeding rounds if you have multiple per year",
                max_length=15,
                verbose_name="Starting month",
            ),
        ),
        migrations.AlterField(
            model_name="egg",
            name="couple",
            field=models.ForeignKey(
                limit_choices_to={"user": models.Value("user")},
                on_delete=django.db.models.deletion.CASCADE,
                to="budgie_breeding.breedingcouple",
                verbose_name="Breeding couple",
            ),
        ),
    ]