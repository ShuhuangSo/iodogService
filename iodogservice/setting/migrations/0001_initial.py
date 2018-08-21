# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-08-20 23:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0003_company_create_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_code', models.CharField(help_text='api平台代码', max_length=50, verbose_name='api平台代码')),
                ('api_name', models.CharField(help_text='api平台名称', max_length=50, verbose_name='api平台名称')),
                ('client_id', models.CharField(help_text='开发账户id', max_length=200, verbose_name='开发账户id')),
                ('client_secret', models.CharField(help_text='开发账户密钥', max_length=200, verbose_name='开发账户密钥')),
                ('dp_code', models.CharField(help_text='开发账号代码', max_length=50, verbose_name='开发账号代码')),
            ],
            options={
                'verbose_name_plural': 'api开发账号信息',
                'verbose_name': 'api开发账号信息',
            },
        ),
        migrations.CreateModel(
            name='LogisticsAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logistics_code', models.CharField(help_text='物流代码', max_length=50, verbose_name='物流代码')),
                ('logistics_company', models.CharField(help_text='物流名称', max_length=50, verbose_name='物流名称')),
                ('auth_status', models.BooleanField(default=False, help_text='授权状态', verbose_name='授权状态')),
                ('auth_time', models.DateTimeField(auto_now=True, help_text='授权时间', verbose_name='授权时间')),
                ('app_key', models.CharField(help_text='物流用户账号', max_length=50, null=True, verbose_name='物流用户账号')),
                ('token', models.CharField(help_text='账户token', max_length=200, null=True, verbose_name='账户token')),
                ('auth_link', models.CharField(help_text='授权链接', max_length=500, verbose_name='授权链接')),
                ('company', models.ForeignKey(help_text='公司', on_delete=django.db.models.deletion.CASCADE, to='users.Company', verbose_name='公司')),
            ],
            options={
                'verbose_name_plural': '物流平台授权信息',
                'verbose_name': '物流平台授权信息',
            },
        ),
    ]
