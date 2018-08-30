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


class ThirdWarehouse(models.Model):
    """
    物流公司仓库列表(与物流公司同步)
    """

    logistics_company = models.CharField(max_length=50, verbose_name='物流公司名称', help_text='物流公司名称')
    wh_code = models.CharField(max_length=80, verbose_name='仓库代码', help_text='仓库代码')
    wh_id = models.CharField(max_length=80, verbose_name='仓库ID', help_text='仓库ID')
    wh_name = models.CharField(max_length=80, verbose_name='仓库名称', help_text='仓库名称')
    wh_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='仓库地址', help_text='仓库地址')
    country_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='仓库所在国家代码', help_text='仓库所在国家代码')

    class Meta:
        verbose_name = '物流公司仓库列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.wh_name


class ThirdDelivery(models.Model):
    """
    物流公司尾程渠道(与物流公司同步)
    """

    product_code = models.CharField(max_length=80, verbose_name='派送方式代码', help_text='派送方式代码')
    delivery_way = models.CharField(max_length=200, verbose_name='派送方式名称', help_text='派送方式名称')
    delivery_id = models.CharField(max_length=30, verbose_name='派送方式id', help_text='派送方式id')
    is_door_number = models.BooleanField(default=False, verbose_name='派送方式是否门牌必选', help_text='派送方式是否门牌必选')
    wh_id = models.CharField(max_length=30, verbose_name='海外仓仓库id', help_text='海外仓仓库id')
    is_active = models.BooleanField(default=False, verbose_name='是否激活', help_text='是否激活')

    class Meta:
        verbose_name = '物流公司尾程渠道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.delivery_way