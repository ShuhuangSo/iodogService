from django.db import models

from users.models import Company

# Create your models here.


class Supplier(models.Model):
    """
    供应商信息
    """

    supplier_name = models.CharField(max_length=30, verbose_name='供应商名称', help_text='供应商名称')
    buy_way = models.CharField(max_length=20, verbose_name='采购渠道', help_text='采购渠道')
    qq = models.CharField(null=True, blank=True, default='', max_length=20, verbose_name='联系qq号码', help_text='联系qq号码')
    phone = models.CharField(null=True, blank=True, default='', max_length=20, verbose_name='联系电话', help_text='联系电话')
    address = models.CharField(null=True, blank=True, default='', max_length=100, verbose_name='地址', help_text='地址')
    store_url = models.CharField(null=True, blank=True, default='', max_length=300, verbose_name='店铺链接', help_text='店铺链接')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    status = models.BooleanField(default=True, verbose_name='启用状态', help_text='启用状态')
    company = models.ForeignKey(Company, null=True, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '供应商信息'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):

        return self.supplier_name


class Product(models.Model):
    """
    产品库
    """
    PRODUCT_STATUS = (
        ('ON_SALE', '在售'),
        ('OFFLINE', '停售'),
        ('CLEAN', '清仓中'),
        ('UNKNOWN', '自动创建'),
    )

    sku = models.CharField(max_length=30, verbose_name='产品编码', help_text='产品编码')
    cn_name = models.CharField(max_length=60, verbose_name='中文名称', help_text='中文名称')
    image = models.ImageField(null=True, blank=True, max_length=200, verbose_name='产品图片', help_text='产品图片')
    status = models.CharField(max_length=10, choices=PRODUCT_STATUS, verbose_name='产品状态', help_text='产品状态')
    cost = models.FloatField(verbose_name='成本价', help_text='成本价')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    en_name = models.CharField(null=True, blank=True, max_length=80, verbose_name='英文名称', help_text='英文名称')
    length = models.FloatField(null=True, blank=True, verbose_name='长', help_text='长')
    width = models.FloatField(null=True, blank=True, verbose_name='宽', help_text='宽')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高', help_text='高')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量', help_text='重量')
    declared_value = models.FloatField(null=True, blank=True, verbose_name='申报价值', help_text='申报价值')
    url = models.CharField(null=True, blank=True, max_length=200, verbose_name='商品URL', help_text='商品URL')
    is_battery = models.BooleanField(default=False, verbose_name='是否带电', help_text='是否带电')
    is_jack = models.BooleanField(default=False, verbose_name='是否带插座', help_text='是否带插座')
    is_brand = models.BooleanField(default=False, verbose_name='是否有品牌', help_text='是否有品牌')
    brand_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌名称', help_text='品牌名称')
    brand_model = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌型号', help_text='品牌型号')
    company = models.ForeignKey(Company, null=True, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '产品库'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):

        return self.sku


class SupplierProduct(models.Model):
    """
    供应商产品
    """
    buy_url = models.CharField(null=True, blank=True, max_length=300, verbose_name='采购链接', help_text='采购链接')
    primary_supplier = models.BooleanField(default=False, verbose_name='默认供应商', help_text='默认供应商')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    supplier = models.ForeignKey(Supplier, related_name='supplier_sup_product', null=True, verbose_name='供应商', help_text='供应商')
    product = models.ForeignKey(Product, related_name='product_sup_product', null=True, verbose_name='产品',
                                help_text='产品')

    class Meta:
        verbose_name = '供应商产品'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):

        return self.sku


class Vsku(models.Model):
    """
    虚拟sku
    """
    vsku = models.CharField(max_length=30, verbose_name='虚拟sku编码', help_text='虚拟sku编码')
    product = models.ForeignKey(Product, related_name='product_vsku', verbose_name='对应产品', help_text='对应产品')

    class Meta:
        verbose_name = '虚拟sku'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.vsku


class RegProduct(models.Model):
    """
    产品注册信息(向物流公司注册)
    """
    logistics_company = models.CharField(max_length=30, verbose_name='物流公司', help_text='物流公司')
    reg_length = models.FloatField(null=True, blank=True, verbose_name='确认长', help_text='确认长')
    reg_width = models.FloatField(null=True, blank=True, verbose_name='确认宽', help_text='确认宽')
    reg_heigth = models.FloatField(null=True, blank=True, verbose_name='确认高', help_text='确认高')
    reg_weight = models.FloatField(null=True, blank=True, verbose_name='确认重量', help_text='确认重量')
    reg_volume = models.FloatField(null=True, blank=True, verbose_name='确认体积', help_text='确认体积')
    is_active = models.BooleanField(default=False, verbose_name='商品是否有效', help_text='商品是否有效')
    product = models.ForeignKey(Product, related_name='product_reg_product', verbose_name='对应产品', help_text='对应产品')

    class Meta:
        verbose_name = '产品注册信息'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.logistics_company


class RegCountry(models.Model):
    """
    产品注册国家
    """
    REG_STATUS = (
        ('ON_SALE', '已发布'),
        ('CHECKING', '待审核'),
        ('REGING', '注册中'),
        ('FAIL', '审核失败'),
    )
    country_code = models.CharField(max_length=5, verbose_name='注册国家编码', help_text='注册国家编码')
    import_value = models.FloatField(verbose_name='进口申报价值', help_text='进口申报价值')
    import_rate = models.FloatField(null=True, blank=True, verbose_name='进口关税率', help_text='进口关税率')
    reg_status = models.CharField(max_length=10, choices=REG_STATUS, verbose_name='产品注册状态', help_text='产品注册状态')
    reg_product = models.ForeignKey(RegProduct, related_name='reg_product_reg_country', null=True, verbose_name='对应注册产品', help_text='对应注册产品')

    class Meta:
        verbose_name = '产品注册国家'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.country_code


class ComboPack(models.Model):
    """
    组合产品
    """
    combo_code = models.CharField(max_length=30, verbose_name='组合sku编码', help_text='组合sku编码')
    combo_name = models.CharField(null=True, blank=True, max_length=50, verbose_name='组合名称', help_text='组合名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    combo_status = models.BooleanField(default=True, verbose_name='启用状态', help_text='启用状态')
    company = models.ForeignKey(Company, null=True, verbose_name='公司', help_text='公司')

    class Meta:
        verbose_name = '组合产品'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):

        return self.combo_code


class ComboSKU(models.Model):
    """
    组合内产品
    """
    sku = models.CharField(max_length=30, verbose_name='产品编码', help_text='产品编码')
    quantity = models.IntegerField(verbose_name='数量', help_text='数量')
    combo_pack = models.ForeignKey(ComboPack, related_name='combo_pack_sku', null=True, verbose_name='组合产品', help_text='组合产品')

    class Meta:
        verbose_name = '组合内产品'
        verbose_name_plural = verbose_name

    def __str__(self):

        return self.sku


class Vcombo(models.Model):
    """
    组合虚拟sku
    """
    vsku = models.CharField(max_length=30, verbose_name='虚拟sku编码', help_text='虚拟sku编码')
    combo_pack = models.ForeignKey(ComboPack, related_name='combo_pack_vcombo', null=True, verbose_name='组合产品', help_text='组合产品')

    class Meta:
        verbose_name = '组合虚拟sku'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.vsku