import time
import numpy as np

from collections import namedtuple

from termcolor import colored
from trade.trader import Trader
from trade.pnl import win_or_loss
from ui.graphdrawer import draw_terminal
from analytics.analytics import compute_RSI, compute_MA, compute_MACD

result = namedtuple('result', ['date', 'price', 'metric1', 'metric2', 'metric3', 'actiondate', 'actionprice', 'action'])


def sell_70_buy_30_RSI(df, n=14, log=True, draw=False):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    day_entered = 10000

    plays = []

    for i, day in df.iterrows():

        if i >= n:
            prev_day = df.iloc[i-1]
            above_70_rsi = day.RSI > 70 and prev_day.RSI <= 70
            below_30_rsi = day.RSI < 30 and prev_day.RSI >= 30
            less_than_last_buy = day.Close < prev_trade.Close
            greater_than_last_sell = day.Close > prev_trade.Close

            if below_30_rsi and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append(trade.string)
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i                

            if above_70_rsi and greater_than_last_sell and trader.btc > 0 and i > day_entered:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if below_30_rsi and less_than_last_buy and trader.balance > 0 and i > day_entered:
                trade = buy(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

    if tm:
        for play in plays:
            print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, tm)


def sell_70_buy_70_RSI(df, n=14, log=True, draw=False):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    day_entered = 10000

    plays = []

    for i, day in df.iterrows():

        if i >= n:
            prev_day = df.iloc[i-1]
            above_70_rsi = day.RSI >= 70 and prev_day.RSI < 70
            below_70_rsi = day.RSI < 70 and prev_day.RSI >= 70

            if below_70_rsi and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append(trade.string)
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i
                
            if above_70_rsi and trader.btc > 0 and i > day_entered:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if below_70_rsi and trader.balance > 0 and i > day_entered:
                trade = buy(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

    if tm:
        for play in plays:
            print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, tm)


def sell_buy_passing_50_RSI(df, n=14, log=True, draw=False):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance

    plays = []

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]
        if tm:
            draw_terminal(df.Date[0:i+1].values, df.Close[0:i+1].values)

        if i == 0:
            trade = trader.buy(day.Close, day.Date, max=True)
            plays.append(trade.string)
            start_btc = trade.quantity
            prev_trade = day
            day_entered = i
            
        if i > 13:
            if day.RSI <= 50 and prev_day.RSI > 50:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if day.RSI >= 50 and prev_day.RSI < 50:
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

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, tm)


def above_under_ma_std(df, stds=2, lookback=14, log=True, draw=False, calib=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    day_entered = np.inf
    start_btc = 0
    start_day = (2*lookback - 2) if not calib else 0  # if df is coming from calibration then all trades will have MA and MA_std so we can start from 0

    plays = []

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]

        if draw:
            draw_terminal(df.Date[0:i+1].values, df.Close[0:i+1].values)

        if i >= start_day:
            less_than_last_buy = day.Close < prev_trade.Close
            greater_than_last_sell = day.Close > prev_trade.Close

            went_above_ma_std = day.Close >= (day.MA + (stds*day.MA_std)) \
                and prev_day.Close < (day.MA+(stds*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA - (stds*day.MA_std)) \
                and prev_day.Close > (day.MA-(stds*day.MA_std))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append((trade.date, trade.buy_price, 'buy'))
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i

            if went_above_ma_std and (not less_than_last_buy) and trader.btc > 0 and i > day_entered:
                trade = sell(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.sell_price, 'sell'))

            if went_below_ma_std and (not greater_than_last_sell) and trader.balance > 0 and i > day_entered:
                trade = buy(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.buy_price, 'buy'))
                    

            if i == len(df)-1 and trader.btc > 0 and (not calib):
                trade = sell(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.sell_price, 'sell'))

    if False:
        for play in plays:
            print(play)
            
    if calib:
        return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)

    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)
    return result(df.Date.values, df.Close.values, df.MA.values, df.MA.values + (df.MA_std.values*stds),
                    df.MA.values - (df.MA_std*stds), [play[0] for play in plays], 
                    [play[1] for play in plays], [play[2] for play in plays])
                    

def moving_past_ma(df, lookback, log=True, draw=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    day_entered = 10000
    start_btc = 0

    plays = []

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]
        if draw:
            draw_terminal(df.Date[0:i+1].tolist(), df.Close[0:i+1].tolist())

        if i == 0:
            trade = trader.buy(day.Close, day.Date, max=True)
            plays.append(trade.string)
            start_btc = trade.quantity
            prev_trade = day
            day_entered = i

        if i > 13:
            if day.Close > day.MA and prev_day.Close < day.MA:
                trade = sell(trader, day, prev_trade, tm)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append(trade.string)

            if day.Close < day.MA and prev_day.Close > day.MA:
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

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)


def macd_crossing_singal_line(df, log=True, draw=False):
    df = compute_MACD(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade.Currency)
    start_balance = trader.balance
    day_entered = 10000
    start_btc = 0

    plays = []

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]
        if draw:
            draw_terminal(df.Date[0:i+1].values, df.Close[0:i+1].values)

        if i > 26:
            less_than_last_buy = day.Close < prev_trade.Close
            greater_than_last_sell = day.Close > prev_trade.Close
            macd_goes_below_sl = day.MACD < day.SL and prev_day.MACD >= day.SL
            macd_goes_above_sl = day.MACD > day.SL and prev_day.MACD <= day.SL

            if macd_goes_above_sl and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append((trade.date, trade.buy_price, 'buy'))
                start_btc = trade.quantity
                prev_trade = day
                day_entered = i

            if macd_goes_below_sl and greater_than_last_sell and i > day_entered:
                trade = sell(trader, day, prev_trade, log)
                if trade.quantity > 0:
                    prev_trade = day
                    plays.append((trade.date, trade.sell_price, 'sell'))

            if macd_goes_above_sl and less_than_last_buy and i > day_entered:
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
    
    return result(df.Date.values, df.Close.values, [play[0] for play in plays],
                    [play[1] for play in plays], [play[2] for play in plays])


def _report_final_pnl(start_balance, start_btc, balance, btc, ccy, log=True):
    final_is_usd = btc == 0
    final = balance if final_is_usd else btc
    start = start_balance if final_is_usd else start_btc
    final_ccy = '$' if final_is_usd else ccy
    pnl = int((final/start)*100 - 100)
    if log:
        print('')
        print('Starting balance: {}{}'.format(final_ccy, start))
        print('Final balance: {}{}'.format(final_ccy, final))
        print('PnL: '+str(pnl)+'%')
        print('')
    return pnl

def buy(trader, day, prev_trade, tm):
    trade = trader.buy(day.Close, day.Date, max=True)
    if trade.quantity > 0:
        if tm:
            wl = win_or_loss(prev_trade.Close, trade.buy_price, trade.quantity, 1)
            # print(colored(', '.join([wl.winloss, wl.pnl, wl.pnlpct]), wl.colour))
            print('')
    return trade

def sell(trader, day, prev_trade, tm):
    trade = trader.sell(day.Close, day.Date, max=True)
    if trade.quantity > 0:
        if tm:
            wl = win_or_loss(prev_trade.Close, trade.sell_price, trade.quantity, -1)
            # print(colored(', '.join([wl.winloss, wl.pnl, wl.pnlpct]), wl.colour))
            print('')
    return trade
