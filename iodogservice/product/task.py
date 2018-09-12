from celery import task
from api.winit import WinIt
from .models import Product, RegProduct, RegCountry
from setting.models import LogisticsAuth, DevelopAuth
import json


@task
def winit_reg_product(products, company, country_code):
    """
    产品注册
    :param products: 产品列表
    :param company: 所属公司帐号
    :param country_code: 注册国家
    :return:
    """
    logis_auth = LogisticsAuth.objects.filter(company=company).get(logistics_code='winit')
    app_key = logis_auth.app_key  # 万邑联账户
    token = logis_auth.token  # 万邑通账户token

    develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
    client_id = develop_auth.client_id  # 开发账户id
    client_secret = develop_auth.client_secret  # 开发账户密钥
    platform = develop_auth.dp_code  # 开发账号代码

    win_it = WinIt(token, client_secret, client_id, app_key, platform)
    res = win_it.reg_product(products)

    # 注册成功后将注册状态修改为CHECKING
    res = json.loads(res)
    if res['code'] == 0:
        sku_list = res['data']
        for i in sku_list:
            sku = i['productCode']
            product = Product.objects.filter(company=company).get(sku=sku)
            reg_product = RegProduct.objects.get(product=product)
            RegCountry.objects.filter(reg_product=reg_product).filter(country_code=country_code).update(reg_status='CHECKING')


@task
def winit_get_product(sku, token, client_secret, client_id, app_key, platform, company):
    """
    查询winit产品，并同步状态到本地数据库
    :param sku:
    :param token:
    :param client_secret:
    :param client_id:
    :param app_key:
    :param platform:
    :return:
    """

    win_it = WinIt(token, client_secret, client_id, app_key, platform)
    res = win_it.get_product(sku)

    # 如果查询到产品，将注册状态修改为ON_SALE
    res = json.loads(res)
    if res['code'] == '0':
        data = res['data']
        p_list = data['list']
        if p_list:
            p = p_list[0]
            country_list = p['customsDeclarationList']
            if country_list:
                for i in country_list:
                    product = Product.objects.filter(company=company).get(sku=sku)
                    reg_product = RegProduct.objects.get(product=product)
                    queryset = RegCountry.objects.filter(reg_product=reg_product).filter(country_code=i['countryCode']).count()
                    if queryset:
                        RegCountry.objects.filter(reg_product=reg_product).filter(country_code=i['countryCode']).update(reg_status='ON_SALE', import_rate=i['importRate'])


@task
def winit_get_pconfirm(sku, token, client_secret, client_id, app_key, platform, company):
    """
    查询winit产品，检查并同步已确认长度，重量等数据到本地数据库
    :param sku:
    :param token:
    :param client_secret:
    :param client_id:
    :param app_key:
    :param platform:
    :param company:
    :return:
    """

    win_it = WinIt(token, client_secret, client_id, app_key, platform)
    res = win_it.get_product(sku)

    # 如果查询到产品，将确认数据同步到本地
    res = json.loads(res)
    if res['code'] == '0':
        data = res['data']
        p_list = data['list']
        if p_list:
            p = p_list[0]
            confirm_length = p['length']
            confirm_width = p['width']
            confirm_height = p['height']
            confirm_volume = p['volume']
            confirm_weight = p['weight']
            if confirm_length:

                product = Product.objects.filter(company=company).get(sku=sku)
                RegProduct.objects.filter(product=product, logistics_company='万邑通').update(
                    reg_length=confirm_length,
                    reg_width=confirm_width,
                    reg_heigth=confirm_height,
                    reg_weight=confirm_weight,
                    reg_volume=confirm_volume
                )


@task
def winit_syn_pstatus_service():
    """
    同步winit产品状态服务
    :return:
    """
    # 查询所有‘待审核’产品
    queryset = Product.objects.filter(product_reg_product__reg_product_reg_country__reg_status='CHECKING')
    # 找出所有‘待审核’产品所在公司
    cp = []
    for i in queryset:
        if i.company not in cp:
            cp.append(i.company)

    # 将产品列队查询
    for c in cp:
        logis_auth = LogisticsAuth.objects.filter(company=c).get(logistics_code='winit')
        app_key = logis_auth.app_key  # 万邑联账户
        token = logis_auth.token  # 万邑通账户token

        develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
        client_id = develop_auth.client_id  # 开发账户id
        client_secret = develop_auth.client_secret  # 开发账户密钥
        platform = develop_auth.dp_code  # 开发账号代码
        for q in queryset:
            winit_get_product.delay(q.sku, token, client_secret, client_id, app_key, platform, c)


@task
def winit_syn_pconfirm_service():
    """
    同步winit产品核实长度，重量数据
    :return:
    """
    # 查询所有‘已发布’并且确认数据为空的产品
    queryset = Product.objects.filter(product_reg_product__reg_product_reg_country__reg_status='ON_SALE').filter(product_reg_product__reg_length=None)
    # 找出产品所在公司
    cp = []
    for i in queryset:
        if i.company not in cp:
            cp.append(i.company)

    # 将产品列队查询
    for c in cp:
        logis_auth = LogisticsAuth.objects.filter(company=c).get(logistics_code='winit')
        app_key = logis_auth.app_key  # 万邑联账户
        token = logis_auth.token  # 万邑通账户token

        develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
        client_id = develop_auth.client_id  # 开发账户id
        client_secret = develop_auth.client_secret  # 开发账户密钥
        platform = develop_auth.dp_code  # 开发账号代码
        for q in queryset:
            winit_get_pconfirm.delay(q.sku, token, client_secret, client_id, app_key, platform, c)