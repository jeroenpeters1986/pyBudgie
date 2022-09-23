# Generated by Django 4.1 on 2022-09-21 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("budgie_bird", "0005_alter_bird_father_alter_bird_mother_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="breeder",
            name="breeding_reg_nr",
            field=models.CharField(
                blank=True,
                max_length=40,
                null=True,
                verbose_name="Breeding registration number",
            ),
        ),
    ]