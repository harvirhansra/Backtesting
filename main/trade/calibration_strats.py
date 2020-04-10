import time

from trade.trader import Trader
from trade.pnl import win_or_loss
from ui.graphdrawer import draw_terminal
from analytics.analytics import compute_MA
from trade.simple_strats import _report_final_pnl, buy, sell
from calibration.calibration import calibrate_std


def above_under_ma_std_calib(df, lookback=14, tm=False, threaded=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    start_btc = 0
    day_entered = 10000

    plays = []

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]

        if i > lookback:
            if i > 116:
                std = calibrate_std(df.iloc[i-100:i], threaded)
            else:
                std = calibrate_std(df.iloc[0:i], threaded)

            if tm:
                draw_terminal(df.Date[0:i+1].values, df.Close[0:i+1].values)

            less_than_last_buy = day.Close < prev_trade.Close
            greater_than_last_sell = day.Close > prev_trade.Close

            went_above_ma_std = day.Close >= (day.MA + (std*day.MA_std))\
                and prev_day.Close < (day.MA+(std*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA-(std*day.MA_std))\
                and prev_day.Close > (day.MA-(std*day.MA_std))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append(trade.string)
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i

            if went_above_ma_std and not less_than_last_buy and trader.btc > 0 and i > day_entered:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0 and i > day_entered:
                trade = buy(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if i == len(df)-1 and trader.btc > 0:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

        if tm:
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy)
