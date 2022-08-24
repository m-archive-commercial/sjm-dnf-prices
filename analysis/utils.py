"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 24, 2022, 17:02
"""
from datetime import datetime

import pandas as pd


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
    return df.sort_index()