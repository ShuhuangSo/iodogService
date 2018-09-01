from django.contrib import admin
from .models import LogisticsAuth, DevelopAuth, ThirdWarehouse, ThirdDelivery

# Register your models here.


@admin.register(LogisticsAuth)
class LogisticsAuthAdmin(admin.ModelAdmin):
    list_display = ['logistics_code', 'logistics_company', 'app_key', 'token', 'auth_status', 'auth_time', 'company', 'auth_link']
    list_filter = ['auth_status']
    search_fields = ['logistics_company', 'app_key', 'token']


@admin.register(DevelopAuth)
class DevelopAuthAdmin(admin.ModelAdmin):
    list_display = ['api_code', 'api_name', 'client_id', 'client_secret', 'dp_code']
    search_fields = ['api_name', 'client_id', 'client_secret']


@admin.register(ThirdWarehouse)
class ThirdWarehouseAdmin(admin.ModelAdmin):
    list_display = ['logistics_company', 'wh_code', 'wh_id', 'wh_name', 'country_code', 'is_active']
    list_filter = ['logistics_company', 'country_code', 'is_active']
    search_fields = ['wh_code', 'wh_id', 'wh_name']


@admin.register(ThirdDelivery)
class ThirdDeliveryAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'delivery_way', 'delivery_id', 'is_door_number', 'wh_id', 'is_active']
    list_filter = ['is_door_number', 'is_active']
    search_fields = ['product_code', 'delivery_way', 'delivery_id', 'wh_id']