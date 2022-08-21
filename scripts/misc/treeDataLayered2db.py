"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 22, 2022, 01:01
"""
import json

from sjm_dnf_prices.settings import DATA_SOURCE_DIR


def queryTreeDataWithLayers():
    with open(DATA_SOURCE_DIR / 'treeDataLayered.json', 'r') as f:
        data = json.load(f)

        for L1_id, L1_data in data['#']['children'].items():
            for L2_id, L2_data in L1_data['children'].items():
                item = {
                    "L1-ID"  : L1_id,
                    "L1-name": L1_data['text'],
                    "L2-ID"  : L2_id,
                    "L2-name": L2_data["text"]
                }
                yield item
