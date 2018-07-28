from rest_framework import serializers

from .models import Supplier, Product, RegProduct, RegCountry, SupplierProduct, Vsku, ComboPack, ComboSKU, Vcombo


class SupplierSerializer(serializers.ModelSerializer):
    """
    供应商
    """

    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierProductListSerializer(serializers.ModelSerializer):
    """
    供应商关联的产品
    """

    class Meta:
        model = SupplierProduct
        fields = "__all__"


class RegCountrySerializer(serializers.ModelSerializer):
    """
    注册国家
    """

    class Meta:
        model = RegCountry
        exclude = ('reg_product',)


class RegProductSerializer(serializers.ModelSerializer):
    """
    注册产品
    """
    # 注册国家信息
    reg_product_reg_country = RegCountrySerializer(many=True, required=False)

    class Meta:
        model = RegProduct
        fields = ('id', 'logistics_company', 'reg_length', 'reg_width', 'reg_heigth',
                  'reg_weight', 'reg_volume', 'is_active', 'reg_product_reg_country',)


class SupplierProductSerializer(serializers.ModelSerializer):
    """
    供应商产品(For 产品详情)
    """
    supplier = serializers.SerializerMethodField()
    buy_way = serializers.SerializerMethodField()

    # 获取供应商名称
    def get_supplier(self, obj):
        return obj.supplier.supplier_name

    # 获取供应商采购渠道
    def get_buy_way(self, obj):
        return obj.supplier.buy_way

    class Meta:
        model = SupplierProduct
        fields = ('id', 'buy_url', 'primary_supplier', 'create_time', 'supplier', 'buy_way')


class SupplierProductList2Serializer(serializers.ModelSerializer):
    """
    供应商产品(供应商管理产品列表)
    """
    sku = serializers.SerializerMethodField()
    cn_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    # 获取产品sku编码
    def get_sku(self, obj):
        return obj.product.sku

    # 获取产品名称
    def get_cn_name(self, obj):
        return obj.product.cn_name

    # 获取产品图片
    def get_image(self, obj):
        return obj.product.image if obj.product.image else ''

    class Meta:
        model = SupplierProduct
        fields = ('id', 'buy_url', 'primary_supplier', 'create_time', 'supplier', 'sku', 'cn_name', 'image')


class VskuSerializer(serializers.ModelSerializer):
    """
    虚拟sku
    """
    class Meta:
        model = Vsku
        fields = ('vsku',)


class ProductSerializer(serializers.ModelSerializer):
    """
    产品
    """
    # 产品注册信息
    product_reg_product = RegProductSerializer(many=True, required=False, read_only=True)
    # 供应商产品
    product_sup_product = SupplierProductSerializer(many=True, required=False, read_only=True)
    # 虚拟sku
    product_vsku = VskuSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'sku', 'cn_name', 'image', 'status', 'cost', 'create_time', 'en_name',
                  'length', 'width', 'heigth', 'weight', 'declared_value', 'url', 'is_battery',
                  'is_jack', 'is_brand', 'brand_name', 'brand_model', 'product_reg_product',
                  'product_sup_product', 'company', 'product_vsku')


class BaseProductSerializer(serializers.ModelSerializer):
    """
    获取产品基本信息，用于搜索产品
    """

    class Meta:
        model = Product
        fields = ('id', 'sku', 'cn_name', 'image', 'status', 'cost', 'create_time', 'en_name',
                  'length', 'width', 'heigth', 'weight', 'declared_value', 'url', 'is_battery',
                  'is_jack', 'is_brand', 'brand_name', 'brand_model')


class ComboSKUSerializer(serializers.ModelSerializer):
    """
    组合内产品
    """
    cn_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()

    # 获取产品名称
    def get_cn_name(self, obj):
        product = Product.objects.get(sku=obj.sku)
        return product.cn_name

    # 获取产品图片
    def get_image(self, obj):
        product = Product.objects.get(sku=obj.sku)
        return product.image if product.image else ''

    # 获取产品id
    def get_product_id(self, obj):
        product = Product.objects.get(sku=obj.sku)
        return product.id

    class Meta:
        model = ComboSKU
        fields = ('id', 'sku', 'quantity', 'cn_name', 'image', 'product_id')


class VcomboSerializer(serializers.ModelSerializer):
    """
    组合虚拟sku
    """
    class Meta:
        model = Vcombo
        fields = ('vsku',)


class ComboPackSerializer(serializers.ModelSerializer):
    """
    组合产品
    """
    # 组合内产品
    combo_pack_sku = ComboSKUSerializer(many=True, required=False, read_only=True)
    # 组合内产品
    combo_pack_vcombo = VcomboSerializer(many=True, required=False, read_only=True)

    weight = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    # 获取组合内产品总重量
    def get_weight(self, obj):
        comboSKU = ComboSKU.objects.filter(combo_pack=obj)
        total_weight = 0
        for i in comboSKU:
            product = Product.objects.get(sku=i.sku)
            if product.weight:
                total_weight += product.weight*i.quantity
        return total_weight if total_weight else ''

    # 获取组合内产品总成本
    def get_cost(self, obj):
        comboSKU = ComboSKU.objects.filter(combo_pack=obj)
        total_cost = 0
        for i in comboSKU:
            product = Product.objects.get(sku=i.sku)
            if product.cost:
                total_cost += product.cost*i.quantity
        return total_cost if total_cost else ''

    class Meta:
        model = ComboPack
        fields = ('id', 'combo_code', 'combo_name', 'weight', 'cost', 'company', 'combo_pack_sku', 'combo_pack_vcombo', 'combo_status', 'create_time')