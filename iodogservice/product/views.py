from .serializers import SupplierSerializer, ProductSerializer, SupplierProductListSerializer, ComboPackSerializer, BaseProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from django.db.models import Q
import json

from .models import Supplier, Product, RegProduct, RegCountry, SupplierProduct, Vsku, ComboPack, Vcombo, ComboSKU

# Create your views here.


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class SupplierListViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
        供应商列表,分页,过滤,搜索(供应商名称),排序
    create:
        供应商新增
    retrieve:
        供应商详情页
    update:
        供应商修改
    destroy:
        供应商删除
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('status', 'buy_way')  # 配置过滤字段
    search_fields = ('supplier_name',)  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return Supplier.objects.filter(company=self.request.user.company)

    # 重写create方法
    def create(self, request, *args, **kwargs):
        data = request.data
        # 获取当前用户的公司
        data['company'] = self.request.user.company.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SupplierBulkOperation(APIView):
    """
    批量删除/修改供应商
    """
    def post(self, request, *args, **kwargs):
        """
        批量删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data  # 获取删除id
        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = Supplier.objects.filter(q)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        批量启用/停用供应商
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data['ids']
        supplier_status = self.request.data['status']

        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = Supplier.objects.filter(q)
        queryset.update(status=supplier_status)
        return Response(status=status.HTTP_200_OK)


class CheckSupplierName(APIView):
    """
    检查供应商名称是否存在
    """

    def post(self, request, *args, **kwargs):

        queryset = Supplier.objects.filter(company=self.request.user.company).filter(supplier_name=self.request.data).count()
        if (queryset):
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        产品列表,分页,过滤,搜索,排序
    create:
        产品新增
    retrieve:
        产品详情页
    update:
        产品修改
    destroy:
        产品删除
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('status', 'product_reg_product__reg_product_reg_country__reg_status')  # 配置过滤字段
    search_fields = ('sku', 'cn_name')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return Product.objects.filter(company=self.request.user.company)

    # 重写create方法
    def create(self, request, *args, **kwargs):
        data = request.data
        # 获取当前用户的公司
        data['company'] = self.request.user.company.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 重写update方法
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        product_id = self.request.data['id']  # 获取产品id
        add_vsku = self.request.data['add_vsku'] # 获取新增虚拟sku
        remove_vsku = self.request.data['remove_vsku'] # 删除虚拟sku

        # 删除虚拟sku
        if remove_vsku:
            q = Q()
            q.connector = 'OR'
            for i in remove_vsku:
                q.children.append(('vsku', i))
            queryset = Vsku.objects.filter(product=product_id).filter(q)
            queryset.delete()

        # 批量增加虚拟sku
        if add_vsku:
            add_list = []
            p = Product.objects.get(id=product_id)
            for i in add_vsku:
                add_list.append(Vsku(vsku=i, product=p))
            Vsku.objects.bulk_create(add_list)

        return Response(serializer.data)


class ProductBulkOperation(APIView):
    """
    批量删除/修改产品
    """
    def post(self, request, *args, **kwargs):
        """
        批量删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data  # 获取删除id
        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = Product.objects.filter(q)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        批量编辑：修改产品状态
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data['ids']
        product_status = self.request.data['status']

        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = Product.objects.filter(q)
        queryset.update(status=product_status)
        return Response(status=status.HTTP_200_OK)


