"""
source: own
author: https://github.com/MarkShawn2020
create: Aug 26, 2022, 12:12
"""

from utils import get_latest_composite_prices_df, getPeriodsCount


df = get_latest_composite_prices_df()
df2 = df.apply(getPeriodsCount, axis=0).T
