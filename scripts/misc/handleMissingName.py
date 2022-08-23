"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 22, 2022, 12:23
"""
from scripts.before_crawl.db_clear_price_invalid import coll_price
from sjm_dnf_prices.items import PriceItem


def itemStr(item: dict):
    return f'item(id={item["_id"]})'


def checkMissingName(item):
    if not item.get("name"):
        print('>>>  missing name!')
        return False
    return True


def addMissingName(item):
    print('adding missing name')
    name = item['data']['title']['text'][:-5]
    res = coll_price.update_one({"_id": item["_id"]}, {"$set": {"name": name}})
    print(res.raw_result)


for item in coll_price.find({}):
    print(itemStr(item))

    if not checkMissingName(item):
        addMissingName(item)
