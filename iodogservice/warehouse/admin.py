from django.contrib import admin

from .models import Warehouse, WarehouseStock, Position, DeliveryWay
# Register your models here.


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['wh_code', 'wh_id', 'wh_name', 'is_active', 'wh_type', 'country_code', 'logistics_company', 'company']
    list_filter = ['logistics_company', 'company', 'country_code', 'wh_type']
    search_fields = ['wh_code', 'wh_id', 'wh_name', 'wh_id']


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ['sku', 'all_stock', 'available_qty', 'reserved_qty', 'on_way_qty', 'doi', 'position', 'warehouse']
    list_filter = ['warehouse']
    search_fields = ['sku', 'position']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['po_code', 'is_active', 'warehouse']
    list_filter = ['warehouse', 'is_active']
    search_fields = ['po_code']


@admin.register(DeliveryWay)
class DeliveryWayAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'delivery_way', 'origin_name', 'delivery_id', 'wh_id', 'warehouse']
    list_filter = ['warehouse', 'is_door_number']
    search_fields = ['product_code', 'delivery_way', 'delivery_id', 'wh_id']