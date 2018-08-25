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
    logis_auth = LogisticsAuth.objects.get(company=company)
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
    print(sku + '88==' + res)

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
        logis_auth = LogisticsAuth.objects.get(company=c)
        app_key = logis_auth.app_key  # 万邑联账户
        token = logis_auth.token  # 万邑通账户token

        develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
        client_id = develop_auth.client_id  # 开发账户id
        client_secret = develop_auth.client_secret  # 开发账户密钥
        platform = develop_auth.dp_code  # 开发账号代码
        for q in queryset:
            winit_get_product.delay(q.sku, token, client_secret, client_id, app_key, platform, c)