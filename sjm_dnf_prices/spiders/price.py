from urllib.parse import quote

import pymongo
import scrapy
from scrapy import Request

from sjm_dnf_prices.pipelines import FIELD_COLL_NAME
from sjm_dnf_prices.settings import MONGO_DATABASE
from sjm_dnf_prices.spiders.product import COLL_PRODUCT_NAME

uri = pymongo.MongoClient()
db = uri[MONGO_DATABASE]

SPIDER_PRICE_NAME = "price"
COLL_PRICE_NAME = SPIDER_PRICE_NAME


class PriceSpider(scrapy.Spider):
    name = SPIDER_PRICE_NAME
    allowed_domains = ['dnf.yxwujia.com']

    def start_requests(self):
        reqs = []
        for product in list(db[COLL_PRODUCT_NAME].find({"isWithPrice": {"$ne": True}})):
            id = product['id']
            name = product['name']
            print(f"adding price info for product(id={id}, name={name})")
            # needed using () to wrap multi-line string
            url = ('http://dnf.yxwujia.com/a/query/data'
                   '?server=qqqfpj'
                   f'&wpmc={name}'
                   '&type='
                   '&startDate=2016-01-01&endDate=2022-08-20'  # 2016-01-01 ~ 2022-08-20 表示 全部
                   '&unit=yxb'  # 游戏币，另一种是人民币
                   '&low=djx&avg=pjjx&high=gjx'  # 三种数据：低、平均、高价线
                   '&period=day')
            reqs.append(Request(url=url, meta={"id": id, "name": name}, dont_filter=True))
        return reqs

    def parse(self, response, **kwargs):
        data = response.json()
        data["name"] = response.meta['name']
        id = response.meta["id"]
        data["_id"] = id
        data[FIELD_COLL_NAME] = COLL_PRICE_NAME
        yield data
        if data['success'] == True:
            db[COLL_PRODUCT_NAME].update_one({"_id": id}, {"$set": {"status.withPrice": True}})
