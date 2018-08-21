from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import LogisticsAuth
from .serializers import LogisticsAuthSerializer


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