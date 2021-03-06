# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 07:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('itinisere_id', models.IntegerField(unique=True)),
                ('direction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_stops', to='transport.Direction')),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_stops', to='transport.Line')),
            ],
            options={
                'ordering': ('line', 'direction', 'order'),
            },
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('itinisere_id', models.IntegerField(unique=True)),
                ('metro_id', models.CharField(blank=True, max_length=250, null=True)),
                ('lines', models.ManyToManyField(related_name='stops', through='transport.LineStop', to='transport.Line')),
            ],
        ),
        migrations.AddField(
            model_name='linestop',
            name='stop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_stops', to='transport.Stop'),
        ),
        migrations.AlterUniqueTogether(
            name='linestop',
            unique_together=set([('line', 'direction', 'order')]),
        ),
        migrations.AddField(
            model_name='stop',
            name='metro_cluster',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
