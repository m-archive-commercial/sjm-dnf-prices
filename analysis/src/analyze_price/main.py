# %% [markdown]
# ## how to handle concat dataframes with different indices
#
# 1. `pd.concat`, `pd.merge` , `dfRaw.join` all works, with method specified as `inner | outer | left | ...`
# 2. but we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`

# %%
import json
import os
from os import path

from general.df.join import joinDFs
from versions import VERSION
from analyze_price.extends.period import dumpIndexesPeriods
from core import dumpProductsMeta2csv, dumpPricesComposite, dumpPricesSingle
from general.db.general import collPrice, collProduct, db
from general.path import OUT_DIR
from log import get_logger
from general.df.transform import item2df
from general.general import getCurTime, packOut


if __name__ == '__main__':
    logger = get_logger("dump-prices")

    subtype = 'price'
    outDir = os.path.join(OUT_DIR, f'sjm-dnf_v{VERSION}_{subtype}_{getCurTime()}')
    os.mkdir(outDir)

    outPricesDir = path.join(outDir, "prices")
    os.mkdir(outPricesDir)

    outPricesCompositeDir = path.join(outPricesDir, 'composite')
    os.mkdir(outPricesCompositeDir)

    outPricesSingleDir = path.join(outPricesDir, 'single')
    os.mkdir(outPricesSingleDir)

    outIndexesDir = path.join(outDir, "indexes")
    os.mkdir(outIndexesDir)

    with open(os.path.join(os.path.dirname(__file__), 'config-db_agg-get-elems-on-price.json'), 'r') as f:
        elemList = list(db['price'].aggregate([json.load(f)]))
        # 得到一整张大表
        dfFull = joinDFs(
            [item2df(item, withNamesLevel=2) for item in [item for elem in elemList for item in elem['items']]])

    dumpProductsMeta2csv(collProduct, os.path.join(outIndexesDir, "index.csv"))
    dumpIndexesPeriods(dfFull, outIndexesDir)
    dumpPricesComposite(dfFull, outPricesCompositeDir)
    dumpPricesSingle(elemList, outPricesSingleDir)

    packOut(outDir)
