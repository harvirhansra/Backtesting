import numpy as np

from collections import namedtuple

from termcolor import colored
from trade.trader import Trader, TradeTuple
from trade.pnl import win_or_loss
from ui.graphdrawer import draw_terminal
from analytics.analytics import compute_RSI, compute_MA, compute_MACD, compute_sharpe_ratio

result = namedtuple('result', ['date', 'price', 'metric1', 'metric2', 'metric3', 'metric4', 'actiondate', 'actionprice', 'action'])


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


def above_under_ma_std(df, std=2, lookback=14, log=True, draw=False, calib=False, prev_trade=None):
    df = compute_MA(df, n=lookback) if not calib else df

    trader = Trader(10000.0, df.iloc[0].Currency)

    prev_trade = TradeTuple(None, None, df.iloc[0].Close, None, None, None) if prev_trade is None else prev_trade  # dummy trade

    if calib:
        if prev_trade.action == 'buy':
            trader.balance = 0
            trader.btc = prev_trade.quantity
        else:
            trader.balance = prev_trade.quantity * prev_trade.price
            trader.btc = 0
    
    start_btc = trader.btc
    start_balance = trader.balance
    df['pct_change'] = np.zeros(len(df))

    start_day = (2*lookback - 2) if not calib else 0  # if df is coming from calibration then all trades will have MA and MA_std so we can start from 0

    plays = []
    market_entered = True if calib else False

    for i, day in df.iterrows():
        prev_day = df.iloc[i-1]

        if draw:
            draw_terminal(df.Date[0:i].values, df.Close[0:i].values)

        if i >= start_day:
            less_than_last_buy = day.Close < prev_trade.price
            greater_than_last_sell = day.Close > prev_trade.price

            went_above_ma_std = day.Close >= (day.MA + (std*day.MA_std)) \
                and prev_day.Close < (day.MA+(std*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA - (std*day.MA_std)) \
                and prev_day.Close > (day.MA-(std*day.MA_std))

            pct_less_than_last_buy = day.Close < (prev_trade.price - (prev_trade.price*0.02))

            if went_below_ma_std and trader.balance > 0 and not market_entered:  # when to join market
                trade = trader.buy(day.Close, day.Date, max=True)
                plays.append((trade.date, trade.price, 'buy'))
                start_btc = trade.quantity
                prev_trade = trade
                market_entered = True

            if went_above_ma_std and (not less_than_last_buy) and trader.btc > 0 and market_entered:
                trade, wl = sell(trader, day, prev_trade, draw, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'sell, +'+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

            if went_below_ma_std and (not greater_than_last_sell) and trader.balance > 0 and market_entered:
                trade, wl = buy(trader, day, prev_trade, draw, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'buy'))

            # if btc is held at the end of the market data, then sell for USD to get USD PnL
            if i == len(df)-1 and trader.btc > 0 and (not calib):
                trade, wl = sell(trader, day, prev_trade, draw, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'sell, '+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

            # sell or buy final amount so PnL is calculated correctly for calibration
            if i == len(df)-1 and trader.balance > 0 and start_balance == 0 and calib:
                trade, wl = buy(trader, day, prev_trade, draw, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'buy, '+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

            if i == len(df)-1 and trader.btc > 0 and start_btc == 0 and calib:
                trade, wl = sell(trader, day, prev_trade, draw, max=True)
                if trade.quantity > 0:
                    prev_trade = trade
                    plays.append((trade.date, trade.price, 'sell, '+wl.pnlpct))
                    df.at[i, 'pct_change'] = float(wl.pnlpct.replace('%', ''))

    if draw:
        for play in plays:
            print(play)

    if calib:
        return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log), len(plays), std
    df = df.iloc[start_day:]
    sharpe = compute_sharpe_ratio(df['pct_change'].values, df.iloc[0].Date, df.iloc[-1].Date)
    print(f"Sharpe: {sharpe}")
    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)
    return result(df.Date.values, df.Close.values, df.MA.values, df.MA.values + (df.MA_std.values*std),
                  df.MA.values - (df.MA_std*std), df.MA_std, [play[0] for play in plays],
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


def macd_crossing_signal_line(df, log=True, draw=False):
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
