# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-26 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercanet', '0005_auto_20171126_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionrequest',
            name='started',
            field=models.BooleanField(default=False, verbose_name='pris en charge par mercanet'),
        ),
    ]
