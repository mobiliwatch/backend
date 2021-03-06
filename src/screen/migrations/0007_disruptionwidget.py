# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-12 22:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20161201_2226'),
        ('screen', '0006_auto_20161130_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisruptionWidget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disruptionwidget', to='screen.Group')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets_disruptions', to='users.Location')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
