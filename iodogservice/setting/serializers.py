from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from .models import LogisticsAuth


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