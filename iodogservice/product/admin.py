from django.contrib import admin


from .models import Supplier, SupplierProduct, Product, Vsku, RegProduct, RegCountry
from .models import ComboPack, ComboSKU, Vcombo

# Register your models here.


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'buy_way', 'address', 'store_url', 'company', 'create_time']
    list_filter = ['buy_way']
    search_fields = ['supplier_name', 'qq', 'phone']


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ['primary_supplier', 'buy_url', 'create_time', 'product', 'supplier']
    list_filter = ['primary_supplier', 'supplier']
    search_fields = ['supplier', 'product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'cn_name', 'status', 'create_time', 'company']
    list_filter = ['status', 'company']
    search_fields = ['sku', 'cn_name']


@admin.register(Vsku)
class VskuAdmin(admin.ModelAdmin):
    list_display = ['vsku', 'product']
    search_fields = ['vsku']


@admin.register(RegProduct)
class RegProductAdmin(admin.ModelAdmin):
    list_display = ['logistics_company', 'reg_length', 'reg_width', 'reg_heigth', 'reg_weight', 'reg_volume', 'is_active']
    list_filter = ['logistics_company', 'is_active']
    search_fields = ['product']


@admin.register(RegCountry)
class RegCountryAdmin(admin.ModelAdmin):
    list_display = ['country_code', 'import_value', 'import_rate', 'reg_status', 'reg_product']
    list_filter = ['country_code', 'reg_status']
    search_fields = ['reg_product']


@admin.register(ComboPack)
class ComboPackAdmin(admin.ModelAdmin):
    list_display = ['combo_code', 'combo_name', 'create_time', 'company']
    list_filter = ['company']
    search_fields = ['combo_code', 'combo_name']


@admin.register(ComboSKU)
class ComboSKUAdmin(admin.ModelAdmin):
    list_display = ['sku', 'quantity', 'combo_pack']
    search_fields = ['sku']


@admin.register(Vcombo)
class VcomboAdmin(admin.ModelAdmin):
    list_display = ['vsku', 'combo_pack']
    search_fields = ['vsku']
