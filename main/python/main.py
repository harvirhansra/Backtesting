import time
import pandas as pd

from market.marketdata import get_data_from_csv
from graph.graphdrawer import draw_terminal, draw_to_image, draw_candlestick
from analytics.analytics import compute_RSI, compute_MA, compute_EMA
from trade.simple_strats import macd_crossing_singal_line, above_under_ma_std, sell_70_buy_30_RSI


def main():
    df1 = get_data_from_csv('../../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    df2 = get_data_from_csv('../../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')

    df3 = get_data_from_csv('../../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    df4 = get_data_from_csv('../../resources/ETH_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df5 = get_data_from_csv('../../resources/BTC_USD_2018-04-05_2020-01-25-CoinDesk.csv')

    df6 = pd.read_csv('../../resources/BTC_USD_2020-01-22_2020-01-27_Hourly.csv')

    df1['Low'].astype(float)
    df1['High'].astype(float)
    df1.loc[:, 'Currency'] = 'BTC'
    df1['Date'] = pd.to_datetime(df5['Date'])

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    # for i, market in enumerate([df1, df2, df3, df4, df5]):
    #     print('Testing market number {}'.format(i+1))
    #     print('')
    #     macd_crossing_singal_line(market)
    #     time.sleep(3)
    #     above_under_ma_std(market)
    #     time.sleep(3)
    #     print('')

    # macd_crossing_singal_line(df5)

    # std = 2
    # above_under_ma_std(df5, stds=std)
    # # draw_to_image(df5.Timestamp.tolist(), [df5.Close.tolist(), df5.MA.tolist(),
    #                                        df5.MA+(std*df5.MA_std).tolist(), df5.MA-(std*df5.MA_std).tolist()], './price')

    from calibration.calibration import calibrate_std
    calibrate_std(df1)


main()
