from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from .models import LogisticsAuth, ThirdWarehouse
from warehouse.models import Warehouse


class LogisticsAuthSerializer(serializers.ModelSerializer):
    """
    物流平台授权列表
    """
    exp_time = serializers.SerializerMethodField()

    # 获取过期时间，18个月
    def get_exp_time(self, obj):
        delta = relativedelta(months=18)
        return obj.auth_time + delta

    class Meta:
        model = LogisticsAuth
        fields = ('id', 'logistics_code', 'logistics_company', 'auth_status', 'auth_time', 'exp_time',
                  'app_key', 'token', 'auth_link')


class ThirdWarehouseSerializer(serializers.ModelSerializer):
    """
    物流仓库列表
    """
    is_added = serializers.SerializerMethodField()

    # 获取该仓库是否已经添加
    def get_is_added(self, obj):
        queryset = Warehouse.objects.filter(wh_id=obj.wh_id).count()
        return True if queryset else False

    class Meta:
        model = ThirdWarehouse
        fields = ('id', 'logistics_company', 'wh_code', 'wh_name', 'wh_address',
                  'country_code', 'is_active', 'is_added')