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

logger = getLogger('analyze-all-main')

TARGETS = ['ys', 'zs']

WITH_PCT = True
DUMP_SCORE = True  # need `WITH_PCT = True`

DUMP_TOTAL = True
DUMP_GROUP = True

PACK_OUT = True

if __name__ == '__main__':

    targetDict = dict()
    for target in TARGETS:
        targetDict[target] = {
            "scoreSeriesList": []
        }

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
    for target in targetDict:
        targetDict[target]['totalSeries'] = createTotalSeries(target)
        if DUMP_TOTAL:
            dump_series2json(targetDict[target]['totalSeries'], os.path.join(outDir, target + "-total.json"))

    # by group
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
            for target in targetDict:
                targetDict[target]['series'] = createSeries(productId, target)

            if WITH_PCT:
                for target in targetDict:
                    series = targetDict[target]['series']
                    # align total series to ys/zs series
                    targetDict[target]['pctSeries'] = pctSeries = series / targetDict[target]['totalSeries'][
                        series.index]
                    pctSeries.name = target + "-pct"
                    targetDict[target]['scoreSeries'] = scoreSeries = pctSeries * priceSeries  # type: pd.Series
                    scoreSeries.name = target + "-score"
                    scoreSeriesForConcat = scoreSeries.copy()
                    scoreSeriesForConcat.name = productId
                    targetDict[target]['scoreSeriesList'].append(scoreSeriesForConcat)

            if DUMP_GROUP:
                targetSeriesList = [targetDict[target]['series'] for target in targetDict]
                toConcatSeries = [priceSeries, *targetSeriesList]
                if WITH_PCT:
                    for field in ['pctSeries', 'scoreSeries']:
                        for target in targetDict:
                            toConcatSeries.append(targetDict[target][field])
                productDF = pd.concat(toConcatSeries, axis=1)
                # concentrating with different elements has possibility to be bigger
                dump_df2csv(productDF, os.path.join(L2Dir, productId + ".csv"))

    # generate ys/zs score indices
    if DUMP_SCORE:
        scoreIndexSeriesList = []
        for target in targetDict:
            scoreDF = pd.concat(targetDict[target]['scoreSeriesList'], axis=1)
            scoreIndexSeries = scoreDF.sum(axis=1)
            scoreIndexSeries.name = target
            dump_df2csv(scoreDF, os.path.join(outDir, target + '-score_detailed.csv'))
            scoreIndexSeriesList.append(scoreIndexSeries)
        dump_df2csv(pd.concat(scoreIndexSeriesList, axis=1), os.path.join(outDir, 'score.csv'))

    if PACK_OUT:
        packOut(outDir)
    logger.info("=== finished ===")
