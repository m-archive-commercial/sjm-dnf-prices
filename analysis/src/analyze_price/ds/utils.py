"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:14
"""
from typing import List

import pandas as pd

from .period import PeriodPoint, PointStatus, PeriodStatus


def getPeriods(col: pd.Series) -> List[PeriodPoint]:
    cur_status = PointStatus.UNKNOWN  # type: PointStatus
    periodPoints = []  # type: List[PeriodPoint]
    for date, data in col.iteritems():
        if pd.isna(data):
            if cur_status != PointStatus.NAN:
                periodPoints.append({"date": date, "status": PeriodStatus.TO_NAN})
            cur_status = PointStatus.NAN
        elif not pd.isna(data):
            if cur_status != PointStatus.NOT_NAN:
                periodPoints.append({"date": date, "status": PeriodStatus.TO_NOT_NAN})
            cur_status = PointStatus.NOT_NAN
    return periodPoints


def getPeriodsCount(col: pd.Series) -> int:
    return len([i for i in getPeriods(col) if i['status'] == PeriodStatus.TO_NOT_NAN])
