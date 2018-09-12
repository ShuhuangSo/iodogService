from rest_framework import serializers

from .models import Warehouse, WarehouseStock, Position
from product.models import Product


class WarehouseSerializer(serializers.ModelSerializer):
    """
    仓库列表
    """
    total_stock_num = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    # 获取仓库产品库存总量
    def get_total_stock_num(self, obj):
        queryset = WarehouseStock.objects.filter(warehouse=obj)
        counts = 0
        for i in queryset:
            counts += i.available_qty
        return counts

    # 获取仓库产品库存价值
    def get_total_value(self, obj):
        queryset = WarehouseStock.objects.filter(warehouse=obj)
        all_value = 0.0
        for i in queryset:
            c = Product.objects.filter(sku=i.sku).count()
            if c == 1:
                p = Product.objects.get(sku=i.sku)
                value = i.available_qty * p.cost
                all_value += value
        return all_value

    class Meta:
        model = Warehouse
        fields = ('id', 'wh_code', 'wh_id', 'wh_name', 'wh_address', 'return_name',
                  'return_phone', 'return_address', 'post_name', 'post_phone',
                  'post_address', 'is_active', 'wh_type', 'country_code',
                  'logistics_company', 'create_time', 'total_stock_num', 'total_value')


class PositionSerializer(serializers.ModelSerializer):
    """
    仓位
    """
    class Meta:
        model = Position
        fields = ('id', 'po_code', 'is_active')


class WarehouseStockSerializer(serializers.ModelSerializer):
    """
    库存列表
    """
    image = serializers.SerializerMethodField()

    # 获取产品图片
    def get_image(self, obj):
        company = obj.warehouse.company
        queryset = Product.objects.filter(company=company, sku=obj.sku).count()
        if queryset:
            product = Product.objects.filter(company=company).get(sku=obj.sku)
            return product.image if product.image else ''
        return ''

    class Meta:
        model = WarehouseStock
        fields = ('id', 'sku', 'cn_name', 'image', 'all_stock', 'available_qty', 'reserved_qty', 'on_way_qty', 'his_in_qty'
                  , 'his_sell_qty', 'avg_sell_qty', 'avg_stock', 'avg_sell_qty15', 'avg_stock15', 'avg_sell_qty7',
                  'avg_stock7', 'doi', 'is_return','is_active', 'is_prohibit', 'is_onsale', 'position', 'create_time', 'warehouse')