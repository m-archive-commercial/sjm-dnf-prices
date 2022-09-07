import json
import os
from os import path

from general.df.dump import dump_df2csv
from versions import VERSION
from path import OUT_DIR
from general.db.general import db
from general.df.join import joinDFs
from general.df.transform import item2df
from general.general import getCurTime, packOut

from general.core import dumpProductsMeta2csv, dumpPricesComposite


if __name__ == '__main__':

    for collName in ['ys', 'zs']:
        with open(os.path.join(os.path.dirname(__file__), "config-db_agg-get-elems-on-yszs.json"), 'r') as f:
            subtype = collName
            elemList = list(db[collName].aggregate([json.load(f)]))

        outDir = os.path.join(OUT_DIR, f'sjm-dnf_v{VERSION}_{subtype}_{getCurTime()}')
        os.mkdir(outDir)

        outIndexesDir = path.join(outDir, "indexes")
        os.mkdir(outIndexesDir)

        outSubDir = path.join(outDir, subtype)
        os.mkdir(outSubDir)

        outSubCompositeDir = path.join(outSubDir, 'composite')
        os.mkdir(outSubCompositeDir)

        outSubSingleDir = path.join(outSubDir, "single")
        os.mkdir(outSubSingleDir)

        # 得到一整张大表
        dfFull = joinDFs(
            [item2df(item, withNamesLevel=2) for item in [item for elem in elemList for item in elem['items']]])
        dfTotal = dfFull.sum(axis=1)
        dfTotal.name = 'total'  # necessary

        # dump sub by single
        for elem in elemList:
            L1_name = elem["_id"]['L1_name']
            L2_name = elem["_id"]['L2_name']
            L1_dir = f'{outSubSingleDir}/{L1_name}'
            if not os.path.exists(L1_dir):
                os.mkdir(L1_dir)

            dfRaw = joinDFs(map(item2df, elem["items"]))
            dfPct = dfRaw.apply(lambda x: x / dfTotal * 100)
            dump_df2csv(dfRaw, f'{L1_dir}/{L2_name}_raw.csv')
            dump_df2csv(dfPct, f'{L1_dir}/{L2_name}_pct.csv')

        dump_df2csv(dfTotal, os.path.join(outSubCompositeDir, f"total-{subtype}.csv"))
        dumpProductsMeta2csv(os.path.join(outIndexesDir, "index.csv"))
        dumpPricesComposite(dfFull, outSubCompositeDir)

        packOut(outDir)
