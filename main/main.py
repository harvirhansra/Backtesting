import time
import pandas as pd

from market.marketdata import get_data_from_csv
from trade.strategery import AboveUnderMAStd, MACD, MACDZero

def main():
    # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-23_Gemini_Daily.csv')
    # df = get_data_from_csv('../resources/BTC_USD_2018-07-01_2020-05-23_Gemini_Daily.csv')
    df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-27_Gemini_Hourly.csv')
    
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    start = time.time()

    """
    TODO:
        - Optimise graph drawing with update
        - Rolling price graph window
        - Create drawdown graph
        - Add markers on equity graph
        - Add stop backtesting button (that kills the QThread)
        - Add multiple trades and logging
        - Win/loss percentages
    """

    # AboveUnderMAStd(df, 'BTC', 10000, log=True, ui=False, std=2, lookback=20)
    strat = MACD(df, 'BTC', 10000, True, False)
    strat.run()

    exec_time = time.time() - start
    print(f'Backtesting ran for {exec_time} seconds')

if __name__ == '__main__':
    main()
