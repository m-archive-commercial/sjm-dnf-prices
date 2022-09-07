"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:27
"""
from typing import Union

import pandas as pd

from log import get_logger


logger = get_logger("pandas-dump")


def dump_df2csv(df: Union[pd.DataFrame, pd.Series], fp: str):
    df.to_csv(fp, encoding='utf_8_sig', float_format='%.4f')
    logger.info(f'dumped dataframe into csv file://{fp}')


def dump_series2json(df: pd.Series, fp: str):
    df.to_json(fp, indent=2, force_ascii=False, date_format='iso')
    logger.info(f"dumped dataframe into json file://{fp}")
