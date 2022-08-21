"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 23:17
"""
import pymongo

from sjm_dnf_prices.settings import MONGO_DATABASE
from sjm_dnf_prices.spiders.price import COLL_PRICE_NAME
from sjm_dnf_prices.spiders.product import COLL_PRODUCT_NAME

uri = pymongo.MongoClient()
db = uri[MONGO_DATABASE]
coll_price = db[COLL_PRICE_NAME]
coll_product = db[COLL_PRODUCT_NAME]

for item in coll_price.find({}):
    if not item['success']:
        print(f'deleting item(_id={item["_id"]}) from coll(name={COLL_PRICE_NAME})')
        coll_price.delete_one({"_id": item["_id"]})
        print(f'updating item(_id={item["_id"]}) from coll(name={COLL_PRODUCT_NAME})')
        coll_product.update_one({"_id": item["_id"]}, {"$set": {"status": {"withPrice": False}}})

coll_product.update_many({"status.withPrice": True}, {"$set": {"isWithPrice": True}})
