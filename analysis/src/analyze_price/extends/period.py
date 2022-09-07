"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 14:10
"""
import pandas as pd

from general.df.dump import dump_series2json
from analyze_price.ds.utils import getPeriods


def dumpIndexesPeriods(dfFull, out_indexes_dir):
    # dump periods
    dfsPeriods = dfFull.apply(getPeriods, axis=0).T  # type: pd.Series
    # 未央幻境装备-辟邪玉-传说辟邪玉 [荣誉祝福]、[勇气祝福]、[禁忌诅咒]物理、魔法和独立攻击增加%3/4/5 重复
    dfsPeriods.drop_duplicates(inplace=True)
    periods_fp = f'{out_indexes_dir}/periods.json'
    dump_series2json(dfsPeriods, periods_fp)
