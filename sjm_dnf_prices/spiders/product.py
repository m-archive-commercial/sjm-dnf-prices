import json
import re
from typing import List, TypedDict

import scrapy
from scrapy import Request
from scrapy.http import TextResponse
from scrapy.shell import inspect_response

from scripts.misc.treeDataLayered2db import queryTreeDataWithLayers
from sjm_dnf_prices.pipelines import FIELD_COLL_NAME
from sjm_dnf_prices.settings import DATA_SOURCE_DIR

SPIDER_PRODUCT_NAME = "product"
COLL_PRODUCT_NAME = SPIDER_PRODUCT_NAME


def parseJsonResponse(response):
    """
    parse and follow response based on json, ref: https://stackoverflow.com/a/63147576/9422455
    :param response:
    :return:
    """
    for row in response.json()['rows']:
        row[FIELD_COLL_NAME] = COLL_PRODUCT_NAME
        row["_id"] = row['id']
        row["category"] = response.meta["category"]
        yield row


class ProductItem(TypedDict):
    parent: str
    id: str
    text: str


class GoodsSpider(scrapy.Spider):
    name = SPIDER_PRODUCT_NAME
    allowed_domains = ['dnf.yxwujia.com']

    def start_requests(self):
        pageSize = 100
        pageNo = 1
        reqs = []
        for categoryItem in queryTreeDataWithLayers():
            url = (
                'http://dnf.yxwujia.com/a/api/product/getByName'
                '?name='
                '&quality='
                f'&ctype.id={categoryItem["L2_id"]}'
                f'&pageNo={pageNo}'
                '&orderBy='
                '&_=1660984982504'
                f'&pageSize={pageSize}'
            )
            reqs.append(Request(
                url=url,
                meta={
                    "category": categoryItem
                },
                dont_filter=True
            ))
        return reqs

    def parse(self, response: TextResponse, **kwargs):
        """
        response 分析：
            目标 51 个；设置no=2, size=100；结果total=51, rows=51个（与no=1一样）
            目标 51 个；设置no=2, size=50 ；结果total=51, rows=1个
            目标 51 个；设置no=3, size=50 ；结果total=51, rows=50个（与no=1一样）
        函数设计：
            其实可以少发一次请求，但为了程序可读性，决定还是直接多发一次请求
        :param response:
        :return:
        """
        # inspect_response(response, self)
        data = response.json()
        pageSize = int(re.search(r'pageSize=(\d+)', response.url).groups()[0])
        expectedTotalPages = (data['total'] - 1) // pageSize + 1
        for pageNo in range(1, expectedTotalPages + 1):
            newUrl = re.sub(r'(?<=pageNo=)\d+', lambda m: str(pageNo), response.url)
            yield Request(url=newUrl, callback=parseJsonResponse, meta=response.meta)
