"""
source: own
author: https://github.com/MarkShawn2020
create: Sep 07, 2022, 13:38
"""
import os

import pandas as pd

from path import OUT_DIR


def get_latest_composite_prices_df():
    """
    获取最新输出的价格文件夹内的指数表
    :return:
    """

    def get_latest_output_dir():
        fps = [os.path.join(OUT_DIR, i) for i in os.listdir(OUT_DIR)]
        fps_dir = [i for i in fps if os.path.isdir(i)]
        return sorted(fps_dir)[-1]

    latest_composite_prices_fp = os.path.join(get_latest_output_dir(), 'prices/composite/index.csv')
    df_latest_composite_prices = pd.read_csv(latest_composite_prices_fp, index_col=0)
    # date sample: 17.06.14
    df_latest_composite_prices.index = pd.to_datetime(df_latest_composite_prices.index)
    return df_latest_composite_prices
