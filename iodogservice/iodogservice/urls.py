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
from django.views.static import serve
from django.conf import settings

from product.views import SupplierListViewSet, SupplierBulkOperation, CheckSupplierName, ProductViewSet, RegProductView
from product.views import SupplierProductViewSet, SetDefaultSupplierView, CheckVskuView, ComboPackViewSet, BaseProductViewSet
from product.views import ComboBulkOperation, ProductBulkOperation, RegProductBulkOperation, ProductBulkImport
from product.views import VskuBulkImport, ComboBulkImport, VcomboBulkImport, SupplierBulkImport, SupplierProductListViewSet
from product.views import SupplierProductBulkOperation, CheckSKU, ProductLabelPrint
from setting.views import LogisticsAuthViewSet

from rest_framework.routers import DefaultRouter
router = DefaultRouter()

# 产品库模块
router.register(r'api/suppliers', SupplierListViewSet, base_name='suppliers')
router.register(r'api/products', ProductViewSet, base_name='products')
router.register(r'api/supplier-product', SupplierProductViewSet, base_name='supplier-product')
router.register(r'api/supplier-product-list', SupplierProductListViewSet, base_name='supplier-product-list')
router.register(r'api/combopacks', ComboPackViewSet, base_name='combopacks')
router.register(r'api/base-products', BaseProductViewSet, base_name='api/base-products')

# 系统设置模块
router.register(r'api/logistics-auth', LogisticsAuthViewSet, base_name='api/logistics-auth')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='跨境狗API文档')),
    url(r'^', include(router.urls)),
    url(r'^api/login/', obtain_jwt_token),
    url(r'^upload/(?P<path>.*)$',  serve, {"document_root": settings.MEDIA_ROOT}),

    # 供应商批量操作
    url(r'^api/suppliers-bulk/', SupplierBulkOperation.as_view(), name='suppliers-bulk'),
    # 检查供应商名称
    url(r'^api/suppliers-check/', CheckSupplierName.as_view(), name='suppliers-check'),
    # 新增注册产品/添加注册国家
    url(r'^api/reg-product/', RegProductView.as_view(), name='reg-product'),
    # 批量操作新增注册产品/添加注册国家
    url(r'^api/reg-product-bulk/', RegProductBulkOperation.as_view(), name='reg-product-bulk'),
    # 设置默认供应商
    url(r'^api/set-default-supplier/', SetDefaultSupplierView.as_view(), name='set-default-supplier'),
    # 检查虚拟sku是否存在
    url(r'^api/vsku-check/', CheckVskuView.as_view(), name='vsku-check'),
    # 检查sku是否存在
    url(r'^api/sku-is-exist-check/', CheckSKU.as_view(), name='sku-is-exist-check'),
    # 组合sku批量操作
    url(r'^api/combopacks-bulk/', ComboBulkOperation.as_view(), name='combopacks-bulk'),
    # 产品批量操作
    url(r'^api/products-bulk/', ProductBulkOperation.as_view(), name='products-bulk'),
    # 供应商关联产品批量操作
    url(r'^api/supplier-products-bulk/', SupplierProductBulkOperation.as_view(), name='supplier-products-bulk'),
    # 产品批量导入
    url(r'^api/import-product/', ProductBulkImport.as_view(), name='import-product'),
    # 产品虚拟sku批量导入
    url(r'^api/import-vsku/', VskuBulkImport.as_view(), name='import-vsku'),
    # 组合产品批量导入
    url(r'^api/import-combo/', ComboBulkImport.as_view(), name='import-combo'),
    # 虚拟组合sku批量导入
    url(r'^api/import-vcombo/', VcomboBulkImport.as_view(), name='import-vcombo'),
    # 供应商批量导入
    url(r'^api/import-supplier/', SupplierBulkImport.as_view(), name='import-supplier'),
    # 打印产品标签
    url(r'^api/product-print/', ProductLabelPrint.as_view(), name='product-print'),

]
