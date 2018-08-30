# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-08-30 22:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0002_auto_20180820_2354'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdDelivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(help_text='派送方式代码', max_length=80, verbose_name='派送方式代码')),
                ('delivery_way', models.CharField(help_text='派送方式名称', max_length=200, verbose_name='派送方式名称')),
                ('delivery_id', models.CharField(help_text='派送方式id', max_length=30, verbose_name='派送方式id')),
                ('is_door_number', models.BooleanField(default=False, help_text='派送方式是否门牌必选', verbose_name='派送方式是否门牌必选')),
                ('wh_id', models.CharField(help_text='海外仓仓库id', max_length=30, verbose_name='海外仓仓库id')),
            ],
            options={
                'verbose_name_plural': '物流公司尾程渠道',
                'verbose_name': '物流公司尾程渠道',
            },
        ),
        migrations.CreateModel(
            name='ThirdWarehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logistics_company', models.CharField(help_text='物流公司名称', max_length=50, verbose_name='物流公司名称')),
                ('wh_code', models.CharField(help_text='仓库代码', max_length=80, verbose_name='仓库代码')),
                ('wh_id', models.CharField(help_text='仓库ID', max_length=80, verbose_name='仓库ID')),
                ('wh_name', models.CharField(help_text='仓库名称', max_length=80, verbose_name='仓库名称')),
                ('country_code', models.CharField(blank=True, help_text='仓库所在国家代码', max_length=20, null=True, verbose_name='仓库所在国家代码')),
            ],
            options={
                'verbose_name_plural': '物流公司仓库列表',
                'verbose_name': '物流公司仓库列表',
            },
        ),
    ]
