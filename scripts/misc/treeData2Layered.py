"""
source: own
author: https://github.com/MarkShawn2020
create: 8月 20, 2022, 23:42
"""
from __future__ import annotations
import json
from collections import defaultdict
from pprint import pprint
from typing import TypedDict, Dict, Optional, DefaultDict, List

from sjm_dnf_prices.settings import DATA_SOURCE_DIR

with open(DATA_SOURCE_DIR / 'treeData.json', 'r') as f:
    treeDataList = json.load(f)


class Node(TypedDict):
    text: str
    children: DefaultDict[str, lambda x: Node]


treeRoot = defaultdict(lambda: defaultdict(Node))

treeMap = defaultdict(list)


def getNode(p: List[str]):
    print(f"treeRoot: {treeRoot}")
    print(f"treeMap: {treeMap}")
    print(f'getNode from path: {p}')
    k = treeRoot
    for s in p:
        k = k[s]
    return k


def popNode(p: List[str]):
    k = treeRoot
    for s in p[:-1]:
        k = k[s]
    return k.pop(p[-1])


for item in treeDataList:
    id: str = item['id']
    parentId = item["parent"]
    text = item["text"]

    # if id == '3fce2f34967249d8bde5b86cbdcc1078': print('')
    if parentId == '#' and text == '防具':
        print('')
    # print({"id": id, "pid": parentId, "text": text})

    # 新的父级与子级
    if parentId not in treeMap:
        assert id not in treeMap
        treeRoot[parentId]["children"][id] = {"text": text, "children": {}}
        treeMap[parentId] = [parentId]
        treeMap[id] = [parentId, 'children', id]
        # print(f'added treeRoot: {treeRoot}')

    # 父级已在x
    else:
        # 父在子不在，合并到父级，父级不用变
        if id not in treeMap:
            getNode(treeMap[parentId])["children"][id] = {"text": text, "children": {}}
            treeMap[id] = [*treeMap[parentId], 'children', id]

        # 父子级都在map（并非严格上下级）中，则需要变动
        else:
            # 之前父级直接盲加的，可能没有text信息
            getNode(treeMap[parentId])['children'][id] = {**popNode(treeMap[id]), "text": text}
            treeMap[id] = [*treeMap[parentId], 'children', id]

    pprint({"id": id, "parentId": parentId, 'text': text, "treeRoot": treeRoot, "treeMap": treeMap})
    print()

with open(DATA_SOURCE_DIR / 'treeDataLayered.json', 'w') as f:
    json.dump(treeRoot, f, ensure_ascii=False, indent=2)

with open(DATA_SOURCE_DIR / 'treeDataMap.json', 'w') as f:
    json.dump(treeMap, f, ensure_ascii=False, indent=2)
