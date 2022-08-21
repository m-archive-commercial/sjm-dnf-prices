"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 22, 2022, 07:23
"""
from urllib.parse import quote


def getPriceUrl(name: str):
    nameQuoted = quote(name)
    return f'http://dnf.yxwujia.com/a/query/data?server=qqqfpj&wpmc={nameQuoted}&type=&startDate=2016-01-01&endDate=2022-08-20&unit=yxb&low=djx&avg=pjjx&high=gjx&period=day'