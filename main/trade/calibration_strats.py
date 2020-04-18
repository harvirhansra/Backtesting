import time
import numpy as np

from collections import namedtuple

from trade.trader import Trader
from trade.pnl import win_or_loss
from ui.graphdrawer import draw_terminal
from analytics.analytics import compute_MA
from trade.simple_strats import _report_final_pnl, buy, sell
from calibration.calibration import calibrate_std

result = namedtuple('result', ['date', 'price', 'metric1', 'metric2', 'metric3', 'actiondate', 'actionprice', 'action'])

def above_under_ma_std_calib(df, lookback=14, log=True, draw=False, threaded=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    start_btc = 0
    day_entered = 10000
    start_day = (2*lookback - 2)

    plays = []
    stds_used = np.zeros(len(df))

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]

        if i >= start_day:

            if i > 101:
                std = calibrate_std(df.iloc[i-101:i-1], threaded, i)
            else:
                std = calibrate_std(df.iloc[0:i-1], threaded, i)

            stds_used[i] = std

            if draw:
                draw_terminal(df.Date[0:i].values, df.Close[0:i].values)

            less_than_last_buy = day.Close < prev_trade.Close
            greater_than_last_sell = day.Close > prev_trade.Close

            went_above_ma_std = day.Close >= (day.MA + (std*day.MA_std))\
                and prev_day.Close < (day.MA+(std*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA-(std*day.MA_std))\
                and prev_day.Close > (day.MA-(std*day.MA_std))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append((trade.date, trade.buy_price, 'buy'))
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i

            if went_above_ma_std and not less_than_last_buy and trader.btc > 0 and i > day_entered:
                trade = sell(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.sell_price, 'sell'))

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0 and i > day_entered:
                trade = buy(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.buy_price, 'buy'))

            if i == len(df)-1 and trader.btc > 0:
                trade = sell(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.sell_price, 'sell'))

        if False:
            for play in plays:
                print(play)

    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)
    return result(df.Date.values, df.Close.values, df.MA.values, df.MA.values + (df.MA_std.values*stds_used),
                    df.MA.values - (df.MA_std*stds_used), [play[0] for play in plays], 
                    [play[1] for play in plays], [play[2] for play in plays])
