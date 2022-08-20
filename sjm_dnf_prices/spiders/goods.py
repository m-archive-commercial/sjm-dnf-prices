import scrapy


class GoodsSpider(scrapy.Spider):
    name = 'goods'
    allowed_domains = ['dnf.yxwujia.com']
    start_urls = ['http://dnf.yxwujia.com/']

    def parse(self, response):
        pass
