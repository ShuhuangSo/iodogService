from celery import task
from api.winit import WinIt
from .models import Warehouse, WarehouseStock
from product.models import Product
from setting.models import LogisticsAuth, DevelopAuth

import json


@task
def winit_get_warehouse_stock(token, client_secret, client_id, app_key, platform, warehouse_id, warehouse_code, company):
    """
    同步海外仓库存到本地
    :return:
    """
    download_status = True
    p_num = 1
    while download_status:
        win_it = WinIt(token, client_secret, client_id, app_key, platform)
        res = win_it.get_warehouse_stock(warehouse_id, warehouse_code, p_num)
        p_num += 1

        # 将库存同步到本地
        res = json.loads(res)
        if res['code'] == 0:
            data = res['data']
            page = data['page']
            total_records = page['TotalRows']  # 总记录数
            page_size = page['NumRows']  # 每页数量
            page_num = page['StartRow']  # 页码
            # 如果仓库没有数据，则停止下载
            if total_records == 0:
                download_status = False
                continue

            # 如果记录下载完，则停止下载
            if page_size * page_num >= total_records:
                download_status = False

            p_list = data['list']
            add_list = []
            if p_list:
                for i in p_list:
                    sku = i['productCode']
                    cn_name = i['name']  # 产品名称
                    available_qty = i['qtyAvailable']
                    reserved_qty = i['qtyReserved']
                    on_way_qty = i['qtyOrdered']
                    his_in_qty = i['qtyHisIn']
                    his_sell_qty = i['qtySellHisOut']
                    is_return = i['isReturnInventory']
                    is_prohibit = i['isprohibitoutbound']

                    # 退货sku没有以下字段
                    avg_sell_qty15 = i['averageSalesQty15'] if is_return == 'N' else 0.0
                    avg_stock15 = i['averageStockQty15'] if is_return == 'N' else 0.0
                    avg_sell_qty7 = i['averageSalesQty7'] if is_return == 'N' else 0.0
                    avg_stock7 = i['averageStockQty7'] if is_return == 'N' else 0.0

                    # 将字符串转浮点
                    doi = float(i['DOI']) if i['DOI'] != '' else 0.0
                    avg_sell_qty = float(i['averageSalesQty']) if i['averageSalesQty'] != '' else 0.0
                    avg_stock = float(i['averageStockQty']) if i['averageStockQty'] != '' else 0.0
                    if avg_sell_qty15:
                        avg_sell_qty15 = float(avg_sell_qty15)
                    if avg_stock15:
                        avg_stock15 = float(avg_stock15)
                    if avg_sell_qty7:
                        avg_sell_qty7 = float(avg_sell_qty7)
                    if avg_stock7:
                        avg_stock7 = float(avg_stock7)

                    # 检查该产品在本地对应仓库是否存在，存在则进行更新数据，不存在则创建
                    warehouse = Warehouse.objects.get(wh_id=warehouse_id)
                    queryset = WarehouseStock.objects.filter(warehouse=warehouse, sku=sku).count()
                    if queryset:
                        WarehouseStock.objects.filter(warehouse=warehouse, sku=sku).update(
                            available_qty=available_qty,
                            reserved_qty=reserved_qty,
                            on_way_qty=on_way_qty,
                            his_in_qty=his_in_qty,
                            his_sell_qty=his_sell_qty,
                            avg_sell_qty=avg_sell_qty,
                            avg_stock=avg_stock,
                            avg_sell_qty15=avg_sell_qty15,
                            avg_stock15=avg_stock15,
                            avg_sell_qty7=avg_sell_qty7,
                            avg_stock7=avg_stock7,
                            doi=doi,
                            is_return=True if is_return == 'Y' else False,
                            is_prohibit=True if is_prohibit == 'Y' else False,
                        )
                    else:
                        product_set = Product.objects.filter(company=company, sku=sku).count()
                        # 如果产品库中有该产品，获取产品名称
                        if product_set:
                            product = Product.objects.filter(company=company).get(sku=sku)
                            cn_name = product.cn_name

                        add_list.append(WarehouseStock(
                            sku=sku,
                            cn_name=cn_name,
                            available_qty=available_qty,
                            reserved_qty=reserved_qty,
                            on_way_qty=on_way_qty,
                            his_in_qty=his_in_qty,
                            his_sell_qty=his_sell_qty,
                            avg_sell_qty=avg_sell_qty,
                            avg_stock=avg_stock,
                            avg_sell_qty15=avg_sell_qty15,
                            avg_stock15=avg_stock15,
                            avg_sell_qty7=avg_sell_qty7,
                            avg_stock7=avg_stock7,
                            doi=doi,
                            is_return=True if is_return == 'Y' else False,
                            is_prohibit=True if is_prohibit == 'Y' else False,
                            warehouse=warehouse
                        ))
            # 新增列表有数据，则进行新增
            if add_list:
                WarehouseStock.objects.bulk_create(add_list)

@task
def winit_sync_warehouse_stock_service():
    """
    同步海外仓库存服务
    :return:
    """
    # 找出所有有万邑通仓库，且已激活的公司
    queryset = Warehouse.objects.filter(logistics_company='winit', is_active=True)
    cp = []
    for i in queryset:
        if i.company not in cp:
            cp.append(i.company)

    # 按公司列队同步仓库库存
    for c in cp:
        # 初始话api请求设置
        logis_auth = LogisticsAuth.objects.filter(company=c).get(logistics_code='winit')
        app_key = logis_auth.app_key  # 万邑联账户
        token = logis_auth.token  # 万邑通账户token

        develop_auth = DevelopAuth.objects.get(api_code=logis_auth.logistics_code)
        client_id = develop_auth.client_id  # 开发账户id
        client_secret = develop_auth.client_secret  # 开发账户密钥
        platform = develop_auth.dp_code  # 开发账号代码

        # 查出该公司需要同步的仓库列表
        warehouses = Warehouse.objects.filter(logistics_company='winit', is_active=True, company=c)
        for i in warehouses:
            winit_get_warehouse_stock.delay(token, client_secret, client_id, app_key, platform, i.wh_id, i.wh_code, c)