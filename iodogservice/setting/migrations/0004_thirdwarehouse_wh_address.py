# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-08-30 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0003_thirddelivery_thirdwarehouse'),
    ]

    operations = [
        migrations.AddField(
            model_name='thirdwarehouse',
            name='wh_address',
            field=models.CharField(blank=True, help_text='仓库地址', max_length=200, null=True, verbose_name='仓库地址'),
        ),
    ]
