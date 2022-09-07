"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 17:28
"""
import os
from typing import Union

import pandas as pd

from general.db.general import db, collProduct
from general.db.transform import transProductInDB
from general.df.dump import dump_df2csv
from general.df.join import dnfXdata2DateSeries, joinDFs
from general.df.transform import item2df
from log import getLogger


logger = getLogger("dnf-core")


def createTotalSeries(collName) -> pd.Series:
    coll = db[collName]
    elems = list(coll.find({}))
    series = [createSeries(elem["_id"], collName) for elem in elems]
    fullDF = pd.concat(series, axis=1)
    totalSeries = fullDF.sum(axis=1)  # type: pd.Series
    totalSeries.name = collName + "-total"
    logger.info(f'created total series from coll: [{collName}]')
    return totalSeries


def queryYList(data, collName):
    if collName == "price":
        return [series for series in data['series'] if series['name'] == '平均价'][0]['data']
    return data['series'][0]['data']


def dropDuplicatedIndex(df: Union[pd.DataFrame, pd.Series]):
    """
    without duplicated index dropped, `pd.concat` would raise `ValueError: cannot reindex on an axis with duplicate labels`
    :param df:
    :return:
    """
    return df[~df.index.duplicated()]


def createSeries(productId, collName) -> pd.Series:
    queryInfo = {"productId": productId, "collName": collName}
    item = db[collName].find_one({"_id": productId})
    assert item is not None, queryInfo
    data = item['data']
    assert data is not None, item
    xList = data['xAxis'][0]['data']
    yList = queryYList(data, collName)
    assert len(xList) == len(yList)
    series = pd.Series(index=dnfXdata2DateSeries(xList), data=yList, name=collName)
    series = dropDuplicatedIndex(series)
    return series


def dumpProductsMeta2csv(fp):
    """
    dump index/base.csv

    :param fp:
    :return:
    """
    dump_df2csv(pd.DataFrame([transProductInDB(item) for item in collProduct.find({})]), fp)


def dumpPricesComposite(dfFull, out_prices_composite_dir):
    """
    dump composite/index.csv

    :return:
    """
    composite_path = f'{out_prices_composite_dir}/index.csv'
    dump_df2csv(dfFull, composite_path)


def dumpPricesSingle(elems, out_prices_single_dir):
    for elem in elems:
        L1_name = elem["_id"]['L1_name']
        L2_name = elem["_id"]['L2_name']
        items = elem["items"]
        df = joinDFs(map(item2df, items))

        L1_dir = f'{out_prices_single_dir}/{L1_name}'
        if not os.path.exists(L1_dir):
            os.mkdir(L1_dir)
        L2_path = f'{L1_dir}/{L2_name}.csv'
        dump_df2csv(df, L2_path)
