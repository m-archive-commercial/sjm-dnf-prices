"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 22, 2022, 06:27
"""
from scripts.before_crawl.db_clear_price_invalid import coll_price, coll_product
from sjm_dnf_prices.spiders.price import COLL_PRODUCT_FIELD_WITH_PRICE, STATUS_WITH_PRICE

if __name__ == '__main__':

    misMatchedIds = []
    matchedIds = []
    for itemInPrice in coll_price.find({}):
        # print(itemInPrice)
        assert itemInPrice['success'] is True

        id = itemInPrice["_id"]
        itemInProduct = coll_product.find_one({"_id": id})

        if itemInProduct.get(COLL_PRODUCT_FIELD_WITH_PRICE) != STATUS_WITH_PRICE.OK:
            misMatchedIds.append(id)
            coll_product.update_one({"_id": id}, {"$set": {COLL_PRODUCT_FIELD_WITH_PRICE: STATUS_WITH_PRICE.OK}})
        else:
            matchedIds.append(id)

    print({
        "nMismatched": len(misMatchedIds),
        "nMatched": len(matchedIds)
    })