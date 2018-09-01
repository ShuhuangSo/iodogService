from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import LogisticsAuth, ThirdWarehouse
from .serializers import LogisticsAuthSerializer, ThirdWarehouseSerializer
from warehouse.models import Warehouse


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class LogisticsAuthViewSet(mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    物流平台授权
    """
    queryset = LogisticsAuth.objects.all()
    serializer_class = LogisticsAuthSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return LogisticsAuth.objects.filter(company=self.request.user.company)


class ThirdWarehouseViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    物流仓库列表
    """
    queryset = ThirdWarehouse.objects.all()
    serializer_class = ThirdWarehouseSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('logistics_company', 'country_code')  # 配置过滤字段
    search_fields = ('wh_code', 'wh_name')  # 配置搜索字段
    ordering_fields = ('logistics_company',)  # 配置排序字段

    def get_queryset(self):
        # 过滤仓库状态为true的仓库
        return ThirdWarehouse.objects.filter(is_active=True)

    # 重写create方法,添加仓库到用户公司
    def create(self, request, *args, **kwargs):
        data = request.data
        wid = data['id']
        company = self.request.user.company

        third_warehouse = ThirdWarehouse.objects.get(id=wid)
        # 如果仓库已存在，不添加
        queryset = Warehouse.objects.filter(wh_id=third_warehouse.wh_id).count()
        if queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        warehouse = Warehouse()
        warehouse.company = company
        warehouse.wh_code = third_warehouse.wh_code
        warehouse.wh_id = third_warehouse.wh_id
        warehouse.wh_name = third_warehouse.wh_name
        warehouse.wh_address = third_warehouse.wh_address
        warehouse.country_code = third_warehouse.country_code
        warehouse.logistics_company = third_warehouse.logistics_company
        warehouse.wh_type = 'OS'
        warehouse.save()

        return Response(status=status.HTTP_200_OK)