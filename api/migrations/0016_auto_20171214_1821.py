# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-14 17:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20171214_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compostage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_created=True)),
                ('billet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Billet')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.File')),
            ],
        ),
        migrations.AddField(
            model_name='billet',
            name='files',
            field=models.ManyToManyField(blank=True, through='api.Compostage', to='api.File'),
        ),
    ]