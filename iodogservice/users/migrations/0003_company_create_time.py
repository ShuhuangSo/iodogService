# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-06-23 17:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180623_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 6, 23, 17, 15, 43, 711109), help_text='创建时间', verbose_name='创建时间'),
            preserve_default=False,
        ),
    ]
