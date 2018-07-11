# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-06-23 17:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='公司名称', max_length=50, null=True, verbose_name='公司名称')),
                ('expried_time', models.DateTimeField(default=datetime.datetime.now, help_text='过期时间', verbose_name='过期时间')),
                ('is_active', models.BooleanField(default=True, help_text='是否激活', verbose_name='是否激活')),
            ],
            options={
                'verbose_name': '公司',
                'verbose_name_plural': '公司',
            },
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='company_id',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='expried_time',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='company',
            field=models.ForeignKey(help_text='公司', null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Company', verbose_name='公司'),
        ),
    ]
