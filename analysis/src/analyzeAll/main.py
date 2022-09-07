"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 15:28
"""
import os
import shutil

import pandas as pd

from general.core import createTotalSeries, createSeries, dumpProductsMeta2csv
from general.db.general import db
from general.df.dump import dump_df2csv, dump_series2json
from general.general import getCurTime, packOut
from path import OUT_DIR, SRC_DIR
from log import getLogger
from versions import VERSION

WITH_PCT = True
DUMP_SCORE = True  # need `WITH_PCT = True`

DUMP_TOTAL = True
DUMP_GROUP = True

PACK_OUT = True

if __name__ == '__main__':

    logger = getLogger('analyze-all-main')

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
    if DUMP_TOTAL:
        shutil.copyfile(os.path.join(SRC_DIR, "versions.py"), os.path.join(outDir, "versions.txt"))
        dumpProductsMeta2csv(os.path.join(outDir, "products.csv"))

    if DUMP_GROUP:
        byGroupDir = os.path.join(outDir, "byGroup")
        os.mkdir(byGroupDir)

    # by total
    if WITH_PCT:
        ysTotalSeries = createTotalSeries("ys")
        zsTotalSeries = createTotalSeries("zs")
        if DUMP_TOTAL:
            dump_series2json(ysTotalSeries, os.path.join(outDir, "ys-total.json"))
            dump_series2json(zsTotalSeries, os.path.join(outDir, "zs-total.json"))

    # by group
    ysScoreSeriesList = []
    zsScoreSeriesList = []
    for productGroup in productGroupedList:
        L1Name = productGroup['_id']["L1_name"]
        L2Name = productGroup['_id']["L2_name"]

        productItems = productGroup["items"]
        if DUMP_GROUP:
            L1Dir = os.path.join(byGroupDir, L1Name)
            if not os.path.exists(L1Dir):
                os.mkdir(L1Dir)
            L2Dir = os.path.join(L1Dir, L2Name)
            os.mkdir(L2Dir)
            L2IndexSeries = pd.Series(dict((item["id"], item["name"]) for item in productItems))
            dump_series2json(L2IndexSeries, os.path.join(L2Dir, "index.json"))
        for productItem in productItems:
            productId = productItem["id"]
            productName = productItem["name"]
            productFullName = f'{L1Name}-{L2Name}-{productName}'

            priceSeries = createSeries(productId, "price")
            ysSeries = createSeries(productId, "ys")
            zsSeries = createSeries(productId, "zs")

            if WITH_PCT:
                # align total series to ys/zs series
                ysPctSeries = ysSeries / ysTotalSeries[ysSeries.index]
                ysPctSeries.name = "ys-pct"
                ysScoreDF = ysPctSeries * priceSeries  # type: pd.Series
                ysScoreDF.name = "ys-score"
                ysScoreSeriesForConcat = ysScoreDF.copy()
                ysScoreSeriesForConcat.name = productId
                ysScoreSeriesList.append(ysScoreSeriesForConcat)

                zsPctSeries = zsSeries / zsTotalSeries[zsSeries.index]
                zsPctSeries.name = "zs-pct"
                zsScoreSeries = zsPctSeries * priceSeries
                zsScoreSeries.name = "zs-score"
                zsScoreSeriesForConcat = zsScoreSeries.copy()
                zsScoreSeriesForConcat.name = productId
                zsScoreSeriesList.append(zsScoreSeriesForConcat)

            if DUMP_GROUP:
                productInfo = {
                    "id"    : productId,
                    "path"  : productFullName,
                    "length": {"price": len(priceSeries), "ys": len(ysSeries), "zs": len(zsSeries)}
                }
                logger.info(f'handling {productInfo}')
                # price | ys | zs 的长度不一定相等:
                #   failed case: {'id': '1683', 'path': '消耗品-其他-+12 青铜装备强化券 (30天)（旧）', 'length': {'price': 1120, 'ys': 1119, 'zs': 398}}
                #   passed case: {'id': '7872', 'path': '首饰-戒指-蓬勃生命的落幕', 'length': {'price': 445, 'ys': 445, 'zs': 445}}
                # - assert len(priceSeries) == len(ysSeries) == len(zsSeries), productInfo

                toConcatSeries = [priceSeries, ysSeries, zsSeries]
                if WITH_PCT:
                    toConcatSeries.extend([ysPctSeries, zsPctSeries, ysScoreDF, zsScoreSeries])
                productDF = pd.concat(toConcatSeries, axis=1)
                productInfo['length']['concat'] = len(productDF)
                # concentrating with different elements has possibility to be bigger
                assert len(productDF) >= max(len(priceSeries), len(ysSeries), len(zsSeries)), productInfo
                dump_df2csv(productDF, os.path.join(L2Dir, productId + ".csv"))

    # generate ys/zs score indices
    if DUMP_SCORE:
        ysScoreDF = pd.concat(ysScoreSeriesList, axis=1)
        zsScoreDF = pd.concat(zsScoreSeriesList, axis=1)
        ysScoreIndexSeries = ysScoreDF.sum(axis=1)
        ysScoreIndexSeries.name = 'ys'
        zsScoreIndexSeries = zsScoreDF.sum(axis=1)
        zsScoreIndexSeries.name = 'zs'
        scoreIndexDF = pd.concat([ysScoreIndexSeries, zsScoreIndexSeries], axis=1)
        dump_df2csv(ysScoreDF, os.path.join(outDir, 'ys-score_detailed.csv'))
        dump_df2csv(zsScoreDF, os.path.join(outDir, 'zs-score_detailed.csv'))
        dump_df2csv(scoreIndexDF, os.path.join(outDir, 'score.csv'))

    if PACK_OUT:
        packOut(outDir)
    logger.info("=== finished ===")