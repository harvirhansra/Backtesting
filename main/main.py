import time
import pandas as pd

from market.marketdata import get_data_from_csv
from trade.calibration_strats import above_under_ma_std_calib
from trade.simple_strats import above_under_ma_std, macd_crossing_signal_line


def main():
    # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-23_Gemini_Daily.csv')
    df = get_data_from_csv('../resources/BTC_USD_2018-07-01_2020-05-23_Gemini_Daily.csv')

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    start = time.time()

    # macd_crossing_singal_line(df1, log=True, draw=False)
    above_under_ma_std_calib(df, lookback=14, log=True, draw=False, multi=False)
    # above_under_ma_std(df, std=1, lookback=14, log=True, draw=False)

    exec_time = time.time() - start
    print(f'Backtesting ran for {exec_time} seconds')

if __name__ == '__main__':
    main()