from django.db import models

from warehouse.models import WarehouseStock, Warehouse
from users.models import Company

# Create your models here.


class RefillPromote(models.Model):
    """
    补货推荐
    """

    buy_qty = models.IntegerField(default=0, verbose_name='推荐采购数量', help_text='推荐采购数量')
    t_weight = models.FloatField(null=True, blank=True, verbose_name='单项重量kg', help_text='单项重量kg')
    warehouse_stock = models.ForeignKey(WarehouseStock, verbose_name='仓库库存', help_text='仓库库存')
    warehouse = models.ForeignKey(Warehouse, verbose_name='仓库', help_text='仓库')

    class Meta:
        verbose_name = '补货推荐'
        verbose_name_plural = verbose_name
        ordering = ['-buy_qty']


class RefillSetting(models.Model):
    """
    补货推荐设置
    """

    is_active = models.BooleanField(default=True, verbose_name='是否开启', help_text='是否开启')
    stock_days = models.IntegerField(default=0, verbose_name='库存备货天数', help_text='库存备货天数')
    min_buy = models.IntegerField(default=0, verbose_name='最少采购个数', help_text='最少采购个数')
    auto_carry = models.IntegerField(default=0, verbose_name='自动进位', help_text='自动进位')
    is_auto_calc = models.BooleanField(default=True, verbose_name='是否自动计算', help_text='是否自动计算')
    remind_weight = models.FloatField(null=True, blank=True, verbose_name='自动计算提醒重量', help_text='自动计算提醒重量')
    remind_sku_qty = models.IntegerField(default=0, verbose_name='提醒商品SKU数', help_text='提醒商品SKU数')
    remind_total_qty = models.IntegerField(default=0, verbose_name='提醒总商品数', help_text='提醒总商品数')
    company = models.ForeignKey(Company, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '补货推荐设置'
        verbose_name_plural = verbose_name