## Scrapy

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
```

## Data Structure

1. get data id list via **after login**: `http://dnf.yxwujia.com/a/product/procutType/treeData`

item sample:

```js
{
    id    : "511e9dba8c1246e1a3354c225b4b7418"
    parent: "3fce2f34967249d8bde5b86cbdcc1078"
    text  : "幻化武器"
}
```

2. transform into layered data shape at `sjm_dnf_prices/data/source/treeDataLayered.json` via script `scripts/misc/treeData2Layered.py`

item sample:

```json
{
  "#": {
    "children": {
      "64b8fd16060445419e467f1471e4736d": {
        "text": "特殊装备",
        "children": {
          "b98c6889625840a48e2204021051e0fb": {
            "text": "辅助装备通用",
            "children": {}
          },
          "c4d4872bd34c4278ab19358e2d70123f": {
            "text": "魔法石通用",
            "children": {}
          },
          "fc5842305f53460589c67180a95957a9": {
            "text": "耳环",
            "children": {}
          }
        },
        ...
      }
    }
  }
}
```

3. write the data into db via script `scripts/misc/treeDataLayered2db.py`
