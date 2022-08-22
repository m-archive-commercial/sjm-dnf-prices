import pymongo
from itemadapter import ItemAdapter

from sjm_dnf_prices.items import PriceItem

FIELD_COLL_NAME = "coll_name"


class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item: PriceItem, spider):
        """
        todo: compat with product
        :param item:
        :param spider:
        :return:
        """
        self.db[item.coll_name].insert_one(ItemAdapter(item).asdict())
        return item
