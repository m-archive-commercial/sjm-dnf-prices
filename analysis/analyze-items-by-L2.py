# %% [markdown]
# ## how to handle concat dataframes with different indices
#
# 1. `pd.concat`, `pd.merge` , `df.join` all works, with method specified as `inner | outer | left | ...`
# 2. but we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`

# %%
import json
import os
from os import path
import pandas as pd
from base import coll_price, coll_product
from utils import transProductInDB, getCurTime, item2df, joinDFs, dump_csv, getPeriodsCount, getPeriods

with open('agg_get_elems.json', 'r') as f:
    elems = list(coll_price.aggregate([json.load(f)]))

# VERSION = '0.2.2' # added feat of column sort
# VERSION = '0.3.0'  # finished crawl, added withPrice status
# VERSION = '0.4.0'  # added L2 category
# VERSION = '0.4.1'  # fixed 500
# VERSION = '0.4.2'  # enabled composite prices
# VERSION = '0.4.3'  # feat: enabled standard datetime index
# VERSION = '0.4.4'  # feat: added periods info
VERSION = '0.5.0'  # bug: fixed periods dump

out_dir = f'output/sjm_dnf_price_v{VERSION}_{getCurTime()}'
os.makedirs(out_dir)

out_prices_dir = path.join(out_dir, "prices")
os.makedirs(out_prices_dir)

df_product = pd.DataFrame([transProductInDB(item) for item in coll_product.find({})])
out_indexes_dir = path.join(out_dir, "indexes")
os.makedirs(out_indexes_dir)
fp_product = f'{out_indexes_dir}/basic.csv'
dump_csv(df_product, fp_product)

# dump composite
all_elems = [item for elem in elems for item in elem['items']]
dfs = joinDFs([item2df(item, withNamesLevel=2) for item in all_elems])
out_prices_composite_dir = path.join(out_prices_dir, 'composite')
os.makedirs(out_prices_composite_dir)
composite_path = f'{out_prices_composite_dir}/index.csv'
dump_csv(dfs, composite_path)

# dump periods
dfs_periods = dfs.apply(getPeriods, axis=0).T  # type: pd.Series
# 未央幻境装备-辟邪玉-传说辟邪玉 [荣誉祝福]、[勇气祝福]、[禁忌诅咒]物理、魔法和独立攻击增加%3/4/5 重复
dfs_periods.drop_duplicates(inplace=True)
periods_fp = f'{out_indexes_dir}/periods.json'
dfs_periods.to_json(periods_fp, indent=2, force_ascii=False, date_format='iso')
print(f'dumped periods data info json file://{periods_fp}')

# dump single
out_prices_single_dir = path.join(out_prices_dir, 'single')
os.makedirs(out_prices_single_dir)
for elem in elems:
    L1_name = elem["_id"]['L1_name']
    L2_name = elem["_id"]['L2_name']
    items = elem["items"]
    df = joinDFs(map(item2df, items))

    L1_dir = f'{out_prices_single_dir}/{L1_name}'
    os.makedirs(L1_dir, exist_ok=True)
    L2_path = f'{L1_dir}/{L2_name}.csv'
    dump_csv(df, L2_path)

ZIP_COMMAND = f"zip {out_dir}.zip -r {out_dir}"
os.system(ZIP_COMMAND)

exit(0)
