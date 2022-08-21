from enum import Enum
from urllib.parse import quote

import pymongo
import scrapy
from scrapy import Request
from scrapy.http import TextResponse

from sjm_dnf_prices.pipelines import FIELD_COLL_NAME
from sjm_dnf_prices.settings import MONGO_DATABASE
from sjm_dnf_prices.spiders.product import COLL_PRODUCT_NAME

uri = pymongo.MongoClient()
db = uri[MONGO_DATABASE]

SPIDER_PRICE_NAME = "price"
COLL_PRICE_NAME = SPIDER_PRICE_NAME

COLL_PRODUCT_FIELD_WITH_PRICE = "withPrice"


class STATUS_WITH_PRICE(str, Enum):
    OK = "OK"
    FAILED_FOR_TOO_FREQUENT = "too frequent"
    FAILED_FOR_INTERNAL_SERVER_ERROR = "500 internal server"


class PriceSpider(scrapy.Spider):
    name = SPIDER_PRICE_NAME
    allowed_domains = ['dnf.yxwujia.com']

    def start_requests(self):
        reqs = []
        products = list(db[COLL_PRODUCT_NAME].find(
            {
                COLL_PRODUCT_FIELD_WITH_PRICE: {
                    "$nin": [STATUS_WITH_PRICE.OK, STATUS_WITH_PRICE.FAILED_FOR_INTERNAL_SERVER_ERROR]},
                # 在使用平均大区的筛选条件下，韩服数据会返回500
                "category.L1_name"           : {"$ne": "韩服独有"}}
        ))
        assert 7903 not in [i['_id'] for i in products]
        for product in products:
            id = product['id']
            name = product['name']
            # print(product)
            print(f"adding price info for product("
                  f"id={id}, "
                  f"name={name}, "
                  f"category={product['category']['L1_name'] + '-' + product['category']['L2_name']})"
                  f"")
            # needed using () to wrap multi-line string
            url = ('http://dnf.yxwujia.com/a/query/data'
                   '?server=qqqfpj'
                   f'&wpmc={quote(name)}'
                   '&type='
                   '&startDate=2016-01-01&endDate=2022-08-20'  # 2016-01-01 ~ 2022-08-20 表示 全部
                   '&unit=yxb'  # 游戏币，另一种是人民币
                   '&low=djx&avg=pjjx&high=gjx'  # 三种数据：低、平均、高价线
                   '&period=day')
            reqs.append(Request(
                url=url,
                meta={"id": id, "name": name, "category": product["category"]},
                dont_filter=True))
        return reqs

    def parse(self, response: TextResponse, **kwargs):
        id = response.meta["id"]
        # scenario: normal
        if response.status == 200:
            data = response.json()
            data["name"] = response.meta['name']
            data["category"] = response.meta["category"]
            data["_id"] = id
            data[FIELD_COLL_NAME] = COLL_PRICE_NAME
            if data['success'] == True:
                yield data
                db[COLL_PRODUCT_NAME].update_one({"_id": id},
                    {"$set": {COLL_PRODUCT_FIELD_WITH_PRICE: STATUS_WITH_PRICE.OK}})
            else:
                """
                response sample:
                    2022-08-22 06:05:13 [scrapy.core.scraper] DEBUG: Scraped from <200 http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E9%AB%98%E5%BC%BA%E5%8C%96%E9%98%BF%E5%B0%94%E9%AB%98%E6%96%AF%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day>
                    {'success': False, 'errorCode': '-1', 'msg': '查询过于频繁,5次操作后，账号将被锁定！！', 'name': '高强化阿尔高斯 卡片', 'category': {'L1_id': 'fecd78becbff4bc6a47836f2c94207ab', 'L1_name': '副职业', 'L2_id': '7476029579a744cdb27f5edf21fece37', 'L2_name': '副职材料'}, '_id': '2744', 'coll_name': 'price'}
                """
                db[COLL_PRODUCT_NAME].update_one({"_id": id},
                    {"$set": {COLL_PRODUCT_FIELD_WITH_PRICE: STATUS_WITH_PRICE.FAILED_FOR_TOO_FREQUENT}})

        if response.status == 500:
            """
            # scenario: server error
            response sample:
                2022-08-22 06:03:27 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E6%9D%B0%E6%A3%AE&middot;%E6%A0%BC%E9%87%8C%E5%85%8B%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day> (failed 1 times): 500 Internal Server Error
                2022-08-22 06:03:36 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E6%9D%B0%E6%A3%AE&middot;%E6%A0%BC%E9%87%8C%E5%85%8B%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day> (failed 2 times): 500 Internal Server Error
                2022-08-22 06:03:44 [scrapy.downloadermiddlewares.retry] ERROR: Gave up retrying <GET http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E6%9D%B0%E6%A3%AE&middot;%E6%A0%BC%E9%87%8C%E5%85%8B%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day> (failed 3 times): 500 Internal Server Error
                2022-08-22 06:03:44 [scrapy.core.engine] DEBUG: Crawled (500) <GET http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E6%9D%B0%E6%A3%AE&middot;%E6%A0%BC%E9%87%8C%E5%85%8B%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day> (referer: None)
                2022-08-22 06:03:44 [scrapy.spidermiddlewares.httperror] INFO: Ignoring response <500 http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E6%9D%B0%E6%A3%AE&middot;%E6%A0%BC%E9%87%8C%E5%85%8B%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day>: HTTP status code is not handled or not allowed
            """
            db[COLL_PRODUCT_NAME].update_one({"_id": id},
                {"$set": {COLL_PRODUCT_FIELD_WITH_PRICE: STATUS_WITH_PRICE.FAILED_FOR_INTERNAL_SERVER_ERROR}})
