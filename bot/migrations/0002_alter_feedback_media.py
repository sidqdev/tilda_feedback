# Generated by Django 4.1.2 on 2023-06-13 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="media",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
