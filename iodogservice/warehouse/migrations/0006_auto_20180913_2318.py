# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-09-13 23:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_auto_20180911_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehousestock',
            name='doi',
            field=models.FloatField(blank=True, help_text='DOI(os)', null=True, verbose_name='DOI(os)'),
        ),
    ]
