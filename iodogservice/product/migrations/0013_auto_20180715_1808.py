# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-07-15 18:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20180709_2336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='combopack',
            options={'ordering': ['-create_time'], 'verbose_name': '组合产品', 'verbose_name_plural': '组合产品'},
        ),
    ]
