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
    # name = scrapy.Field()
    success: bool  # default: True
    errorCode: str  # {type:int, sample: -1}
    msg: str  # default： 操作成功
    data: dict
    category: dict
    _id: str  # int
    coll_name: str

    def getName(self):
        try:
            return self.data["title"]['text']
        except:
            pprint(self.__dict__)
            return ''

    def __repr__(self):
        return f"PriceItem(id={self._id}, name={self.getName()}, success={self.success}, msg={self.msg}, category={printCategory(self.category)})"
