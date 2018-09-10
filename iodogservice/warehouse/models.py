from django.db import models

from users.models import Company

# Create your models here.


class Warehouse(models.Model):
    """
    仓库列表
    """
    WAREHOUSE_TYPE = (
        ('LOCAL', '本地仓'),
        ('OS', '海外仓'),
    )

    wh_code = models.CharField(max_length=80, verbose_name='仓库代码', help_text='仓库代码')
    wh_id = models.CharField(max_length=80, verbose_name='仓库ID', help_text='仓库ID')
    wh_name = models.CharField(max_length=30, verbose_name='仓库名称', help_text='仓库名称')
    wh_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='仓库地址', help_text='仓库地址')
    return_name = models.CharField(max_length=80, null=True, blank=True, verbose_name='仓库退货收件人', help_text='仓库退货收件人')
    return_phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='仓库退货电话', help_text='仓库退货电话')
    return_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='仓库退货地址', help_text='仓库退货地址')
    post_name = models.CharField(max_length=80, null=True, blank=True, verbose_name='仓库发货人姓名', help_text='仓库发货人姓名')
    post_phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='仓库发货人电话', help_text='仓库发货人电话')
    post_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='仓库发货地址', help_text='仓库发货地址')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    wh_type = models.CharField(max_length=10, choices=WAREHOUSE_TYPE, default='OS', verbose_name='仓库类型', help_text='仓库类型')
    country_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='仓库所在国家代码', help_text='仓库所在国家代码')
    logistics_company = models.CharField(max_length=50, verbose_name='物流公司', help_text='物流公司')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    company = models.ForeignKey(Company, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '仓库列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.wh_code


class WarehouseStock(models.Model):
    """
    仓库库存
    """

    sku = models.CharField(max_length=50, verbose_name='产品sku编码', help_text='产品sku编码')
    cn_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='产品名称', help_text='产品名称')
    all_stock = models.IntegerField(default=0, verbose_name='总库存', help_text='总库存')
    available_qty = models.IntegerField(default=0, verbose_name='可用库存(os)', help_text='可用库存(os)')
    reserved_qty = models.IntegerField(default=0, verbose_name='待出库(os)', help_text='待出库(os)')
    on_way_qty = models.IntegerField(default=0, verbose_name='在途库存(os)', help_text='在途库存(os)')
    his_in_qty = models.IntegerField(default=0, verbose_name='历史入库数量(os)', help_text='历史入库数量(os)')
    his_sell_qty = models.IntegerField(default=0, verbose_name='历史销量(os)', help_text='历史销量(os)')
    avg_sell_qty = models.CharField(max_length=50, null=True, blank=True, verbose_name='近30天平均销量(os)', help_text='近30天平均销量(os)')
    avg_stock = models.CharField(max_length=50, null=True, blank=True, verbose_name='近30天平均库存(os)', help_text='近30天平均库存(os)')
    doi = models.CharField(max_length=50, null=True, blank=True, verbose_name='DOI(os)', help_text='DOI(os)')
    is_return = models.BooleanField(default=False, verbose_name='是否退货库存(os)', help_text='是否退货库存(os)')
    is_active = models.BooleanField(default=True, verbose_name='产品是否有效(os)', help_text='产品是否有效(os)')
    is_prohibit = models.BooleanField(default=False, verbose_name='是否禁止出库(os)', help_text='是否禁止出库(os)')
    is_onsale = models.BooleanField(default=True, verbose_name='是否在售', help_text='是否在售')
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name='仓位', help_text='仓位')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    warehouse = models.ForeignKey(Warehouse, verbose_name='仓库', help_text='仓库')

    class Meta:
        verbose_name = '仓库库存'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class Position(models.Model):
    """
    仓位
    """

    po_code = models.CharField(max_length=50, verbose_name='仓位编码', help_text='仓位编码')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    warehouse = models.ForeignKey(Warehouse, verbose_name='仓库', help_text='仓库')

    class Meta:
        verbose_name = '仓位'
        verbose_name_plural = verbose_name
        ordering = ['po_code']

    def __str__(self):
        return self.po_code


class DeliveryWay(models.Model):
    """
    仓库物流派送方式
    """

    product_code = models.CharField(max_length=80, verbose_name='派送方式代码', help_text='派送方式代码')
    delivery_way = models.CharField(max_length=200, verbose_name='派送方式名称', help_text='派送方式名称')
    origin_name = models.CharField(max_length=200, verbose_name='派送方式名称(原名称)', help_text='派送方式名称(原名称)')
    delivery_id = models.CharField(max_length=30, verbose_name='派送方式id', help_text='派送方式id')
    is_door_number = models.BooleanField(default=False, verbose_name='派送方式是否门牌必选', help_text='派送方式是否门牌必选')
    wh_id = models.CharField(max_length=30, verbose_name='海外仓仓库id', help_text='海外仓仓库id')
    warehouse = models.ForeignKey(Warehouse, verbose_name='仓库', help_text='仓库')

    class Meta:
        verbose_name = '仓库物流派送方式'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.delivery_way