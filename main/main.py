import time
import pandas as pd

from market.marketdata import get_data_from_csv
from trade.calibration_strats import above_under_ma_std_calib
from trade.simple_strats import above_under_ma_std, macd_crossing_singal_line


def main():
    df1 = get_data_from_csv('../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    df2 = get_data_from_csv('../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')

    df3 = get_data_from_csv('../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    df4 = get_data_from_csv('../resources/ETH_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df5 = get_data_from_csv('../resources/BTC_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df6 = pd.read_csv('../resources/BTC_USD_2020-01-22_2020-01-27_Hourly.csv')
    df6['Low'].astype(float)
    df6['High'].astype(float)
    df6.loc[:, 'Currency'] = 'BTC'
    df6['Date'] = pd.to_datetime(df6['Timestamp'])

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    start = time.time()

    macd_crossing_singal_line(df6, stds=0, log=True, draw=True)
    # above_under_ma_std_calib(df6, 14, log=True, draw=True, threaded=False)
    # above_under_ma_std(df1, stds=1.5, log=True, draw=True)

    exec_time = time.time() - start
    print(f'Backtesting ran for {exec_time} seconds')


main()
