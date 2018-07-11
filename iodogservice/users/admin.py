from django.contrib import admin

from .models import UserProfile, Company


# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_superuser']
    search_fields = ['username']
    list_filter = ['is_superuser', 'is_staff', 'is_active', 'is_admin']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'create_time', 'expried_time']
    list_filter = ['is_active']
    search_fields = ['name']