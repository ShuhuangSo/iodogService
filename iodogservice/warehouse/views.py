from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Warehouse
from .serializers import WarehouseSerializer


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class WarehouseViewSet(mixins.ListModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    仓库列表
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('logistics_company', 'is_active', 'wh_type')  # 配置过滤字段
    search_fields = ('wh_code', 'wh_name')  # 配置搜索字段
    ordering_fields = ('logistics_company',)  # 配置排序字段

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return Warehouse.objects.filter(company=self.request.user.company)