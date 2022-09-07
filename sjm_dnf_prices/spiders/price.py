from typing import TypedDict, List
from urllib.parse import quote

import pymongo
import scrapy
from scrapy import Request
from scrapy.http import TextResponse

from sjm_dnf_prices.ds import STATUS, SPIDER_PRICE_NAME, COLL_PRICE_NAME, FIELD_WITH_PRICE, \
    COLL_PRODUCT_NAME, PASSED_STATUSES_WITH_PRICE, FIELD_WITH_YS, FIELD_WITH_ZS
from sjm_dnf_prices.items import PriceItem
from sjm_dnf_prices.settings import MONGO_DATABASE
from collections import defaultdict

uri = pymongo.MongoClient()
db = uri[MONGO_DATABASE]


class IReqPrice(TypedDict):
    query: str
    collName: str
    fieldMarkFinished: str


reqPrices = [
    {
        "query"            : '&type=&low=djx&avg=pjjx&high=gjx',  # 三种数据：低、平均、高价线
        "collName"         : "price",
        "fieldMarkFinished": FIELD_WITH_PRICE
    },
    {
        "query"            : '&type=ys',
        "collName"         : "ys",
        "fieldMarkFinished": FIELD_WITH_YS
    },
    {
        "query"            : '&type=zs',
        "collName"         : "zs",
        "fieldMarkFinished": FIELD_WITH_ZS
    },
]  # type: List[IReqPrice]


def printProduct(product):
    return f'product(id={product["id"]}, name={product["name"]} category={product["category"]["L1_name"] + "-" + product["category"]["L2_name"]})'


class PriceSpider(scrapy.Spider):
    name = SPIDER_PRICE_NAME
    allowed_domains = ['dnf.yxwujia.com']

    def start_requests(self):
        reqs = []

        reqPriceTypeStat = defaultdict(int)
        for reqPrice in reqPrices:
            products = list(
                db[COLL_PRODUCT_NAME].find({reqPrice["fieldMarkFinished"]: {"$nin": PASSED_STATUSES_WITH_PRICE}}))
            for product in products:
                id = product['id']
                name = product['name']
                # print(product)
                print(f"added price info for {printProduct(product)}")
                # needed using () to wrap multi-line string
                url = ('http://dnf.yxwujia.com/a/query/data'
                       '?server=qqqfpj'
                       f'&wpmc={quote(name)}'
                       '&startDate=2016-01-01'
                       '&endDate=2022-08-20'  # 2016-01-01 ~ 2022-08-20 表示 全部
                       '&unit=yxb'  # 游戏币，另一种是人民币
                       '&period=day' +
                       reqPrice["query"]
                       )
                reqs.append(Request(
                    url=url,
                    meta={
                        "id"               : id,
                        "name"             : name,
                        "category"         : product["category"],
                        "collName"         : reqPrice["collName"],
                        "fieldMarkFinished": reqPrice["fieldMarkFinished"]
                    },
                    dont_filter=True))
                reqPriceTypeStat[reqPrice["collName"]] += 1
        print(f'\n===\nTOTAL: {len(reqs)}, DETAIL: {dict(reqPriceTypeStat)}\n===\n')
        return reqs

    def parse(self, response: TextResponse, **kwargs):
        id = response.meta["id"]
        fieldMarkFinished = response.meta["fieldMarkFinished"]
        # scenario: normal
        if response.status == 200:
            data = response.json()  # type: dict

            if data['success']:
                assert set(data.keys()) == {'success', 'errorCode', 'msg', 'data'}, data
                priceItem = PriceItem(
                    success=data['success'],
                    errorCode=data['errorCode'],
                    msg=data['msg'],
                    data=data['data'],

                    _id=id,

                    name=response.meta['name'],
                    category=response.meta['category'],
                    coll_name=response.meta["collName"],
                )
                yield priceItem
                db[COLL_PRODUCT_NAME].update_one({"_id": id},
                    {"$set": {fieldMarkFinished: STATUS.OK}})
            else:
                """
                response sample:
                    2022-08-22 06:05:13 [scrapy.core.scraper] DEBUG: Scraped from <200 http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc=%E9%AB%98%E5%BC%BA%E5%8C%96%E9%98%BF%E5%B0%94%E9%AB%98%E6%96%AF%20%E5%8D%A1%E7%89%87&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day>
                    {'success': False, 'errorCode': '-1', 'msg': '查询过于频繁,5次操作后，账号将被锁定！！', 'name': '高强化阿尔高斯 卡片', 'category': {'L1_id': 'fecd78becbff4bc6a47836f2c94207ab', 'L1_name': '副职业', 'L2_id': '7476029579a744cdb27f5edf21fece37', 'L2_name': '副职材料'}, '_id': '2744', 'coll_name': 'price'}
                """
                assert set(data.keys()) == {'success', 'errorCode', 'msg'}, data
                db[COLL_PRODUCT_NAME].update_one({"_id": id},
                    {"$set": {fieldMarkFinished: STATUS.FAILED_FOR_TOO_FREQUENT}})

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
                {"$set": {fieldMarkFinished: STATUS.PASSED_FOR_INTERNAL_SERVER_ERROR}})
