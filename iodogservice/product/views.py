from .serializers import SupplierSerializer, ProductSerializer, SupplierProductListSerializer, ComboPackSerializer, BaseProductSerializer
from .serializers import SupplierProductList2Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from django.db.models import Q
from .task import *
import base64

from .models import Supplier, Product, RegProduct, RegCountry, SupplierProduct, Vsku, ComboPack, Vcombo, ComboSKU
from setting.models import LogisticsAuth, DevelopAuth

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
        if ids:
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

        if ids:
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

    # 重写destroy方法
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查该sku是否在组合sku中
        query_combo_sku = ComboSKU.objects.filter(sku=instance.sku).count()
        if query_combo_sku:
            combo_sku = ComboSKU.objects.get(sku=instance.sku)
            # 如果存在，检查是否在本公司帐号中
            if combo_sku.combo_pack.company == self.request.user.company:
                err = {'err': '该sku已绑定在组合中，需要解除绑定才能删除'}
                return Response(err, status=status.HTTP_200_OK)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        err_list = []  # 错误信息列表
        if ids:
            vaild_ids = []  # 有效的id列表
            for i in ids:
                # 检查该sku是否在组合sku中
                product = Product.objects.get(id=i)
                query_combo_sku = ComboSKU.objects.filter(sku=product.sku).count()
                if query_combo_sku:
                    # 如果存在，检查是否在本公司帐号中
                    if product.company == self.request.user.company:
                        err_item = {}
                        err_item.update({'sku': product.sku})
                        err_item.update({'msg': '该sku已绑定在组合中，需要解除绑定才能删除'})
                        err_list.append(err_item)
                        continue
                vaild_ids.append(i)
            # 如果没有有效的id，则直接返回
            if len(vaild_ids) == 0:
                return Response(err_list, status=status.HTTP_200_OK)

            q = Q()
            q.connector = 'OR'
            for i in vaild_ids:
                q.children.append(('id', i))
            queryset = Product.objects.filter(q)
            queryset.delete()

        return Response(err_list, status=status.HTTP_200_OK)

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

        if ids:
            q = Q()
            q.connector = 'OR'
            for i in ids:
                q.children.append(('id', i))
            queryset = Product.objects.filter(q)
            queryset.update(status=product_status)
        return Response(status=status.HTTP_200_OK)


