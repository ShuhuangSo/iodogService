from django.contrib import admin
from .models import RefillPromote, RefillSetting

# Register your models here.


@admin.register(RefillPromote)
class RefillPromoteAdmin(admin.ModelAdmin):
    list_display = ['buy_qty', 't_weight', 'warehouse_stock', 'warehouse']
    list_filter = ['warehouse']


@admin.register(RefillSetting)
class RefillSettingAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'stock_days', 'min_buy', 'auto_carry', 'is_auto_calc', 'remind_weight',
                    'remind_sku_qty', 'remind_total_qty', 'company']
    list_filter = ['is_active', 'is_auto_calc']
