from django.contrib import admin
from .models import LogisticsAuth, DevelopAuth

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