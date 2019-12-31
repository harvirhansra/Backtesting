from market.marketdata import MktData
from graph.graphdrawer import draw_terminal, draw_to_image, draw_candlestick
from analytics.analytics import compute_RSI
from trade.simple_strats import *


def main():
    md = MktData()
    df = md.get_data_from_csv(
        '../../resources/BTC_USD_2018-07-14_2019-07-13-CoinDesk.csv')

    # draw_candlestick(df, 'candlsticks.png')
    # draw_terminal(df['Date'].tolist(), df['Low'].tolist())

    # draw_to_image(df['Date'].tolist(), df['Low'].tolist(), 'price.png')
    # draw_terminal(df['Date'].tolist(), df['Low'].tolist())
    # df = compute_RSI(df)
    # draw_terminal(df['Date'].tolist(), df['RSI'].tolist())
    # draw_to_image(df['Date'].tolist(), df['RSI'].tolist(), 'rsi.png', 'rsi')

    # sell_70_buy_70_RSI(df)
    # buy_t0_sell_eoy(df)
    sell_buy_passing_50_RSI(df)


main()