class CheckSKU(APIView):
    """
    检查SKU是否存在,是否已关联到供应商
    """

    def post(self, request, *args, **kwargs):
        data = self.request.data

        sku_queryset = Product.objects.filter(company=self.request.user.company).filter(sku=data['sku']).count()
        if not sku_queryset:
            err_msg = {'msg': '该SKU不存在!'}
            return Response(err_msg, status=status.HTTP_200_OK)

        product = Product.objects.filter(company=self.request.user.company).get(sku=data['sku'])
        sup_queryset = SupplierProduct.objects.filter(supplier=data['supplier']).filter(product=product).count()
        if sup_queryset:
            err_msg = {'msg': '该SKU已关联!'}
            return Response(err_msg, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


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

                # 检查sku是否存在
                st = SkuTool()
                is_exist = st.check_sku_exist(i['sku'].strip(), company)
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


class VskuBulkImport(APIView):
    """
    虚拟sku批量导入
    """

    def post(self, request, *args, **kwargs):
        """
        虚拟sku批量导入
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data  # 获取上传数据
        company = self.request.user.company

        err_list = []  # 错误列表
        all_sku_list = []
        # 检查sku是否存在
        st = SkuTool()
        for item in data[1:]:
            sku_is_exist = st.check_sku_exist(item[0].strip(), company)
            if not sku_is_exist:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': 'sku不存在'})
                err_list.append(err_item)
                continue
            sku_list = []
            sku_list.append(item[0].strip())
            for n in item[1:]:
                is_exist = st.check_sku_exist(n.strip(), company)
                if is_exist:
                    err_item = {}
                    err_item.update({'sku': n})
                    err_item.update({'msg': '该虚拟sku已存在'})
                    err_list.append(err_item)
                    continue
                sku_list.append(n.strip())
            if len(sku_list) > 1:
                all_sku_list.append(sku_list)

        # 批量新增虚拟sku
        add_list = []
        for item in all_sku_list:
            product = Product.objects.filter(company=company).get(sku=item[0])
            for n in item[1:]:
                add_list.append(Vsku(vsku=n, product=product))
        Vsku.objects.bulk_create(add_list)

        success_count = len(all_sku_list)
        fail_count = len(data)-1-success_count
        all_data = {}
        all_data.update({'err_list': err_list})
        all_data.update({'fail_count': fail_count})
        all_data.update({'success_count': success_count})
        return Response(all_data, status=status.HTTP_201_CREATED)


class ComboBulkImport(APIView):
    """
    组合批量导入
    """

    def post(self, request, *args, **kwargs):
        """
        组合批量导入
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data  # 获取上传数据
        company = self.request.user.company

        err_list = []  # 错误列表
        all_combopack_list = []
        # 检查组合sku是否存在
        st = SkuTool()
        combo_code_list = []
        for item in data[1:]:
            # 检查组合编码是否为空
            if not item[0]:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '组合编码不能为空'})
                err_list.append(err_item)
                continue

            # 检查组合编码是否重复
            if item[0] in combo_code_list:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '组合编码重复'})
                err_list.append(err_item)
                continue
            combo_code_list.append(item[0])

            combo_is_exist = st.check_sku_exist(item[0].strip(), company)
            # 检查组合编码是否存在
            if combo_is_exist:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '组合编码已存在'})
                err_list.append(err_item)
                continue

            # 检查组合内sku是否重复
            inside_sku_list = []
            inside_sku_duplicate = False
            for i in item[2:]:
                if item[2:].index(i) % 2 == 0:
                    inside_sku_list.append(i)
                    if item[2:].count(i) > 1:
                        inside_sku_duplicate = True
                        err_item = {}
                        err_item.update({'sku': i})
                        err_item.update({'msg': '组合内SKU重复'})
                        err_list.append(err_item)
            if inside_sku_duplicate:
                continue

            # 检查组合内sku是否存在
            inside_sku_invalid = False
            for i in inside_sku_list:
                if not i:
                    err_item = {}
                    err_item.update({'sku': i})
                    err_item.update({'msg': '组合内SKU为空'})
                    err_list.append(err_item)
                    inside_sku_invalid = True
                    break
                sku_is_exist = Product.objects.filter(sku=i, company=company).count()
                if not sku_is_exist:
                    err_item = {}
                    err_item.update({'sku': i})
                    err_item.update({'msg': '组合内SKU不存在'})
                    err_list.append(err_item)
                    inside_sku_invalid = True
            if inside_sku_invalid:
                continue

            # 获取组合内产品数据
            inside_skus = []
            for i in item[2:]:
                if item[2:].index(i) % 2 == 0:
                    inside_item = {}
                    inside_item.update({'sku': i})
                else:
                    inside_item.update({'quantity': i})
                    inside_skus.append(inside_item)

            # 获取组合编码和名称
            combo_info = {}
            combo_info.update({'combo_code': item[0]})
            combo_info.update({'combo_name': item[1]})

            # 生成有效数据列表
            one_group_data = {}
            one_group_data.update({'combo_pack': combo_info})
            one_group_data.update({'combo_skus': inside_skus})
            all_combopack_list.append(one_group_data)

        # 批量添加组合
        combo_add_list = []
        for i in all_combopack_list:
            combo_code = i['combo_pack']['combo_code']
            combo_name = i['combo_pack']['combo_name']
            combo_add_list.append(ComboPack(combo_code=combo_code, combo_name=combo_name, company=company))
        ComboPack.objects.bulk_create(combo_add_list)

        # 批量添加组合内sku
        for i in all_combopack_list:
            combo_skus = i['combo_skus']
            combo_code = i['combo_pack']['combo_code']
            combo_pack = ComboPack.objects.get(combo_code=combo_code, company=company)
            sku_add_list = []
            for n in combo_skus:
                sku = n['sku']
                quantity = n['quantity']
                sku_add_list.append(ComboSKU(sku=sku, quantity=quantity, combo_pack=combo_pack))
            ComboSKU.objects.bulk_create(sku_add_list)

        success_count = len(all_combopack_list)
        fail_count = len(data) - 1 - success_count
        all_data = {}
        all_data.update({'err_list': err_list})
        all_data.update({'fail_count': fail_count})
        all_data.update({'success_count': success_count})

        return Response(all_data, status=status.HTTP_201_CREATED)


