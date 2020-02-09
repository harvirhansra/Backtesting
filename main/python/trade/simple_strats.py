import time

from trade.trader import Trader
from trade.pnl import win_or_loss
from analytics.analytics import compute_RSI, compute_MA, compute_MACD
from graph.graphdrawer import draw_terminal


def sell_70_buy_30_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):

        if i == 0:
            trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
            start_btc = trader.btc
            print('')

        if i > 13:
            prev_day = df.iloc[i-1]
            above_70_rsi = day[1]['RSI'] > 70 and prev_day['RSI'] <= 70
            below_30_rsi = day[1]['RSI'] < 30 and prev_day['RSI'] >= 30
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            if above_70_rsi and greater_than_last_sell:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                prev_trade = day[1]
                print('')

            if below_30_rsi and less_than_last_buy:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                prev_trade = day[1]
                print('')

    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy)


def sell_70_buy_70_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        if i == 0:
            trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
            start_btc = trader.btc
            print('')

        if i > 13:
            if day[1]['RSI'] >= 70:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] <= 70:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                prev_trade = day[1]
                print('')

    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc)


def sell_buy_passing_50_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        if i == 0:
            trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
            start_btc = trader.btc
            print('')

        if i > 13:
            if day[1]['RSI'] <= 50 and prev_day['RSI'] > 50:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] >= 50 and prev_day['RSI'] < 50:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                prev_trade = day[1]
                print('')
    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc)


def above_under_ma_std(df, stds=2, lookback=14):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    start_ccy = 0
    day_entered = 10000

    for i, day in enumerate(df.iterrows()):
        # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

        # if i == 0:
        #     trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
        #     start_btc = trader.btc
        #     prev_trade = day[1]
        #     print('')

        if i > lookback:
            prev_day = df.iloc[i-1]
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            went_above_ma_std = day[1]['Close'] >= day[1]['MA'] + \
                (stds*day[1]['MA_std']) and prev_day['Close'] < (day[1]['MA']+(stds*day[1]['MA_std']))
            went_below_ma_std = day[1]['Close'] <= (
                day[1]['MA']-(stds*day[1]['MA_std'])) and prev_day['Close'] > (day[1]['MA']-(stds*day[1]['MA_std']))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                start_ccy = trade[2]
                day_entered = i
                print('')

            if went_above_ma_std and not less_than_last_buy and trader.btc > 0 and i > day_entered:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    prev_trade = day[1]
                    print('')

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0 and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    prev_trade = day[1]
                    print('')

    _report_final_pnl(start_balance, start_ccy, trader.balance, trader.btc, trader.ccy)


def moving_past_ma(df):
    df = compute_MA(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

        if i == 0:
            trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
            start_btc = trader.btc
            print('')

        if i > 13:
            if day[1]['Close'] > day[1]['MA'] and prev_day['Close'] < day[1]['MA']:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    prev_trade = day[1]
                    print('')

            if day[1]['Close'] < day[1]['MA'] and prev_day['Close'] > day[1]['MA']:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    prev_trade = day[1]
                    print('')

    _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc)


def macd_crossing_singal_line(df, std=0):
    df = compute_MACD(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    start_ccy = 0
    day_entered = 10000

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        # if i == 0:
        #     trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
        #     start_ccy = trader.btc

        if i > 13:
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']
            macd_goes_below_sl = day[1]['MACD'] < day[1]['SL'] and prev_day['MACD'] >= day[1]['SL']
            macd_goes_above_sl = day[1]['MACD'] > day[1]['SL'] and prev_day['MACD'] <= day[1]['SL']

            if macd_goes_above_sl and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                start_ccy = trader.btc
                prev_trade = day[1]
                day_entered = i
                print('')

            if macd_goes_below_sl and greater_than_last_sell and i > day_entered:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    prev_trade = day[1]
                    print('')

            if macd_goes_above_sl and less_than_last_buy and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    prev_trade = day[1]
                    print('')

    _report_final_pnl(start_balance, start_ccy, trader.balance, trader.btc, trader.ccy)


def _report_final_pnl(start_balance, start_btc, balance, btc, ccy):
    final_is_usd = btc == 0
    final = balance if final_is_usd else btc
    start = start_balance if final_is_usd else start_btc
    final_ccy = '$' if final_is_usd else ccy
    print('Starting balance: {}{}'.format(final_ccy, start))
    print('Final balance: {}{}'.format(final_ccy, final))
    print('PnL: '+str(int((final/start)*100 - 100))+'%')
    print('')
