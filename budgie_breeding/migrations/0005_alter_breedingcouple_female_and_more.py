# Generated by Django 4.1 on 2022-09-16 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("budgie_bird", "0005_alter_bird_father_alter_bird_mother_and_more"),
        ("budgie_breeding", "0004_alter_egg_couple"),
    ]

    operations = [
        migrations.AlterField(
            model_name="breedingcouple",
            name="female",
            field=models.ForeignKey(
                limit_choices_to=models.Q(
                    ("gender", "female"), ("gender", "unknown"), _connector="OR"
                ),
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
                limit_choices_to=models.Q(
                    ("gender", "male"), ("gender", "unknown"), _connector="OR"
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="male",
                to="budgie_bird.bird",
                verbose_name="Male",
            ),
        ),
    ]