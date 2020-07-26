import time
import pandas as pd

from market.marketdata import get_data_from_csv
from trade.strategery import AboveUnderMAStd, MACD, MACDZero, RSI, RSIandMACD, RSIdelay, MA50MA10

def main():
    # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-23_Gemini_Daily.csv')
    # df = get_data_from_csv('../resources/BTC_USD_2018-07-01_2020-05-23_Gemini_Daily.csv')
    # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-27_Gemini_Hourly.csv')
    # df = get_data_from_csv('../resources/BTC_USD_2018-05-27_2020-05-27_Gemini_Hourly.csv')
    # df = get_data_from_csv('../resources/BTC_USD_2020-01-01_2020-05-27_Gemini_Hourly.csv')
    df = get_data_from_csv('../resources/gemini_BTCUSD_1hr.csv')
    # df = get_data_from_csv('../resources/gemini_BTCUSD_2019_1min.csv')

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    start = time.time()

    """
    TODO:
        - minimum holding period
        - Longest holding period
        - Optimise graph drawing with update
        - Rolling price graph window
        - Add multiple trades and logging to file
    """

    # AboveUnderMAStd(df, 'BTC', 10000, log=True, ui=True, std=2, lookback=20)
    # RSI(df, 'BTC', 10000, log=True, ui=True)
    # MACD(df, 'BTC', 10000, log=True, ui=True)
    # MACDZero(df, 'BTC', 10000, log=True, ui=True)
    # RSIandMACD(df, 'BTC', 10000, log=True, ui=True)
    # RSIdelay(df, 'BTC', 2000, log=True, ui=True)
    MA50MA10(df, 'BTC', 2000, log=True, ui=True)

    exec_time = time.time() - start
    print('')
    print(f'Backtesting ran for {exec_time} seconds')

if __name__ == '__main__':
    main()
