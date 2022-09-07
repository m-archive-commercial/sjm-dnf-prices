"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 14:07
"""
import os

import pandas as pd

from general.db.general import collProduct
from general.db.transform import transProductInDB
from general.df.dump import dump_df2csv
from general.df.join import joinDFs
from general.df.transform import item2df


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
