from market.marketdata import MktData
from graph.graphdrawer import draw_terminal, draw_to_image, draw_candlestick
from analytics.analytics import compute_RSI
from trade.simple_strats import *


def main():
    md = MktData()
    df = md.get_data_from_csv(
        '../../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    df2 = md.get_data_from_csv(
        '../../resources/BTC_USD_2019-07-12_2019-12-30-CoinDesk.csv')

    df3 = md.get_data_from_csv(
        '../../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    # draw_to_image(df3['Date'].tolist(), df3['Close'].tolist(), 'price.png')
    sell_buy_passing_50_RSI(df)
    df3 = compute_RSI(df3)
    # draw_to_image(df3['Date'].tolist(), df3['RSI'].tolist(), 'rsi.png', 'rsi')


main()
