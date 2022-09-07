## Scrapy

> some helpful scripts (before or after a crawl process) can be found at under `scripts`

0. config

should config the cookie field of `dnf.session.id` in `sjm_dnf_prices/settings.py`

1. fetch product info into like `sjm_dnf_prices/data/source/treeData.json`

```shell
# sjm_dnf_prices/spiders/product.py
scrapy crawl product
```

2. fetch price info from product (tracked by database)

```shell
# sjm_dnf_prices/spiders/price.py
scrapy crawl price
```

## Database

based on Mongodb:

```yaml
URI: localhost:27017
DB_NAME: sjm_dnf_prices
COLL_NAMES:
  - product
  - price  
  - ys
  - zs
```

## Analysis of dnf website

### get the product list with `id | name`, build its tree structure and dump into database

1. get data id list via **after login**: 

```yml
url of tree data: http://dnf.yxwujia.com/a/product/procutType/treeData
```

sample:

```js
{
    id    : "511e9dba8c1246e1a3354c225b4b7418"
    parent: "3fce2f34967249d8bde5b86cbdcc1078"
    text  : "幻化武器"
}
```

2. transform into layered data shape at `sjm_dnf_prices/data/source/treeDataLayered.json` via script `scripts/misc/treeData2Layered.py`

3. write the data into db via script `scripts/misc/treeDataLayered2db.py`

## Output of aggregated data

```shell
cd analysis/src

# generate output data into `analyze/out/xx`
python analyzeAll/main.py
```

sample output structure:

```text
.
├── byGroup
│   ├── 副职业
│   ├── 期限道具
│   ├── 未央幻境装备
│   ├── 武器
│   ├── 消耗品
│   ├── 特殊装备
│   ├── 防具
│   └── 首饰
├── products.csv
├── versions.txt
├── ys-total.json
└── zs-total.json

```
