# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass
from pprint import pprint

import scrapy
from scrapy import Field

from scripts.misc.printCategory import printCategory


@dataclass
class PriceItem:
    # define the fields for your itemInPrice here like:
    name: str
    success: bool  # default: True
    errorCode: str  # {type:int, sample: -1}
    msg: str  # default： 操作成功
    data: dict
    category: dict
    _id: str  # int
    coll_name: str

    def __repr__(self):
        return f"PriceItem(collName={self.coll_name}, id={self._id}, name={self.name}, success={self.success}, msg={self.msg}, category={printCategory(self.category)})"
