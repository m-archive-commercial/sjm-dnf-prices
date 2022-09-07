"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 15:28
"""
import os
from typing import Union

import pandas as pd

from core import dumpProductsMeta2csv
from general.db.general import db
from general.df.dump import dump_df2csv, dump_series2json
from general.df.join import dnfXdata2DateSeries
from general.general import getCurTime, packOut
from general.path import OUT_DIR
from log import get_logger
from versions import VERSION


def createTotalSeries(collName) -> pd.Series:
    coll = db[collName]
    elems = list(coll.find({}))
    series = [createSeries(elem["_id"], collName) for elem in elems]
    fullDF = pd.concat(series, axis=1)
    totalSeries = fullDF.sum(axis=1)  # type: pd.Series
    totalSeries.name = collName + "-total"
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


if __name__ == '__main__':

    logger = get_logger('analyze-all-main')

    targetQuery = {
        "withPrice": "OK",
        "withYS"   : "OK",
        "withZS"   : "OK"
    }
    productList = list(db['product'].find(targetQuery))
    productGroupedList = list(db['product'].aggregate([
        {
            "$match": targetQuery
        },
        {
            "$group": {
                "_id"  : {
                    "L1_name": "$category.L1_name",
                    "L2_name": "$category.L2_name",
                },
                "items": {
                    "$push": {
                        "id"  : "$id",
                        "name": "$name"
                    }
                }
            }
        }
    ]))

    outDir = os.path.join(OUT_DIR, f'sjm-dnf_v{VERSION}_{getCurTime()}')
    os.mkdir(outDir)

    statDir = os.path.join(outDir, "stat")
    os.mkdir(statDir)

    groupedDir = os.path.join(outDir, "grouped")
    os.mkdir(groupedDir)

    # by total
    dumpProductsMeta2csv(os.path.join(outDir, "products.csv"))
    ysTotalSeries = createTotalSeries("ys")
    dump_series2json(ysTotalSeries, os.path.join(statDir, "ys-total.json"))
    zsTotalSeries = createTotalSeries("zs")
    dump_series2json(zsTotalSeries, os.path.join(statDir, "zs-total.json"))

    # by group
    for productGroup_ in productGroupedList:
        L1_name_ = productGroup_['_id']["L1_name"]
        L2_name_ = productGroup_['_id']["L2_name"]
        groupL1dir_ = os.path.join(groupedDir, L1_name_)
        if not os.path.exists(groupL1dir_):
            os.mkdir(groupL1dir_)
        groupL2dir_ = os.path.join(groupL1dir_, L2_name_)
        os.mkdir(groupL2dir_)

        for productItem in productGroup_["items"]:
            productName = productItem["name"]
            productFullName = f'{L1_name_}-{L2_name_}-{productName}'

            productId = productItem["id"]
            # cannot mkdir based on productName since `/` existed
            productDir = os.path.join(groupL2dir_, productId)
            os.mkdir(productDir)

            priceSeries = createSeries(productId, "price")
            ysSeries = createSeries(productId, "ys")
            ysPctSeries = ysSeries.apply(lambda x: x / ysTotalSeries * 100)

            zsSeries = createSeries(productId, "zs")
            zsPctSeries = zsSeries.apply(lambda x: x / zsTotalSeries * 100)

            productInfo = {
                "id"    : productId,
                "path"  : productFullName,
                "length": {
                    "price": len(priceSeries),
                    "ys"   : len(ysSeries),
                    "zs"   : len(zsSeries)
                }
            }
            logger.info(f'handling {productInfo}')
            # price | ys | zs 的长度不一定相等:
            #   failed case: {'id': '1683', 'path': '消耗品-其他-+12 青铜装备强化券 (30天)（旧）', 'length': {'price': 1120, 'ys': 1119, 'zs': 398}}
            #   passed case: {'id': '7872', 'path': '首饰-戒指-蓬勃生命的落幕', 'length': {'price': 445, 'ys': 445, 'zs': 445}}
            # - assert len(priceSeries) == len(ysSeries) == len(zsSeries), productInfo

            productDF = pd.concat([
                priceSeries,
                ysSeries,
                ysPctSeries,
                zsSeries,
                zsPctSeries,
            ], axis=1)
            productInfo['length']['concat'] = len(productDF)
            # concentrating with different elements has possibility to be bigger
            assert len(productDF) >= max(len(priceSeries), len(ysSeries), len(zsSeries)), productInfo
            dump_df2csv(productDF, os.path.join(productDir, "data.csv"))

    packOut(outDir)
    logger.info("=== finished ===")
