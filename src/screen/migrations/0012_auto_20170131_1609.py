# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-31 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0011_locationwidget_auto_pagination'),
        ('region', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherwidget',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weather_widgets', to='region.City'),
        ),
    ]
