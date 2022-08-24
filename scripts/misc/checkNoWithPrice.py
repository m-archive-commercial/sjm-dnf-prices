"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 16:32
"""
from scripts.before_crawl.db_clear_price_invalid import coll_product
from sjm_dnf_prices.ds import STATUS_WITH_PRICE, FIELD_WITH_PRICE


nNotExistsBefore = coll_product.count_documents({FIELD_WITH_PRICE: {"$exists": False}})

updatedResult = coll_product.update_many(
    {FIELD_WITH_PRICE: {"$exists": False}},
    {"$set": {FIELD_WITH_PRICE: STATUS_WITH_PRICE.UNKNOWN}},
    upsert=False
)

nNotExistsAfter = coll_product.count_documents({FIELD_WITH_PRICE: {"$exists": False}})

print({
    "nNotExistsBefore": nNotExistsBefore,
    "nNotExistsAfter" : nNotExistsAfter,
    "updatedResult"   : updatedResult.raw_result
})
