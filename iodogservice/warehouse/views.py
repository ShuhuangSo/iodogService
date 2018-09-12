from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
import datetime
from random import choice

from .models import Warehouse, Position, WarehouseStock
from .serializers import WarehouseSerializer, PositionSerializer, WarehouseStockSerializer


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


class PositionViewSet(mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """
    仓位列表
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('po_code', 'is_active', 'warehouse')  # 配置过滤字段
    search_fields = ('po_code',)  # 配置搜索字段
    ordering_fields = ('po_code',)  # 配置排序字段


class AddPosition(APIView):
    """
    添加仓位
    """

    def post(self, request, *args, **kwargs):
        data = self.request.data
        id = data['wh_id']
        codes = data['codes']

        new_codes = []
        warehouse = Warehouse.objects.get(id=id)

        # 检查仓位编码是否存在
        for i in codes:
            queryset = Position.objects.filter(warehouse=warehouse, po_code=i)
            if not queryset:
                new_codes.append(i)

        add_list = []
        for i in new_codes:
            add_list.append(Position(
                po_code=i,
                warehouse=warehouse
            ))
        Position.objects.bulk_create(add_list)

        return Response(status=status.HTTP_201_CREATED)


class UpdatePosition(APIView):
    """
    修改仓位
    """

    def post(self, request, *args, **kwargs):
        data = self.request.data
        id = data['wh_id']
        p = data['position']
        delete_list = data['delete_list']
        warehouse = Warehouse.objects.get(id=id)

        # 批量删除
        if delete_list:
            q = Q()
            q.connector = 'OR'
            for i in delete_list:
                q.children.append(('id', i))
            queryset = Position.objects.filter(warehouse=warehouse).filter(q)
            queryset.delete()

        # 如果仓位编码不一样，就修改
        for i in p:
            po_code = i['po_code']
            id = i['id']
            position = Position.objects.get(id=id)
            if position.po_code == po_code:
                continue
            queryset = Position.objects.filter(warehouse=warehouse, po_code=po_code)
            if queryset:
                continue
            Position.objects.filter(id=id).update(po_code=po_code)

        return Response(status=status.HTTP_200_OK)


class BulkUpdatePositionStatus(APIView):
    """
    修改仓位状态
    """

    def post(self, request, *args, **kwargs):
        data = self.request.data
        ids = data['ids']
        wh_id = data['wh_id']
        is_active = data['is_active']
        warehouse = Warehouse.objects.get(id=wh_id)

        if ids:
            q = Q()
            q.connector = 'OR'
            for i in ids:
                q.children.append(('id', i))
            queryset = Position.objects.filter(warehouse=warehouse).filter(q)
            queryset.update(is_active=is_active)

        return Response(status=status.HTTP_200_OK)


class WarehouseStockViewSet(mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """
    库存列表
    """
    queryset = WarehouseStock.objects.all()
    serializer_class = WarehouseStockSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('is_return', 'is_onsale', 'warehouse')  # 配置过滤字段
    search_fields = ('^sku', 'cn_name')  # 配置搜索字段
    ordering_fields = ('all_stock', 'available_qty', 'reserved_qty', 'on_way_qty', 'his_in_qty'
                       , 'his_sell_qty', 'avg_sell_qty', 'avg_stock', 'doi', 'create_time',
                       'avg_sell_qty15', 'avg_stock15', 'avg_sell_qty7', 'avg_stock7')  # 配置排序字段
