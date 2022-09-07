"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 16:41
"""
from enum import Enum


class STATUS(str, Enum):
    OK = "OK"
    PASSED_FOR_INTERNAL_SERVER_ERROR = "passed for 500 internal server"
    PASSED_FOR_KOREAN_ONLY = "passed for korean only"
    FAILED_FOR_TOO_FREQUENT = "failed for too frequent"
    UNKNOWN = "unknown"


PASSED_STATUSES_WITH_PRICE = [
    STATUS.OK,
    STATUS.PASSED_FOR_INTERNAL_SERVER_ERROR,
    STATUS.PASSED_FOR_KOREAN_ONLY
]

FIELD_WITH_PRICE = "withPrice"
FIELD_WITH_YS = "withYS"
FIELD_WITH_ZS = "withZS"

SPIDER_PRICE_NAME = "price"
COLL_PRICE_NAME = SPIDER_PRICE_NAME

SPIDER_PRODUCT_NAME = "product"
COLL_PRODUCT_NAME = SPIDER_PRODUCT_NAME
