# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 13:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0004_auto_20161031_1511'),
        ('users', '0002_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='line_stops',
            field=models.ManyToManyField(related_name='locations', to='transport.LineStop'),
        ),
    ]