"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 06, 2022, 23:19
"""
from scripts.before_crawl.db_clear_price_invalid import coll_product
from sjm_dnf_prices.ds import FIELD_WITH_PRICE, PASSED_STATUSES_WITH_PRICE, FIELD_WITH_YS, FIELD_WITH_ZS

for item in coll_product.find({FIELD_WITH_PRICE: {"$nin": PASSED_STATUSES_WITH_PRICE}}):
    status = item[FIELD_WITH_PRICE]
    res = coll_product.update_one({"_id": item["_id"]}, {"$set": {FIELD_WITH_YS: status, FIELD_WITH_ZS: status}})
    print(res.raw_result)
