import django_filters
from rest_framework import filters

from .models import WarehouseStock


class WarehouseStockFilter(filters.FilterSet):
    """
    仓库库存过滤类
    """
    min_doi = django_filters.NumberFilter(name='doi', lookup_expr='gte')
    max_doi = django_filters.NumberFilter(name='doi', lookup_expr='lte')

    class Meta:
        model = WarehouseStock
        fields = ['is_return', 'is_onsale', 'warehouse', 'min_doi', 'max_doi']

