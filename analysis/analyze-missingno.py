from utils import get_latest_composite_prices_df


if __name__ == '__main__':
    import missingno as msno

    df = get_latest_composite_prices_df()
    msno.matrix(df.iloc[:, :1000])
    msno.matrix(df.iloc[:, 1000:2000]);
    msno.matrix(df.iloc[:, 2000:3000]);
