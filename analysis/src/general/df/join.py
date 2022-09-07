"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:31
"""
import pandas as pd


def dnfXdata2DateSeries(xList):
    return pd.to_datetime([('20' + i).replace('.', '-') for i in xList])


def joinDFs(dataframes):
    """
    how to handle concat dataframes with different indices
        1. `pd.concat`, `pd.merge` , `dfRaw.join` all works, with method specified as `inner | outer | left | ...`
        2. but we should be especially careful about the duplicated indexes, which would lead to the error of `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`

    :param dataframes:
    :param keys:
    :return:
    """
    df = pd.concat(dataframes, axis=1)  # type: pd.DataFrame
    df.columns = sorted(df.columns)  # sort columns
    df.index = dnfXdata2DateSeries(df.index)
    return df.sort_index()
