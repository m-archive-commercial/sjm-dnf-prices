"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 22, 2022, 06:24
"""
from sjm_dnf_prices.spiders.price import db, COLL_PRODUCT_FIELD_WITH_PRICE, STATUS_WITH_PRICE
from sjm_dnf_prices.spiders.product import COLL_PRODUCT_NAME

products = list(db[COLL_PRODUCT_NAME].find(
    {
        COLL_PRODUCT_FIELD_WITH_PRICE: {
            "$nin": [STATUS_WITH_PRICE.OK, STATUS_WITH_PRICE.FAILED_FOR_INTERNAL_SERVER_ERROR]},
        # 在使用平均大区的筛选条件下，韩服数据会返回500
        "category.L1_name"           : {"$ne": "韩服独有"}}
))
ids = sorted([int(i['_id']) for i in products])
assert 7903 not in ids
print(ids)