class VcomboBulkImport(APIView):
    """
    虚拟组合sku批量导入
    """

    def post(self, request, *args, **kwargs):
        """
        虚拟组合sku批量导入
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data  # 获取上传数据
        company = self.request.user.company

        err_list = []  # 错误列表
        all_sku_list = []
        # 检查sku是否存在
        st = SkuTool()
        for item in data[1:]:
            # 检查组合编码是否为空
            if not item[0]:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '组合编码不能为空'})
                err_list.append(err_item)
                continue

            # 检查组合编码是否存在
            sku_is_exist = st.check_sku_exist(item[0].strip(), company)
            if not sku_is_exist:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '组合编码不存在'})
                err_list.append(err_item)
                continue

            sku_list = []
            sku_list.append(item[0].strip())
            for n in item[1:]:
                if not n:
                    continue
                is_exist = st.check_sku_exist(n.strip(), company)
                if is_exist:
                    err_item = {}
                    err_item.update({'sku': n})
                    err_item.update({'msg': '该虚拟sku已存在'})
                    err_list.append(err_item)
                    continue
                sku_list.append(n.strip())
            if len(sku_list) > 1:
                all_sku_list.append(sku_list)

        # 批量新增虚拟组合sku
        add_list = []
        for item in all_sku_list:
            combo_pack = ComboPack.objects.filter(company=company).get(combo_code=item[0])
            for n in item[1:]:
                add_list.append(Vcombo(vsku=n, combo_pack=combo_pack))
        Vcombo.objects.bulk_create(add_list)

        success_count = len(all_sku_list)
        fail_count = len(data)-1-success_count
        all_data = {}
        all_data.update({'err_list': err_list})
        all_data.update({'fail_count': fail_count})
        all_data.update({'success_count': success_count})
        return Response(all_data, status=status.HTTP_201_CREATED)


class SupplierBulkImport(APIView):
    """
    供应商批量导入
    """

    def post(self, request, *args, **kwargs):
        """
        供应商批量导入
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data  # 获取上传数据
        company = self.request.user.company

        err_list = []  # 错误列表
        all_supplier_list = []
        for item in data[1:]:
            # 检查供应商是否为空
            if not item[0]:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '供应商不能为空'})
                err_list.append(err_item)
                continue

            # 检查供应商是否存在
            supplier_is_exist = Supplier.objects.filter(supplier_name=item[0].strip(), company=company).count()
            if supplier_is_exist:
                err_item = {}
                err_item.update({'sku': item[0]})
                err_item.update({'msg': '该供应商已存在'})
                err_list.append(err_item)
                continue

            all_supplier_list.append(item)

        key = ['supplier_name', 'buy_way', 'store_url', 'address', 'qq', 'phone', 'note']
        # 将数据转为对应的字典,从第二行开始
        dict_list_s = [dict(zip(key, v)) for v in all_supplier_list]

        # 批量新增供应商
        add_list = []
        for i in dict_list_s:
            if i.__contains__('supplier_name'):
                supplier_name = i['supplier_name'].strip() if i['supplier_name'] else None
            if i.__contains__('buy_way'):
                buy_way = i['buy_way'].strip() if i['buy_way'] else None
            if i.__contains__('store_url'):
                store_url = i['store_url'].strip() if i['store_url'] else None
            if i.__contains__('address'):
                address = i['address'].strip() if i['address'] else None
            if i.__contains__('qq'):
                qq = i['qq'].strip() if i['qq'] else None
            if i.__contains__('phone'):
                phone = i['phone'].strip() if i['phone'] else None
            if i.__contains__('note'):
                note = i['note'].strip() if i['note'] else None

            add_list.append(Supplier(
                supplier_name=supplier_name,
                buy_way=buy_way if buy_way else '',
                store_url=store_url if store_url else '',
                address=address if address else '',
                qq=qq if qq else '',
                phone=phone if phone else '',
                note=note if note else '',
                company=company
            ))
        Supplier.objects.bulk_create(add_list)

        success_count = len(all_supplier_list)
        fail_count = len(data)-1-success_count
        all_data = {}
        all_data.update({'err_list': err_list})
        all_data.update({'fail_count': fail_count})
        all_data.update({'success_count': success_count})
        return Response(all_data, status=status.HTTP_201_CREATED)


