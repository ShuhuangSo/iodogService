from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import datetime
from random import choice

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


class AddLocalWarehouse(APIView):
    """
    新增本地仓库
    """

    def post(self, request, *args, **kwargs):
        data = self.request.data
        company = self.request.user.company
        wh_name = data['wh_name']
        wh_address = data['wh_address']
        return_name = data['return_name']
        return_phone = data['return_phone']
        return_address = data['return_address']
        post_name = data['post_name']
        post_phone = data['post_phone']
        post_address = data['post_address']

        # 检查该仓库名称是否已存在
        queryset = Warehouse.objects.filter(company=company).filter(wh_name=wh_name).count()
        if queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # 生成仓库编码
        now_time = datetime.datetime.now().strftime("%m%d%H")  # 生成月日时分
        seeds = "1234567890"
        random_num = ''
        for i in range(4):
            random_num += str(choice(seeds))
        code = 'LC%s%s' % (str(now_time), random_num)

        warehouse = Warehouse()
        warehouse.wh_id = code
        warehouse.wh_code = code
        warehouse.wh_name = wh_name
        warehouse.wh_address = wh_address
        warehouse.return_name = return_name
        warehouse.return_phone = return_phone
        warehouse.return_address = return_address
        warehouse.post_name = post_name
        warehouse.post_phone = post_phone
        warehouse.post_address = post_address
        warehouse.wh_type = 'LOCAL'
        warehouse.country_code = 'CN'
        warehouse.logistics_company = 'LOCAL'
        warehouse.company = company
        warehouse.save()

        return Response(status=status.HTTP_201_CREATED)