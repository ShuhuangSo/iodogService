import requests
import json
import hashlib
import time
import collections


class WinIt(object):
    """
    万邑通物流
    """

    def __init__(self, token, client_secret, client_id, app_key, platform):
        self.TOKEN = token
        self.CLIENT_SECRET = client_secret
        self.CLIENT_ID = client_id
        self.APP_KEY = app_key
        self.PLATFORM = platform

        # 应用签名
        self.client_sign = ''
        # 客户签名
        self.sign = ''

        # 建带排序的字典
        self.req = collections.OrderedDict()
        self.req.update({'action': ''})
        self.req.update({'app_key': app_key})
        self.req.update({'data': ''})
        self.req.update({'format': 'json'})
        self.req.update({'platform': platform})
        self.req.update({'sign_method': 'md5'})
        self.req.update({'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))})
        self.req.update({'version': '1.0'})

    def generate_sign(self, req, token, client_secret):
        """
        生成签名(MD5 32位加密，转大写)
        :param req:
        :param token:
        :param client_secret:
        :return:
        """
        ping = ''
        for k, v in req.items():
            if str(k) == 'data':
                v = json.dumps(v).strip()
            temp = str(k) + str(v)
            ping += temp

        token_ping = token + ping + token
        client_ping = client_secret + ping + client_secret

        sign_md5 = hashlib.md5(token_ping.encode('utf-8')).hexdigest()
        client_md5 = hashlib.md5(client_ping.encode('utf-8')).hexdigest()

        self.sign = sign_md5.upper()
        self.client_sign = client_md5.upper()

    def get_product(self, sku=''):
        """
        查询商品
        :param sku: 产品sku编码（支持模糊搜索）
        :return:
        """
        url = 'http://openapi.winit.com.cn/openapi/service'
        self.req.update({'action': 'winit.mms.item.list'})
        self.req.update({'data': {
                'pageNo': '1',
                'pageSize': '5',
                'skuCode': sku
        }})

        # 生成签名
        self.generate_sign(self.req, self.TOKEN, self.CLIENT_SECRET)

        # 添加请求报文信息
        self.req.update({'client_id': self.CLIENT_ID})
        self.req.update({'client_sign': self.client_sign})
        self.req.update({'sign': self.sign})

        # 发起请求
        response = requests.post(url, data=json.dumps(self.req))
        return response.text

    def reg_product(self, product_list):
        """
        注册产品
        :param product_list: 产品列表
        :return:
        """
        url = 'http://api.winit.com.cn/ADInterface/api'
        self.req.update({'action': 'registerProduct'})
        self.req.update({'data': {
            'productList': product_list
        }})

        # 生成签名
        self.generate_sign(self.req, self.TOKEN, self.CLIENT_SECRET)

        # 添加请求报文信息
        self.req.update({'client_id': self.CLIENT_ID})
        self.req.update({'client_sign': self.client_sign})
        self.req.update({'sign': self.sign})

        # 发起请求
        response = requests.post(url, data=json.dumps(self.req))
        return response.text

    def print_product_label(self, single_items, label_type='LZ6040', made_in='China'):
        """
        打印产品标签
        :param single_items: 产品列表
        :param label_type: 条码尺寸类型 LZ10060：100x60mm仅有单品条码； LZ7050：70x50mm，仅有单品条码； LZ6040:60x40mm，仅有单品条码
        :param made_in: None:不显示信息在条码 China: 产地显示中国
        :return:
        """
        url = 'http://openapi.winit.com.cn/openapi/service'
        self.req.update({'action': 'winit.singleitem.label.print.v2'})
        self.req.update({'data': {
            'singleItems': single_items,
            'labelType': label_type,
            'madeIn': made_in
        }})

        # 生成签名
        self.generate_sign(self.req, self.TOKEN, self.CLIENT_SECRET)

        # 添加请求报文信息
        self.req.update({'client_id': self.CLIENT_ID})
        self.req.update({'client_sign': self.client_sign})
        self.req.update({'sign': self.sign})

        # 发起请求
        response = requests.post(url, data=json.dumps(self.req))
        return response.text

    def get_warehouse(self):
        """
        查询仓库列表
        :return:
        """
        url = 'http://api.winit.com.cn/ADInterface/api'
        self.req.update({'action': 'queryWarehouse'})
        self.req.update({'data': {

        }})

        # 生成签名
        self.generate_sign(self.req, self.TOKEN, self.CLIENT_SECRET)

        # 添加请求报文信息
        self.req.update({'client_id': self.CLIENT_ID})
        self.req.update({'client_sign': self.client_sign})
        self.req.update({'sign': self.sign})

        # 发起请求
        response = requests.post(url, data=json.dumps(self.req))
        return response.text

    def get_delivery_way(self, warehouse_id):
        """
        查询物流公司尾程渠道
        :return:
        """
        url = 'http://api.winit.com.cn/ADInterface/api'
        self.req.update({'action': 'queryDeliveryWay'})
        self.req.update({'data': {
            "warehouseID": warehouse_id
        }})

        # 生成签名
        self.generate_sign(self.req, self.TOKEN, self.CLIENT_SECRET)

        # 添加请求报文信息
        self.req.update({'client_id': self.CLIENT_ID})
        self.req.update({'client_sign': self.client_sign})
        self.req.update({'sign': self.sign})

        # 发起请求
        response = requests.post(url, data=json.dumps(self.req))
        return response.text