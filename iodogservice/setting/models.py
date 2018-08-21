from django.db import models
from product.models import Company

# Create your models here.


class LogisticsAuth(models.Model):
    """
    物流平台授权
    """

    logistics_code = models.CharField(max_length=50, verbose_name='物流代码', help_text='物流代码')
    logistics_company = models.CharField(max_length=50, verbose_name='物流名称', help_text='物流名称')
    auth_status = models.BooleanField(default=False, verbose_name='授权状态', help_text='授权状态')
    auth_time = models.DateTimeField(auto_now=True, verbose_name='授权时间', help_text='授权时间')
    app_key = models.CharField(max_length=50, null=True, blank=True, verbose_name='物流用户账号', help_text='物流用户账号')
    token = models.CharField(max_length=200, null=True, blank=True, verbose_name='账户token', help_text='账户token')
    auth_link = models.CharField(max_length=500, verbose_name='授权链接', help_text='授权链接')
    company = models.ForeignKey(Company, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '物流平台授权信息'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.logistics_company


class DevelopAuth(models.Model):
    """
    api开发账号信息
    """

    api_code = models.CharField(max_length=50, verbose_name='api平台代码', help_text='api平台代码')
    api_name = models.CharField(max_length=50, verbose_name='api平台名称', help_text='api平台名称')
    client_id = models.CharField(max_length=200, verbose_name='开发账户id', help_text='开发账户id')
    client_secret = models.CharField(max_length=200, verbose_name='开发账户密钥', help_text='开发账户密钥')
    dp_code = models.CharField(max_length=50, verbose_name='开发账号代码', help_text='开发账号代码')

    class Meta:
        verbose_name = 'api开发账号信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.api_name