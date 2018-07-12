"""iodogservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    # 2. Add a URL to urlpatterns/:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token

from product.views import SupplierListViewSet, SupplierBulkOperation, CheckSupplierName, ProductViewSet, RegProductView
from product.views import SupplierProductViewSet, SetDefaultSupplierView, CheckVskuView, ComboPackViewSet, BaseProductViewSet

from rest_framework.routers import DefaultRouter
router = DefaultRouter()

# 注册供应商列表url
router.register(r'api/suppliers', SupplierListViewSet, base_name='suppliers')
router.register(r'api/products', ProductViewSet, base_name='products')
router.register(r'api/supplier-product', SupplierProductViewSet, base_name='supplier-product')
router.register(r'api/combopacks', ComboPackViewSet, base_name='combopacks')
router.register(r'api/base-products', BaseProductViewSet, base_name='api/base-products')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='跨境狗API文档')),
    url(r'^', include(router.urls)),
    url(r'^api/login/', obtain_jwt_token),

    # 供应商批量操作
    url(r'^api/suppliers-bulk/', SupplierBulkOperation.as_view(), name='suppliers-bulk'),
    # 检查供应商名称
    url(r'^api/suppliers-check/', CheckSupplierName.as_view(), name='suppliers-check'),
    # 新增注册产品/添加注册国家
    url(r'^api/reg-product/', RegProductView.as_view(), name='reg-product'),
    # 设置默认供应商
    url(r'^api/set-default-supplier/', SetDefaultSupplierView.as_view(), name='set-default-supplier'),
    # 检查虚拟sku是否存在
    url(r'^api/vsku-check/', CheckVskuView.as_view(), name='vsku-check'),

]