class ProductBulkImport(APIView):
    """
        批量导入产品
        """

    def post(self, request, *args, **kwargs):
        """
        批量导入产品
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        data = self.request.data  # 获取产品数据
        company = self.request.user.company
        key = ['sku', 'cn_name', 'cost', 'supplier', 'en_name', 'declared_value', 'length', 'width', 'heigth', 'weight', 'url', 'is_battery', 'is_jack', 'is_brand', 'brand_name', 'brand_model']
        # 将数据转为对应的字典,从第二行开始
        before_list_p = [dict(zip(key, v)) for v in data[1:]]
        list_p = []
        list_sku = []
        # 检查数据有效性
        err_list = []
        for i in before_list_p:
            if i.__contains__('sku') and i.__contains__('cn_name') and i.__contains__('cost'):
                if not i['sku'] or not i['cn_name'] or not i['cost']:
                    err_item = {}
                    err_item.update({'sku': i['sku']})
                    err_item.update({'msg': '必填项出错'})
                    err_list.append(err_item)
                    continue

                is_exist = Product.objects.filter(sku=i['sku'].strip()).count()
                if is_exist:
                    err_item = {}
                    err_item.update({'sku': i['sku']})
                    err_item.update({'msg': '该sku已存在'})
                    err_list.append(err_item)
                    continue

                if i['sku'].strip() in list_sku:
                    err_item = {}
                    err_item.update({'sku': i['sku']})
                    err_item.update({'msg': '该sku重复导入'})
                    err_list.append(err_item)
                    continue
                list_p.append(i)
                list_sku.append(i['sku'].strip())
            else:
                err_item = {}
                err_item.update({'msg': '模板表格出错'})
                err_list.append(err_item)

        fail_count = len(err_list)
        success_count = len(list_p)
        all_data = {}
        all_data.update({'err_list': err_list})
        all_data.update({'fail_count': fail_count})
        all_data.update({'success_count': success_count})
        if not list_p:
            return Response(all_data, status=status.HTTP_201_CREATED)

        add_list = []
        # sku对应的供应商表
        supplier_dic = {}
        for i in list_p:
            if i['supplier']:
                if i['supplier'].strip() != '':
                    supplier_dic[i['sku'].strip()] = i['supplier'].strip()
            if i.__contains__('sku'):
                sku = i['sku'].strip()
            else:
                sku = None
            if i.__contains__('cn_name'):
                cn_name = i['cn_name'].strip() if i['cn_name'] else None
            else:
                cn_name = None
            if i.__contains__('cost'):
                cost = i['cost']
            else:
                cost = None
            if i.__contains__('en_name'):
                en_name = i['en_name'].strip() if i['en_name'] else None
            else:
                en_name = None
            if i.__contains__('declared_value'):
                declared_value = i['declared_value']
            else:
                declared_value = None
            if i.__contains__('length'):
                length = i['length']
            else:
                length = None
            if i.__contains__('width'):
                width = i['width']
            else:
                width = None
            if i.__contains__('heigth'):
                heigth = i['heigth']
            else:
                heigth = None
            if i.__contains__('weight'):
                weight = i['weight']
            else:
                weight = None
            if i.__contains__('url'):
                url = i['url'].strip()
            else:
                url = None
            if i.__contains__('is_battery'):
                is_battery = True if i['is_battery'] == '1' else False
            else:
                is_battery = None
            if i.__contains__('is_jack'):
                is_jack = True if i['is_jack'] == '1' else False
            else:
                is_jack = None
            if i.__contains__('is_brand'):
                is_brand = True if i['is_brand'] == '1' else False
            else:
                is_brand = None
            if i.__contains__('brand_name'):
                brand_name = i['brand_name'].strip() if i['brand_name'] else None
            else:
                brand_name = None
            if i.__contains__('brand_model'):
                brand_model = i['brand_model'].strip() if i['brand_model'] else None
            else:
                brand_model = None
            add_list.append(Product(
                sku=sku,
                cn_name=cn_name if cn_name else '',
                cost=cost,
                en_name=en_name if en_name else '',
                declared_value=declared_value,
                length=length if length else None,
                width=width if width else None,
                heigth=heigth if heigth else None,
                weight=weight if weight else None,
                url=url if url else '',
                is_battery=True if is_battery == 1 else False,
                is_jack=True if is_jack == 1 else False,
                is_brand=True if is_brand == 1 else False,
                brand_name=brand_name if brand_name else '',
                brand_model=brand_model if brand_model else '',
                company=company
            ))
        Product.objects.bulk_create(add_list)

        supplier_add_list = []
        for k, v in supplier_dic.items():
            queryset = Supplier.objects.filter(supplier_name=v).count()
            # 如果供应商不存在，则创建供应商
            if not queryset:
                new_supplier = Supplier()
                new_supplier.company = company
                new_supplier.supplier_name = v
                new_supplier.save()
            product = Product.objects.get(sku=k)
            supplier = Supplier.objects.get(supplier_name=v)
            supplier_add_list.append(SupplierProduct(product=product, supplier=supplier, primary_supplier=True))
        SupplierProduct.objects.bulk_create(supplier_add_list)

        return Response(all_data, status=status.HTTP_201_CREATED)


class RegProductView(APIView):
    """
    新增注册产品/添加注册国家
    """
    def post(self, request, *args, **kwargs):
        product_id = request.data['product']
        product = Product.objects.get(id=product_id)
        # 产品是否已经注册
        is_reg = RegProduct.objects.filter(product=product_id).count()
        # 产品如果未注册物流公司,则先注册物流公司
        if not is_reg:
            reg_product = RegProduct()
            reg_product.logistics_company = request.data['logistics_company']
            reg_product.product = product
            reg_product.save()

        # 注册国家
        reg_product = RegProduct.objects.get(product=product)
        reg_country = RegCountry()
        reg_country.country_code = request.data['country_code']
        reg_country.import_value = request.data['import_value']
        reg_country.reg_status = 'REGING'
        reg_country.reg_product = reg_product
        reg_country.save()

        return Response(status=status.HTTP_201_CREATED)


class RegProductBulkOperation(APIView):
    """
    批量新增注册产品/添加注册国家
    """
    def post(self, request, *args, **kwargs):
        product_ids = request.data['product']
        for product_id in product_ids:
            product = Product.objects.get(id=product_id)
            # 产品是否已经注册
            is_reg = RegProduct.objects.filter(product=product_id).count()
            # 产品如果未注册物流公司,则先注册物流公司
            if not is_reg:
                reg_product = RegProduct()
                reg_product.logistics_company = request.data['logistics_company']
                reg_product.product = product
                reg_product.save()
            reg_product = RegProduct.objects.get(product=product)

            is_country_reg = RegCountry.objects.filter(reg_product=reg_product).filter(country_code=request.data['country_code']).count()
            # 检查该国家没有注册过，才进行注册
            if not is_country_reg:
                # 注册国家
                reg_country = RegCountry()
                reg_country.country_code = request.data['country_code']
                reg_country.import_value = request.data['import_value']
                reg_country.reg_status = 'REGING'
                reg_country.reg_product = reg_product
                reg_country.save()

        return Response(status=status.HTTP_201_CREATED)


class SupplierProductViewSet(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """
    供应商产品
    """
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductListSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    # filter_fields = ('status', 'buy_way')  # 配置过滤字段
    # search_fields = ('supplier_name',)  # 配置搜索字段
    # ordering_fields = ('create_time',)  # 配置排序字段


class SetDefaultSupplierView(APIView):
    """
    设置默认供应商
    """
    def post(self, request, *args, **kwargs):
        set_id = request.data['set_id']
        remove_id = request.data['remove_id']
        # 将远默认供应商去除
        if remove_id:
            SupplierProduct.objects.filter(id=remove_id).update(primary_supplier=False)
        # 设置新的默认供应商
        if set_id:
            SupplierProduct.objects.filter(id=set_id).update(primary_supplier=True)

        return Response(status=status.HTTP_200_OK)


class CheckVskuView(APIView):
    """
    检查虚拟sku(包含组合虚拟sku)是否存在
    """

    def post(self, request, *args, **kwargs):

        vsku = self.request.data

        # 先检查该虚拟sku是否存在
        vsku_queryset = Vsku.objects.filter(vsku=vsku)
        if vsku_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in vsku_queryset:
                if i.product.company == self.request.user.company:
                    return Response(status=status.HTTP_200_OK)

        # 检查该虚拟sku是否与产品sku相同
        sku_queryset = Product.objects.filter(sku=vsku)
        if sku_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in sku_queryset:
                if i.company == self.request.user.company:
                    return Response(status=status.HTTP_200_OK)

        # 检查该虚拟sku是否与组合sku相同
        combo_queryset = ComboPack.objects.filter(combo_code=vsku)
        if combo_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in combo_queryset:
                if i.company == self.request.user.company:
                    return Response(status=status.HTTP_200_OK)

        # 检查该虚拟sku是否与虚拟组合sku相同
        vcombo_queryset = Vcombo.objects.filter(vsku=vsku)
        if vcombo_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in vcombo_queryset:
                if i.combo_pack.company == self.request.user.company:
                    return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ComboPackViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    组合产品
    """
    queryset = ComboPack.objects.all()
    serializer_class = ComboPackSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('combo_status', )  # 配置过滤字段
    search_fields = ('^combo_code', 'combo_name', '^combo_pack_sku__sku')  # 配置搜索字段

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return ComboPack.objects.filter(company=self.request.user.company)

    # 重写create方法
    def create(self, request, *args, **kwargs):
        data = request.data
        # 获取当前用户的公司
        company = self.request.user.company

        v_combo = data['combo_pack_vcombo']
        combo_sku = data['combo_pack_sku']

        # 增加组合sku
        if data:
            combo_pack = ComboPack()
            combo_pack.combo_code = request.data['combo_code']
            combo_pack.combo_name = request.data['combo_name']
            combo_pack.company = company
            combo_pack.save()
        new_combo_pack = ComboPack.objects.get(combo_code=data['combo_code'])

        # 批量增加组合虚拟sku
        if v_combo:
            v_add_list = []
            for i in v_combo:
                v_add_list.append(Vcombo(vsku=i, combo_pack=new_combo_pack))
            Vcombo.objects.bulk_create(v_add_list)

        # 批量增加组合内sku
        if combo_sku:
            sku_add_list = []
            for i in combo_sku:
                sku_add_list.append(ComboSKU(sku=i['sku'], quantity=i['quantity'], combo_pack=new_combo_pack))
            ComboSKU.objects.bulk_create(sku_add_list)

        return Response(status=status.HTTP_201_CREATED)

    # 重写update方法
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        combo_id = self.request.data['id']  # 获取组合产品id
        add_vsku = self.request.data['add_vsku']  # 获取新增虚拟sku
        remove_vsku = self.request.data['remove_vsku']  # 删除虚拟sku
        add_combo_sku = self.request.data['add_combo_sku']  # 新增组合内sku
        edit_combo_sku = self.request.data['edit_combo_sku']  # 编辑组合内sku
        remove_combo_sku = self.request.data['remove_combo_sku']  # 删除组合内sku

        # 删除组合虚拟sku
        if remove_vsku:
            q = Q()
            q.connector = 'OR'
            for i in remove_vsku:
                q.children.append(('vsku', i))
            queryset = Vcombo.objects.filter(combo_pack=combo_id).filter(q)
            queryset.delete()

        # 批量增加组合虚拟sku
        if add_vsku:
            add_list = []
            cp = ComboPack.objects.get(id=combo_id)
            for i in add_vsku:
                add_list.append(Vcombo(vsku=i, combo_pack=cp))
            Vcombo.objects.bulk_create(add_list)

        # 删除组合sku
        if remove_combo_sku:
            q = Q()
            q.connector = 'OR'
            for i in remove_combo_sku:
                q.children.append(('sku', i))
            queryset = ComboSKU.objects.filter(combo_pack=combo_id).filter(q)
            queryset.delete()

        # 批量增加组合sku
        if add_combo_sku:
            combosku_add_list = []
            cp = ComboPack.objects.get(id=combo_id)
            for i in add_combo_sku:
                combosku_add_list.append(ComboSKU(sku=i['sku'], quantity=i['quantity'], combo_pack=cp))
            ComboSKU.objects.bulk_create(combosku_add_list)

        # 修改组合sku数量
        if edit_combo_sku:
            for i in edit_combo_sku:
                ComboSKU.objects.filter(combo_pack=combo_id).filter(sku=i['sku']).update(quantity=i['quantity'])

        return Response(serializer.data)


class ComboBulkOperation(APIView):
    """
    批量删除/修改组合
    """
    def post(self, request, *args, **kwargs):
        """
        批量删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data  # 获取删除id
        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = ComboPack.objects.filter(q)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        批量启用/停用组合
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ids = self.request.data['ids']
        combo_status = self.request.data['combo_status']

        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        queryset = ComboPack.objects.filter(q)
        queryset.update(combo_status=combo_status)
        return Response(status=status.HTTP_200_OK)


class BaseProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取产品基本信息，用于搜索产品
    """
    queryset = Product.objects.all()
    serializer_class = BaseProductSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索
    filter_fields = ('sku',)  # 配置过滤字段
    search_fields = ('^sku', 'cn_name')  # 配置搜索字段

    def get_queryset(self):
        # 获取当前用户所在公司的数据
        return Product.objects.filter(company=self.request.user.company)