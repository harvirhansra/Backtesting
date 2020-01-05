from market.marketdata import MktData
from graph.graphdrawer import draw_terminal, draw_to_image, draw_candlestick
from analytics.analytics import compute_RSI, compute_MA, compute_EMA
from trade.simple_strats import *


def main():
    md = MktData()
    df = md.get_data_from_csv(
        '../../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    df2 = md.get_data_from_csv(
        '../../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')

    df3 = md.get_data_from_csv(
        '../../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    # df = compute_MA(df, n=14)
    # draw_to_image(df.Date.tolist(), [df.Close.tolist(), df.MA.tolist()], 'price+MA.png')

    # above_under_ma_std(df, stds=2)
    # import time
    # time.sleep(5)
    # moving_past_ma(df3)
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    above_under_ma_std(df, stds=2)
    df = compute_MA(df)
    draw_to_image(df.Date.tolist(), [df.Close.tolist(), df.MA.tolist(),
                                     (df.MA+(2*df.MA_std)).tolist(), (df.MA-(2*df.MA_std)).tolist()], 'price+MA+std.png')


main()
