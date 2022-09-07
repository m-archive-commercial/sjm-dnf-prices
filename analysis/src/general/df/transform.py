"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:31
"""
import json

import pandas as pd

from log import get_logger

logger = get_logger('pandas-transform')


def item2df(item: dict, withNamesLevel=0) -> pd.DataFrame:
    """
    将处理过的 item 转成 dfRaw
    :param item:
    :param withNamesLevel:
    :return:
    """

    def drop_duplicates_by_index(df) -> pd.DataFrame:
        """
        pandas 输出的时候，行不能重复，所以需要去重
        :param df:
        :return:
        """
        # we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`
        duplicates = df[df.index.duplicated()]
        if len(duplicates):
            for _, row in duplicates.iterrows():
                logger.warn(f'duplicated: {dict(date=_, **row)}')
        return df[~df.index.duplicated()]

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
