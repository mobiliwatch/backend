# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-31 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0008_providers_part_2'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AlterModelTable('City', 'region_city'),
            ]
        ),
    ]