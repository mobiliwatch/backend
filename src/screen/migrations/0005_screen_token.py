# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 05:30
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0004_screen_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
