"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 23:34
"""
from scripts.before_crawl.db_clear_price_invalid import coll_price

data = [i['data'] for i in coll_price.find({})]
