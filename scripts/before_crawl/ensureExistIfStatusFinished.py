"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 16:36
"""
from scripts.before_crawl.db_clear_price_invalid import db
from sjm_dnf_prices.ds import STATUS

for fieldSuffix in ['Price', "YS", "ZS"]:
    field = 'with' + fieldSuffix
    collName = fieldSuffix.lower()
    for item in db['product'].find({field: STATUS.OK}):
        id = item['_id']
        itemInfo = {"id": id, "collName": collName, "statusInProduct": "OK", "statusInTargetColl": "NOT-EXIST"}
        if db[collName].find_one({"_id": id}) is None:
            print(itemInfo)
            res = db['product'].update_one({"_id": id}, {"$set": {field: STATUS.UNKNOWN}})
            print(res.raw_result)
