# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-22 13:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0012_auto_20170131_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterWidget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('position', models.PositiveIntegerField(default=0)),
                ('mode', models.CharField(choices=[('timeline', 'Timeline'), ('user_tweets', 'User Tweets'), ('search', 'Search')], default='timeline', max_length=50)),
                ('search_terms', models.CharField(blank=True, max_length=250, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='twitterwidget', to='screen.Group')),
            ],
            options={
                'ordering': ('group', 'position'),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='twitterwidget',
            unique_together=set([('group', 'position')]),
        ),
    ]
