"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 17:02
"""
import os
from datetime import datetime
from typing import List

import pandas as pd

from ds import PointStatus, PeriodStatus, PeriodPoint


def transProductInDB(productItem: dict) -> dict:
    try:
        item = {
            "L1_name": productItem['category']["L1_name"],
            "L1_id"  : productItem['category']["L1_id"],
            "L2_name": productItem['category']["L2_name"],
            "L2_id"  : productItem['category']["L2_id"],
            "name"   : productItem["name"],
            "id"     : productItem["_id"],
            "status" : productItem['withPrice']
        }
        return item
    except Exception as e:
        print(productItem)
        raise e


def drop_duplicates_by_index(df, printAtEnd=True) -> pd.DataFrame:
    # we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`
    duplicates = df[df.index.duplicated()]
    if len(duplicates):
        if not printAtEnd:
            for _, row in duplicates.iterrows():
                print(f'duplicated: {dict(date=_, **row)}')
    return df[~df.index.duplicated()]


def getCurTime():
    return datetime.now().strftime('%m-%dT%H-%M')


def item2df(item: dict, withNamesLevel=0) -> pd.DataFrame:
    itemName = item['name']
    if withNamesLevel >= 1:
        itemName = f"{item['category']['L2_name']}-{itemName}"
    if withNamesLevel >= 2:
        itemName = f"{item['category']['L1_name']}-{itemName}"

    df = pd.DataFrame({"x": item['x'], itemName: item['y']})

    df.set_index('x', inplace=True)

    df = drop_duplicates_by_index(df)

    df.name = itemName

    return df


def joinDFs(dataframes, keys=None):
    df = pd.concat(dataframes, axis=1)  # type: pd.DataFrame
    # sort columns
    df.columns = sorted(df.columns)
    df.index = pd.to_datetime([('20' + i).replace('.', '-') for i in df.index])
    return df.sort_index()


def dump_csv(df: pd.DataFrame, fp: str):
    df.to_csv(fp, encoding='utf_8_sig')
    print(f'dumped dataframe into csv file://{fp}')


def get_latest_composite_prices_df():
    def get_latest_output_dir():
        fps = [os.path.join(output_dir, i) for i in os.listdir(output_dir)]
        fps_dir = [i for i in fps if os.path.isdir(i)]
        return sorted(fps_dir)[-1]

    output_dir = 'output'

    latest_composite_prices_fp = os.path.join(get_latest_output_dir(), 'prices/composite/index.csv')
    df_latest_composite_prices = pd.read_csv(latest_composite_prices_fp, index_col=0)
    # date sample: 17.06.14
    df_latest_composite_prices.index = pd.to_datetime(df_latest_composite_prices.index)
    return df_latest_composite_prices


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