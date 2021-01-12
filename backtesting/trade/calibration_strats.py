import time
import numpy as np

from collections import namedtuple

from trade.trader import Trader, TradeTuple
from trade.pnl import win_or_loss
from ui.graphdrawer import draw_terminal
from analytics.analytics import compute_MA, compute_sharpe_ratio
from trade.simple_strats import _report_final_pnl, buy, sell
from calibration.calibration import calibrate_std

result = namedtuple('result', ['date', 'price', 'metric1', 'metric2', 'metric3', 'metric4', 'actiondate', 'actionprice', 'action'])


def above_under_ma_std_calib(df, lookback=14, log=True, draw=False, multi=False):
    df = compute_MA(df, n=lookback)

    trader = Trader(10000.0, df.iloc[0].Currency)
    start_balance = trader.balance
    start_btc = trader.btc
    df['pct_change'] = np.zeros(len(df))
    
    entered_market = False
    start_day = (2*lookback - 2)
    prev_trade = TradeTuple(None, None, df.iloc[0].Close, None, None, None)
    prev_trade_day = df.iloc[0]
    

    plays = []
    stds_used = np.zeros(shape=len(df))

    for i, day in df.iterrows():

        if i >= start_day:
            prev_day = df.iloc[i-1]

            if not entered_market:
                std = 4  # only enter the market if significant (4 stds) drop in price from MA
                prev_std = std
            else:
                if prev_trade_day.name == i-1:
                    # for the first loop after a buy or sell, use the previous std
                    std = prev_std
                else:
                    std, pnl = calibrate_std(df.iloc[prev_trade_day.name:i-1], prev_trade, multi=multi)
                    # use previous std if calibration return 0 PnL for whole range of stds
                    # typically happens when testing small range of dates after last buy or sell
                    std = prev_std if pnl == 0 else std

            prev_std = std
            stds_used[i] = std

            if draw:
                draw_terminal(df.Date[0:i].values, df.Close[0:i].values)

            less_than_last_buy = day.Close < prev_trade.price
            greater_than_last_sell = day.Close > prev_trade.price

            pct_less_than_last_buy = day.Close < (prev_trade.price - (prev_trade.price*0.05))

            went_above_ma_std = day.Close >= (day.MA + (std*day.MA_std))\
                and prev_day.Close < (day.MA+(std*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA-(std*day.MA_std))\
                and prev_day.Close > (day.MA-(std*day.MA_std))

            if went_below_ma_std and trader.balance > 0 and (not entered_market):  # when to join market
                # trade = trader.buy(day.Close, day.Date, quantity=((trader.balance/2)/day.Close))
                trade = trader.long(day.Close, day.Date, max=True)
                plays.append((trade.date, trade.price, 'buy'))
                start_btc = trade.quantity
                prev_trade = trade
                prev_trade_day = day
                entered_market = True

            """ if pct_less_than_last_buy and prev_day.MA_std < 200 and trader.btc > 0 and entered_market:
                trade, wl = sell(trader, day, prev_trade, log, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    prev_trade_day = day
                    plays.append((trade.date, trade.price, 'sell, '+wl.pnlpct))
 """
            if went_above_ma_std and not less_than_last_buy and trader.btc > 0 and entered_market:
                # trade, wl = sell(trader, day, prev_trade, log, quantity=trader.btc/2)
                trade, wl = sell(trader, day, prev_trade, log, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    prev_trade_day = day
                    plays.append((trade.date, trade.price, 'sell, '+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0 and entered_market:
                # trade, wl = buy(trader, day, prev_trade, log, quantity=((trader.balance/2)/day.Close))
                trade, wl = buy(trader, day, prev_trade, log, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    prev_trade_day = day
                    plays.append((trade.date, trade.price, 'buy'))

            if i == len(df)-1 and trader.btc > 0:
                trade, wl = sell(trader, day, prev_trade, log, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'sell,'+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

        if False:
            for play in plays:
                print(play)
    
    stds_used = stds_used[start_day:]
    df = df.iloc[start_day:]
    sharpe = compute_sharpe_ratio(df['pct_change'].values, df.iloc[0].Date, df.iloc[-1].Date)
    print(f"Sharpe: {sharpe}")
    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)
    return result(df.Date.values, df.Close.values, df.MA.values, df.MA.values + (df.MA_std.values*stds_used),
                  df.MA.values - (df.MA_std*stds_used), df.MA_std,
                  [play[0] for play in plays], [play[1] for play in plays], [play[2] for play in plays])
