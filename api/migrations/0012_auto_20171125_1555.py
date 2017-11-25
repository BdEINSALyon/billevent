# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-25 14:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20171125_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='first_name',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='last_name',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL),
        ),
    ]
