from celery import task
from api.winit import WinIt
from .models import Product, RegProduct, RegCountry
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
    token = '94341349A48B822AE921257FBE74A8B4'  # 万邑通账户token
    client_secret = 'NJG5NJFIOGMTN2MWYS00MTI2LTGYZWUTNTY1NZNHZDK1ZJCYMJE4MTIWMTI0NZUXOTC1NZK='  # 开发账户密钥
    client_id = 'ODG1ZDHJZWITNWY1ZC00YJI1LTGYODCTY2M3OWVKNJZMYWNL'  # 开发账户id
    app_key = '46526075@qq.com'  # 万邑联账户
    platform = 'IODOG'  # 开发账号代码

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