"""
source: own
author: https://github.com/MarkShawn2020
create: Aug 26, 2022, 12:12
"""

from analyze_price.ds.utils import getPeriodsCount
from general.df.utils import get_latest_composite_prices_df


df = get_latest_composite_prices_df()
df2 = df.apply(getPeriodsCount, axis=0).T
