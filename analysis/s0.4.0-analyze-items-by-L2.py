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
from utils import transProductInDB, getCurTime, item2df, joinDFs

with open('agg_get_elems.json', 'r') as f:
    elems = list(coll_price.aggregate([json.load(f)]))

VERSION = '0.4.0'  # added L2 category
# VERSION = '0.3.0'  # finished crawl, added withPrice status
# VERSION = '0.2.2' # added feat of column sort

out_dir = f'output/sjm_dnf_price_v{VERSION}_{getCurTime()}'
out_prices_dir = path.join(out_dir, "prices")
out_indexes_dir = path.join(out_dir, "indexes")
os.makedirs(out_dir)
os.makedirs(out_prices_dir)
os.makedirs(out_indexes_dir)

df_product = pd.DataFrame([transProductInDB(item) for item in coll_product.find({})])
fp_product = f'{out_indexes_dir}/index.csv'
df_product.to_csv(fp_product, encoding='utf_8_sig')
print(f'dumped into file://{fp_product}')

for elem in elems:
    L1_name = elem["_id"]['L1_name']
    L2_name = elem["_id"]['L2_name']
    items = elem["items"]

    df = joinDFs(map(item2df, items))

    fd = f'{out_prices_dir}/{L1_name}'
    os.makedirs(fd, exist_ok=True)
    fp = f'{fd}/{L2_name}.csv'
    df.to_csv(fp, encoding='utf_8_sig')

    print(f'dumped into file://{fp}')

exit(0)
