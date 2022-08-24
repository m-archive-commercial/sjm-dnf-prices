"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 16:59
"""
from pymongo import MongoClient

client = MongoClient()
db = client['sjm_dnf_prices']
coll_price = db['price']
coll_product = db['product']
