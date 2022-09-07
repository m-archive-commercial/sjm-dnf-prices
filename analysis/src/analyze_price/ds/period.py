"""
source: own
author: https://github.com/MarkShawn2020
create: Aug 26, 2022, 13:06
"""
from enum import Enum
from typing import TypedDict, Any


class PointStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    NAN = "NAN"
    NOT_NAN = "NOT_NAN"


class PeriodStatus(str, Enum):
    TO_NOT_NAN = 'TO_NOT_NAN'
    TO_NAN = 'TO_NAN'
    KEEPS_NAN = 'KEEPS_NAN'
    KEEPS_NOT_NAN = 'KEEPS_NOT_NAN'


class PeriodPoint(TypedDict):
    date: Any
    status: PeriodStatus
