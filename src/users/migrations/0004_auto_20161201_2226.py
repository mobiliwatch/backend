# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def move_links(apps, schema_editor):
    """
    Move m2m relations
    """
    LocationStop = apps.get_model('users', 'LocationStop')
    Location = apps.get_model('users', 'Location')

    for location in Location.objects.all():
        for line_stop in location.line_stops.all():
            LocationStop.objects.create(
                location=location,
                line_stop=line_stop,
            )

class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0005_city_position'),
        ('users', '0003_location_line_stops'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),

        # Create new relation model
        migrations.CreateModel(
            name='LocationStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(default=0)),
                ('walking_time', models.FloatField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('line_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_stops', to='transport.LineStop')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_stops', to='users.Location')),
            ],
        ),

        # Fill it with current data
        migrations.RunPython(move_links),

        # Kill the old link
        migrations.RemoveField(
            model_name='location',
            name='line_stops',
        ),

        # Create new link
        migrations.AddField(
            model_name='location',
            name='line_stops',
            field=models.ManyToManyField(related_name='locations', through='users.LocationStop', to='transport.LineStop'),
        ),

        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='locationstop',
            unique_together=set([('location', 'line_stop')]),
        ),
    ]