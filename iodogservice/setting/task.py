from celery import task
from api.winit import WinIt
from setting.models import LogisticsAuth, DevelopAuth, ThirdWarehouse, ThirdDelivery
import json


@task
def winit_get_warehouse():
    """
    获取仓库列表
    :return:
    """

    logis_auth = LogisticsAuth.objects.get(app_key='46526075@qq.com')
    app_key = logis_auth.app_key  # 万邑联账户
    token = logis_auth.token  # 万邑通账户token

    develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
    client_id = develop_auth.client_id  # 开发账户id
    client_secret = develop_auth.client_secret  # 开发账户密钥
    platform = develop_auth.dp_code  # 开发账号代码

    win_it = WinIt(token, client_secret, client_id, app_key, platform)
    res = win_it.get_warehouse()

    res = json.loads(res)
    if res['code'] == 0:
        wh_list = res['data']
        add_list = []
        for i in wh_list:
            wh_code = i['warehouseCode']
            wh_id = i['warehouseID']
            wh_name = i['warehouseName']
            wh_address = i['warehouseAddress']
            logistics_company = 'winit'

            queryset = ThirdWarehouse.objects.filter(wh_id=wh_id).count()
            # 如果仓库已存在,检查更新仓库名称和地址两个字段
            if queryset:
                warehouse = ThirdWarehouse.objects.get(wh_id=wh_id)
                if warehouse.wh_name != wh_name:
                    ThirdWarehouse.objects.filter(wh_id=wh_id).update(wh_name=wh_name)
                if warehouse.wh_address != wh_address:
                    ThirdWarehouse.objects.filter(wh_id=wh_id).update(wh_address=wh_address)
                continue

            add_list.append(ThirdWarehouse(
                wh_code=wh_code,
                wh_id=wh_id,
                wh_name=wh_name,
                wh_address=wh_address,
                logistics_company=logistics_company
            ))
        if len(add_list):
            ThirdWarehouse.objects.bulk_create(add_list)


@task
def winit_get_delivery_way(warehouse_id):
    """
    物流公司尾程渠道
    :return:
    """

    logis_auth = LogisticsAuth.objects.get(app_key='46526075@qq.com')
    app_key = logis_auth.app_key  # 万邑联账户
    token = logis_auth.token  # 万邑通账户token

    develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
    client_id = develop_auth.client_id  # 开发账户id
    client_secret = develop_auth.client_secret  # 开发账户密钥
    platform = develop_auth.dp_code  # 开发账号代码

    win_it = WinIt(token, client_secret, client_id, app_key, platform)
    res = win_it.get_delivery_way(warehouse_id)

    res = json.loads(res)
    if res['code'] == '0':
        dy_list = res['data']
        add_list = []
        for i in dy_list:
            product_code = i['winitProductCode']
            delivery_way = i['deliveryWay']
            delivery_id = i['deliveryID']
            is_door_number = True if i['isMandoorplateNumbers'] == 'Y' else False
            wh_id = i['warehouseID']

            # 如果渠道已存在,检查更新渠道两个字段
            queryset = ThirdDelivery.objects.filter(delivery_id=delivery_id).count()
            if queryset:
                delivery = ThirdDelivery.objects.get(delivery_id=delivery_id)
                if delivery.delivery_way != delivery_way:
                    ThirdDelivery.objects.filter(delivery_id=delivery_id).update(delivery_way=delivery_way)
                if delivery.is_door_number != is_door_number:
                    ThirdDelivery.objects.filter(delivery_id=delivery_id).update(is_door_number=is_door_number)
                continue

            add_list.append(ThirdDelivery(
                product_code=product_code,
                delivery_way=delivery_way,
                delivery_id=delivery_id,
                is_door_number=is_door_number,
                wh_id=wh_id
            ))
        if len(add_list):
            ThirdDelivery.objects.bulk_create(add_list)