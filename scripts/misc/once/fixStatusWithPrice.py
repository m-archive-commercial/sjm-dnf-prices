"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 16:38
"""
from scripts.before_crawl.db_clear_price_invalid import coll_product
from sjm_dnf_prices.ds import STATUS_WITH_PRICE, FIELD_WITH_PRICE

update500 = coll_product.update_many(
    {FIELD_WITH_PRICE: "500 internal server"},
    {"$set": {FIELD_WITH_PRICE: STATUS_WITH_PRICE.PASSED_FOR_INTERNAL_SERVER_ERROR}}
)

updateUnknown = coll_product.update_many(
    {FIELD_WITH_PRICE: STATUS_WITH_PRICE.PASSED_FOR_KOREAN_ONLY},
    {"$set": {FIELD_WITH_PRICE: STATUS_WITH_PRICE.UNKNOWN}}
)

updateKorean = coll_product.update_many(
    {"category.L1_name": "韩服独有"},
    {"$set": {FIELD_WITH_PRICE: STATUS_WITH_PRICE.PASSED_FOR_KOREAN_ONLY}}
)

print({
    "update500"   : update500.raw_result,
    "updateUnknown": updateUnknown.raw_result,
    "updateKorean": updateKorean.raw_result,
})
