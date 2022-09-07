"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 23:17
"""
import pymongo

from sjm_dnf_prices.settings import MONGO_DATABASE
from sjm_dnf_prices.ds import STATUS, COLL_PRICE_NAME, FIELD_WITH_PRICE, COLL_PRODUCT_NAME

uri = pymongo.MongoClient()
db = uri[MONGO_DATABASE]
coll_price = db[COLL_PRICE_NAME]
coll_product = db[COLL_PRODUCT_NAME]

# for itemInPrice in coll_price.find({}):
#     if not itemInPrice['success']:
#         print(f'deleting itemInPrice(_id={itemInPrice["_id"]}) from coll(name={COLL_PRICE_NAME})')
#         coll_price.delete_one({"_id": itemInPrice["_id"]})
#         print(f'updating itemInPrice(_id={itemInPrice["_id"]}) from coll(name={COLL_PRODUCT_NAME})')
#         coll_product.update_one({"_id": itemInPrice["_id"]}, {"$set": {"status": {"withPrice": False}}})

# res = coll_product.update_many({"status.withPrice": True}, {"$set": {FIELD_WITH_PRICE: STATUS_WITH_PRICE.OK}})
# print(res.raw_result)

if __name__ == '__main__':
    res = coll_product.update_many({}, {"$unset": {"WithPrice": ""}})
    print(res.raw_result)
