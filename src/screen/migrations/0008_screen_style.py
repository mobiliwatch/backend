# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0007_disruptionwidget'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='style',
            field=models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=10),
        ),
    ]