class RegProductView(APIView):
    """
    新增注册产品/添加注册国家
    """
    def post(self, request, *args, **kwargs):
        product_id = request.data['product']
        company = self.request.user.company
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

        # 开始winit注册产品
        product_list = []
        p = {}
        p.update({'productCode': product.sku})  # 商品编码
        p.update({'specification': ''})  # 商品规格
        p.update({'chineseName': product.en_name})  # 中文名称
        p.update({'englishName': product.en_name})  # 英文名称
        p.update({'registeredWeight': product.weight})  # 注册重量(克/g)
        p.update({'fixedVolumeWeight': 'Y'})  # 重量体积是否固定，默认为Y
        p.update({'registeredLength': product.length})  # 注册长度(cm)
        p.update({'registeredWidth': product.width})  # 注册宽度(cm)
        p.update({'registeredHeight': product.heigth})  # 注册高度(cm)
        p.update({'branded': 'Y' if product.is_brand else 'N'})  # 是否有品牌
        p.update({'brandedName': product.brand_name})  # 品牌名称
        p.update({'model': product.brand_model})  # 品牌型号，当brandedname为Y时为必填
        p.update({'displayPageUrl': product.url})  # Ebay网页展示URL
        p.update({'remark': ''})  # 备注
        p.update({'exportCountry': 'CN'})  # 出口国家
        p.update({'inporCountry': request.data['country_code']})  # 进口国家
        p.update({'inportDeclaredvalue': float(request.data['import_value'])})  # 进口申报价
        p.update({'exportDeclaredvalue': float(request.data['import_value'])})  # 出口申报价
        p.update({'battery': 'Y' if product.is_battery else 'N'})  # 是否有电池
        product_list.append(p)

        # 调用task任务注册
        winit_reg_product.delay(product_list, company, request.data['country_code'])

        return Response(status=status.HTTP_201_CREATED)


class RegProductBulkOperation(APIView):
    """
    批量新增注册产品/添加注册国家
    """
    def post(self, request, *args, **kwargs):
        product_ids = request.data['product']
        company = self.request.user.company

        product_list = []

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

                # 开始winit注册产品
                p = {}
                p.update({'productCode': product.sku})  # 商品编码
                p.update({'specification': ''})  # 商品规格
                p.update({'chineseName': product.en_name})  # 中文名称
                p.update({'englishName': product.en_name})  # 英文名称
                p.update({'registeredWeight': product.weight})  # 注册重量(克/g)
                p.update({'fixedVolumeWeight': 'Y'})  # 重量体积是否固定，默认为Y
                p.update({'registeredLength': product.length})  # 注册长度(cm)
                p.update({'registeredWidth': product.width})  # 注册宽度(cm)
                p.update({'registeredHeight': product.heigth})  # 注册高度(cm)
                p.update({'branded': 'Y' if product.is_brand else 'N'})  # 是否有品牌
                p.update({'brandedName': product.brand_name})  # 品牌名称
                p.update({'model': product.brand_model})  # 品牌型号，当brandedname为Y时为必填
                p.update({'displayPageUrl': product.url})  # Ebay网页展示URL
                p.update({'remark': ''})  # 备注
                p.update({'exportCountry': 'CN'})  # 出口国家
                p.update({'inporCountry': request.data['country_code']})  # 进口国家
                p.update({'inportDeclaredvalue': float(request.data['import_value'])})  # 进口申报价
                p.update({'exportDeclaredvalue': float(request.data['import_value'])})  # 出口申报价
                p.update({'battery': 'Y' if product.is_battery else 'N'})  # 是否有电池
                product_list.append(p)

        # 调用task任务注册
        if product_list:
            winit_reg_product.delay(product_list, company, request.data['country_code'])

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


