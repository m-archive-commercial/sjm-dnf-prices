import re
from urllib.parse import urlencode, parse_qs

import scrapy
from scrapy import Request
from scrapy.http import TextResponse
from scrapy.shell import inspect_response


def parseJsonResponse(response):
    """
    parse and follow response based on json, ref: https://stackoverflow.com/a/63147576/9422455
    :param response:
    :return:
    """
    for row in response.json()['rows']:
        row["coll"] = "goods"
        yield row


class GoodsSpider(scrapy.Spider):
    name = 'goods'
    allowed_domains = ['dnf.yxwujia.com']

    ctypeIds = [
        'b98c6889625840a48e2204021051e0fb'  # 特殊装备 - 辅助装备通用 - 全部品质
        'c4d4872bd34c4278ab19358e2d70123f'  # 特殊装备 - 魔法石通用 - 全部品质
    ]

    pageSize = 100
    pageNo = 1
    ctypeId = ctypeIds[0]
    start_urls = [
        'http://dnf.yxwujia.com/a/api/product/getByName'
        '?name='
        '&quality='
        f'&ctype.id={ctypeId}'
        f'&pageNo={pageNo}'
        '&orderBy='
        '&_=1660984982504'
        f'&pageSize={pageSize}'
    ]

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
            yield Request(url=newUrl, callback=parseJsonResponse)
