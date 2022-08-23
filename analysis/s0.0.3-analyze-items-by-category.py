# %% [markdown]
# ## how to handle concat dataframes with different indices
#
# 1. `pd.concat`, `pd.merge` , `df.join` all works, with method specified as `inner | outer | left | ...`
# 2. but we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`

# %%
from collections import OrderedDict
import os
from os import path
import pymongo
from pymongo.mongo_client import MongoClient
import pandas as pd
from pprint import pprint
from datetime import datetime

# %%
client = MongoClient()
db = client['sjm_dnf_prices']
coll_price = db['price']
coll_product = db['product']
coll_price.count_documents({})

# %% [markdown]
# ### validate
#

# %%
elems = list(coll_price.aggregate([
    {
        "$group": {
            "_id": "$category.L1_name",
            "items": {"$push": {
                "name": {
                    # xxx价格走势图
                    "$substrCP": ["$data.title.text", 0, {
                        "$subtract": [{"$strLenCP": "$data.title.text"}, 5]
                    }],
                },
                "category": "$category",
                "x": {
                    "$arrayElemAt": ["$data.xAxis.data", 0]
                },
                "y": {
                    "$let": {
                        "vars": {
                            "item": {
                                "$arrayElemAt": [
                                    {
                                        "$filter": {
                                            "input": "$data.series",
                                            "as": "item",
                                            "cond": {
                                                "$eq": ["$$item.name", "平均价"]
                                            }
                                        }
                                    },
                                    0
                                ]
                            }
                        },
                        "in": "$$item.data"
                    }
                }
            }}
        }
    }
]))
# %%
vexpr = {
    "collMod": "price",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["category", "data", "name"],
            "properties": {
                "data": {
                    "properties": {
                        "xAxis": {
                            "bsonType": "array",
                            "minItems": 1,
                            "maxItems": 1
                        },
                        "series": {
                            "bsonType": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "uniqueItems": True,
                            "items": {
                                "properties": {
                                    "name": {
                                        "enum": [
                                            "低价",
                                            "平均价",
                                            "高价"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "validationLevel": "strict",
    "validationAction": "error"
}

db.command(OrderedDict(vexpr))

db.validate_collection('price')

# TODO: why no errors, instead of warnings ?

# check log if validated result has `warnings` or `errors`
# client.admin.command( { "getLog": "global" } )


print()


def drop_duplicates_by_index(df, printAtEnd=True) -> pd.DataFrame:
    # we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`
    duplicates = df[df.index.duplicated()]
    if len(duplicates):
        if not printAtEnd:
            for _, row in duplicates.iterrows():
                print(f'duplicated: {dict(date=_, **row)}')
    return df[~df.index.duplicated()]


def getCurTime():
    return datetime.now().strftime('%m-%dT%H-%M')


def item2df(item: dict) -> pd.DataFrame:
    itemName = f"{item['category']['L1_name']}-{item['category']['L2_name']}-{item['name']}"

    df = pd.DataFrame({"x": item['x'], itemName: item['y']})

    df.set_index('x', inplace=True)

    df = drop_duplicates_by_index(df)

    df.name = itemName

    return df


def joinDFs(dataframes, keys=None):
    df = pd.concat(dataframes, axis=1)
    return df.sort_index()

# %% [markdown]
# ## output


out_dir = f'sjm_dnf_price_v0.2.1_{getCurTime()}'
out_prices_dir = path.join(out_dir, "prices")
out_indexes_dir = path.join(out_dir, "indexes")
os.makedirs(out_dir)
os.makedirs(out_prices_dir)
os.makedirs(out_indexes_dir)

def transProductInDB(productItem: dict) -> dict:
    return {
        "L1_name": productItem['category']["L1_name"],
        "L1_id": productItem['category']["L1_id"],
        "L2_name": productItem['category']["L2_name"],
        "L2_id": productItem['category']["L2_id"],
        "name": productItem["name"],
        "id": productItem["_id"],
    }

df_product = pd.DataFrame([transProductInDB(item) for item in coll_product.find({})])
fp_product = f'{out_indexes_dir}/index.csv'
df_product.to_csv(fp_product, encoding='utf_8_sig')
print(f'dumped into file://{fp_product}')

for elem in elems:
    L1_name = elem["_id"]
    items = elem["items"]

    df = joinDFs(map(item2df, items))

    fp = f'{out_prices_dir}/{L1_name}.csv'
    df.to_csv(fp, encoding='utf_8_sig')

    print(f'dumped into file://{fp}')

exit(0)
# %% [markdown]
#

# %% [markdown]
# ### stat of categories of coll_price

# %%
list(coll_price.aggregate([
    {
        "$group": {
            "_id": "$category.L1_name",
            "count": {"$count": {}}
        }
    }
]))

# %% [markdown]
# ## pre-process

# %% [markdown]
# ### check coll_price item

# %%
coll_price.find_one({})

# %% [markdown]
# ## Development debug

# %% [markdown]
# ### failed, since `OperationFailure: Executor error during getMore :: caused by :: BSONObj size: 19345634`
#

# %%
list(coll_price.aggregate([
    {
        "$group": {
            "_id": "$category.L1_name",
            "items": {"$push": "$$ROOT"}
        }
    }
]))
