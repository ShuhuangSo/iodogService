from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Company(models.Model):
    """
    公司
    """
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='公司名称', help_text='公司名称')
    expried_time = models.DateTimeField(default=datetime.now, verbose_name='过期时间', help_text='过期时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活', help_text='是否激活')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.name


class UserProfile(AbstractUser):
    """
    用户
    """
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name='姓名', help_text='姓名')
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员', help_text='是否管理员')
    company = models.ForeignKey(Company, null=True, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.username


