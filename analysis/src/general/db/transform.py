"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:22
"""
from log import get_logger

logger = get_logger('utils-db')


def transProductInDB(product: dict) -> dict:
    """
    将 product 数据库里的条目，转变成具有层次结构的条目，方便后续分组输出
    :param product:
    :return:
    """
    try:
        item = {
            "L1_name": product['category']["L1_name"],
            "L1_id"  : product['category']["L1_id"],
            "L2_name": product['category']["L2_name"],
            "L2_id"  : product['category']["L2_id"],
            "name"   : product["name"],
            "id"     : product["_id"],
            "status" : product['withPrice']
        }
        return item
    except Exception as e:
        logger.error(f"failed to transform product: {product}")
        raise e
