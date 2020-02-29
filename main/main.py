import datetime
import pandas as pd

from market.marketdata import get_data_from_csv
from calibration.calibration import calibrate_std
from trade.calibration_strats import above_under_ma_std_calib
from analytics.analytics import compute_RSI, compute_MA, compute_EMA
from graph.graphdrawer import draw_terminal, draw_to_image, draw_candlestick
from trade.simple_strats import macd_crossing_singal_line, above_under_ma_std, sell_70_buy_30_RSI


def main():
    df1 = get_data_from_csv('../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    df2 = get_data_from_csv('../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')

    df3 = get_data_from_csv('../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    df4 = get_data_from_csv('../resources/ETH_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df5 = get_data_from_csv('../resources/BTC_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df6 = pd.read_csv('../resources/BTC_USD_2020-01-22_2020-01-27_Hourly.csv')

    df7 = pd.read_csv('../resources/Bitfinex_BTCUSD_1h.csv')

    df7 = df7.tail(72)  # last 48 hours
    df7['Date'] = df7['Date'].str.replace('-AM', ':00AM')
    df7['Date'] = df7['Date'].str.replace('-PM', ':00PM')

    df7['Low'].astype(float)
    df7['High'].astype(float)
    df7.loc[:, 'Currency'] = 'BTC'
    df7['Date'] = pd.to_datetime(df7['Date'])

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    above_under_ma_std_calib(df7, 14, False)


main()
