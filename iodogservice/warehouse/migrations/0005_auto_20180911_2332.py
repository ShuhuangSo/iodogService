# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-09-11 23:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0004_warehousestock_cn_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousestock',
            name='avg_sell_qty15',
            field=models.CharField(blank=True, help_text='近15天平均销量(os)', max_length=50, null=True, verbose_name='近15天平均销量(os)'),
        ),
        migrations.AddField(
            model_name='warehousestock',
            name='avg_sell_qty7',
            field=models.CharField(blank=True, help_text='近7天平均销量(os)', max_length=50, null=True, verbose_name='近7天平均销量(os)'),
        ),
        migrations.AddField(
            model_name='warehousestock',
            name='avg_stock15',
            field=models.CharField(blank=True, help_text='近15天平均库存(os)', max_length=50, null=True, verbose_name='近15天平均库存(os)'),
        ),
        migrations.AddField(
            model_name='warehousestock',
            name='avg_stock7',
            field=models.CharField(blank=True, help_text='近7天平均库存(os)', max_length=50, null=True, verbose_name='近7天平均库存(os)'),
        ),
    ]