class SupplierProductListViewSet(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    """
    供应商关联产品列表
    """
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductList2Serializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('primary_supplier', 'supplier')  # 配置过滤字段
    search_fields = ('^product__sku', 'product__cn_name')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段


class SupplierProductBulkOperation(APIView):
    """
    批量删除/修改供应商关联产品
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

        if ids:
            q = Q()
            q.connector = 'OR'
            for i in ids:
                q.children.append(('id', i))
            queryset = SupplierProduct.objects.filter(q)
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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


class SkuTool(object):
    """
    检查sku是否存在，检查包括sku，虚拟sku，组合sku，虚拟组合sku
    """

    def check_sku_exist(self, to_check_sku, company):

        # 先检查该虚拟sku是否存在
        vsku_queryset = Vsku.objects.filter(vsku=to_check_sku)
        if vsku_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in vsku_queryset:
                if i.product.company == company:
                    return True

        # 检查该虚拟sku是否与产品sku相同
        sku_queryset = Product.objects.filter(sku=to_check_sku)
        if sku_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in sku_queryset:
                if i.company == company:
                    return True

        # 检查该虚拟sku是否与组合sku相同
        combo_queryset = ComboPack.objects.filter(combo_code=to_check_sku)
        if combo_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in combo_queryset:
                if i.company == company:
                    return True

        # 检查该虚拟sku是否与虚拟组合sku相同
        vcombo_queryset = Vcombo.objects.filter(vsku=to_check_sku)
        if vcombo_queryset:
            # 如果存在，再检查是否在当前公司帐号下
            for i in vcombo_queryset:
                if i.combo_pack.company == company:
                    return True
        return False


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

        if ids:
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

        if ids:
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


class ProductLabelPrint(APIView):
    """
    打印产品标签(万邑通)
    """
    def post(self, request, *args, **kwargs):
        """
        打印标签
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 获取当前用户的公司
        company = self.request.user.company

        data1 = self.request.data[0]
        data2 = self.request.data[1]
        data3 = self.request.data[2]

        single_items = data1['singleItems']
        label_type = data2['labelType']
        made_in = data3['madeIn']

        queryset = LogisticsAuth.objects.filter(company=company).count()
        if not queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        logis_auth = LogisticsAuth.objects.get(company=company)
        app_key = logis_auth.app_key  # 万邑联账户
        token = logis_auth.token  # 万邑通账户token

        develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
        client_id = develop_auth.client_id  # 开发账户id
        client_secret = develop_auth.client_secret  # 开发账户密钥
        platform = develop_auth.dp_code  # 开发账号代码

        # 调用winit打印产品接口
        win_it = WinIt(token, client_secret, client_id, app_key, platform)
        res = win_it.print_product_label(single_items, label_type, made_in)

        res = json.loads(res)
        data = res['data']
        code = res['code']
        if code != '0':
            return Response(status=status.HTTP_204_NO_CONTENT)

        barcode_file = data['itemBarcodeFile']
        code_list = data['itemBarcodeList']

        # 取第一个标签编码为pdf文件名
        pdf_name = code_list[0]

        pdf_data = base64.b64decode(barcode_file)

        from django.conf import settings
        f_name = '%s/label/%s.pdf' % (settings.MEDIA_ROOT, pdf_name)
        file = open(f_name, "wb")
        file.write(pdf_data)
        file.close()

        pdf_path = '%slabel/%s.pdf' % (settings.MEDIA_URL, pdf_name)
        file_path = settings.BASE_URL + pdf_path

        return Response(file_path, status=status.HTTP_200_OK)


class Test(APIView):
    """
    test
    """
    def get(self, request, *args, **kwargs):

        # queryset = Product.objects.filter(product_reg_product__reg_product_reg_country__reg_status='CHECKING')
        # cp = []
        # for i in queryset:
        #     if i.company not in cp:
        #         cp.append(i.company)
        #
        # for c in cp:
            # logis_auth = LogisticsAuth.objects.get(company=c)
            # app_key = logis_auth.app_key  # 万邑联账户
            # token = logis_auth.token  # 万邑通账户token
            #
            # develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
            # client_id = develop_auth.client_id  # 开发账户id
            # client_secret = develop_auth.client_secret  # 开发账户密钥
            # platform = develop_auth.dp_code  # 开发账号代码
            #
            # win_it = WinIt(token, client_secret, client_id, app_key, platform)

            # winit_get_product('N288CR', c)
        from setting.task import winit_get_all_warehouse_delivery_way
        winit_get_all_warehouse_delivery_way()

        return Response(status=status.HTTP_200_OK)