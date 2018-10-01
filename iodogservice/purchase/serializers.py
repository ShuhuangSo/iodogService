from rest_framework import serializers

from product.models import Product
from .models import RefillPromote, RefillSetting


class RefillPromoteSerializer(serializers.ModelSerializer):
    """
    补货推荐
    """
    image = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    product_weight = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    cn_name = serializers.SerializerMethodField()
    available_qty = serializers.SerializerMethodField()
    on_way_qty = serializers.SerializerMethodField()
    avg_sell_qty = serializers.SerializerMethodField()
    avg_sell_qty15 = serializers.SerializerMethodField()
    avg_sell_qty7 = serializers.SerializerMethodField()
    doi = serializers.SerializerMethodField()

    # 获取产品图片
    def get_image(self, obj):
        company = obj.warehouse.company
        sku = obj.warehouse_stock.sku
        queryset = Product.objects.filter(company=company, sku=sku).count()
        if queryset:
            product = Product.objects.filter(company=company).get(sku=sku)
            return product.image if product.image else ''
        return ''

    # 获取产品sku
    def get_sku(self, obj):
        return obj.warehouse_stock.sku

    # 获取产品名称
    def get_cn_name(self, obj):
        return obj.warehouse_stock.cn_name

    # 获取可用库存
    def get_available_qty(self, obj):
        return obj.warehouse_stock.available_qty

    # 获取在途数量
    def get_on_way_qty(self, obj):
        return obj.warehouse_stock.on_way_qty

    # 获取30天平均销量
    def get_avg_sell_qty(self, obj):
        return obj.warehouse_stock.avg_sell_qty

    # 获取15天平均销量
    def get_avg_sell_qty15(self, obj):
        return obj.warehouse_stock.avg_sell_qty15

    # 获取7天平均销量
    def get_avg_sell_qty7(self, obj):
        return obj.warehouse_stock.avg_sell_qty7

    # 获取doi
    def get_doi(self, obj):
        return obj.warehouse_stock.doi

    # 获取产品id
    def get_product_id(self, obj):
        company = obj.warehouse.company
        sku = obj.warehouse_stock.sku
        queryset = Product.objects.filter(company=company, sku=sku).count()
        if queryset:
            product = Product.objects.filter(company=company).get(sku=sku)
            return product.id
        return ''

    # 获取产品重量
    def get_product_weight(self, obj):
        company = obj.warehouse.company
        sku = obj.warehouse_stock.sku
        queryset = Product.objects.filter(company=company, sku=sku).count()
        if queryset:
            product = Product.objects.filter(company=company).get(sku=sku)
            return product.weight/1000 if product.weight else None
        return ''

    class Meta:
        model = RefillPromote
        fields = ('id', 'sku', 'product_id', 'cn_name', 'image', 'product_weight', 'buy_qty',
                  'available_qty', 'on_way_qty', 'avg_sell_qty', 'avg_sell_qty15', 'avg_sell_qty7', 'doi')


class RefillSettingSerializer(serializers.ModelSerializer):
    """
    补货推荐设置
    """
    class Meta:
        model = RefillSetting
        fields = "__all__"