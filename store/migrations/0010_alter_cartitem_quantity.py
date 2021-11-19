# Generated by Django 3.2.8 on 2021-11-19 06:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20211018_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]