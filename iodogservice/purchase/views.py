from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import RefillSetting, RefillPromote
from warehouse.models import Warehouse, WarehouseStock
from product.models import Product
from .serializers import RefillPromoteSerializer, RefillSettingSerializer


class CalcRefillPromote(APIView):
    """
    计算补货推荐
    """

    def get(self, request, *args, **kwargs):
        company = self.request.user.company
        queryset = RefillSetting.objects.filter(company=company).count()
        if not queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # 取出补货设置信息
        rf_setting = RefillSetting.objects.get(company=company)

        # 列出该公司下激活的海外仓仓库
        warehouses = Warehouse.objects.filter(company=company, is_active=True, wh_type='OS')
        for i in warehouses:
            # 清除旧的补货推荐数据
            RefillPromote.objects.filter(warehouse=i).delete()

            # 取出该仓库下的库存商品数据
            queryset = WarehouseStock.objects.filter(warehouse=i)
            add_list = []
            for ws in queryset:
                stock_days = rf_setting.stock_days  # 备货库存天数
                avg_30 = ws.avg_sell_qty
                avg_15 = ws.avg_sell_qty15
                avg_7 = ws.avg_sell_qty7
                if not avg_30:
                    avg_30 = 0
                if not avg_15:
                    avg_15 = 0
                if not avg_7:
                    avg_7 = 0

                # 日均销量=30天日均×0.3 + 15天日均×0.4 + 7天日均×0.3
                avg = avg_30 * 0.3 + avg_15 * 0.4 + avg_7 * 0.3
                # 推荐采购数量: 日均销量×备货库存天数 - （可用库存 + 在途库存）
                buy_qty = int(avg * stock_days) - (ws.available_qty + ws.on_way_qty)

                # 向上取整
                if buy_qty >= rf_setting.min_buy:
                    if rf_setting.auto_carry:
                        for n in range(buy_qty, buy_qty + rf_setting.auto_carry):
                            if n % rf_setting.auto_carry == 0:
                                buy_qty = n
                                break
                            n += 1

                # 获取单项总重量
                products = Product.objects.filter(company=company, sku=ws.sku).count()
                t_weight = 0.0  # 单项重量
                if products:
                    product = Product.objects.filter(company=company).get(sku=ws.sku)
                    if product.weight:
                        t_weight = product.weight / 1000 * buy_qty

                # 超过最低采购数量的才保存
                if buy_qty >= rf_setting.min_buy:
                    add_list.append(RefillPromote(
                        buy_qty=buy_qty,
                        t_weight=t_weight,
                        warehouse_stock=ws,
                        warehouse=i
                    ))
            if add_list:
                RefillPromote.objects.bulk_create(add_list)

        return Response(status=status.HTTP_200_OK)


class RefillPromoteViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    补货推荐
    """
    queryset = RefillPromote.objects.all()
    serializer_class = RefillPromoteSerializer  # 序列化
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('warehouse',)  # 配置过滤字段
    search_fields = ('^sku', 'cn_name')  # 配置搜索字段
    ordering_fields = ('buy_qty',)  # 配置排序字段


class RefillSettingViewSet(mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    补货推荐设置
    """
    queryset = RefillSetting.objects.all()
    serializer_class = RefillSettingSerializer  # 序列化

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return RefillSetting.objects.filter(company=self.request.user.company)
