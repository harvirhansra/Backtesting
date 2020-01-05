import time

from trade.trader import Trader
from trade.pnl import win_or_loss
from analytics.analytics import compute_RSI, compute_MA
from graph.graphdrawer import draw_terminal


def sell_70_buy_30_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        if i > 13:
            if day[1]['RSI'] >= 70:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] <= 30:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                prev_trade = day[1]
                print('')

        if i == len(df)-1:
            if trader.btc > 0:
                trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    print('')
    print('Starting balance: $'+str(start_balance))
    print('Final balance: $'+str(trader.balance))
    print(str(trader.btc)+'BTC')
    print('PnL: '+str((trader.balance/start_balance)*100 - 100)+'%')


def sell_70_buy_70_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
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

        if i == len(df)-1:
            if trader.btc > 0:
                trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    print('')
    print('Starting balance: $'+str(start_balance))
    print('Final balance: $'+str(trader.balance))
    print(str(trader.btc)+'BTC')
    print('PnL: '+str((trader.balance/start_balance)*100 - 100)+'%')


def sell_buy_passing_50_RSI(df, n=14):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
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

        if i == len(df)-1:
            if trader.btc > 0:
                trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    print('')
    print('Starting balance: $'+str(start_balance))
    print('Final balance: $'+str(trader.balance))
    print(str(trader.btc)+'BTC')
    print('PnL: '+str((trader.balance/start_balance)*100 - 100)+'%')


def above_under_ma_std(df, stds=2):
    df = compute_MA(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        if i == 0:
            trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
            print('')

        if i > 13:
            prev_day = df.iloc[i-1]

            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            went_above_ma_std = day[1]['Close'] >= day[1]['MA'] + \
                (stds*day[1]['MA_std']) and prev_day['Close'] < (day[1]['MA']+(stds*day[1]['MA_std']))
            went_below_ma_std = day[1]['Close'] <= (
                day[1]['MA']-(stds*day[1]['MA_std'])) and prev_day['Close'] > (day[1]['MA']-(stds*day[1]['MA_std']))

            if went_above_ma_std and not less_than_last_buy and trader.btc > 0:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                if trade[2] > 0:
                    prev_trade = day[1]
                print('')
                # time.sleep(1.5)

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                if trade[2] > 0:
                    prev_trade = day[1]
                print('')
                # time.sleep(1.5)

        if i == len(df)-1:
            if trader.btc > 0:
                trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    print('')
    print('Starting balance: $'+str(start_balance))
    print('Final balance: $'+str(trader.balance))
    print(str(trader.btc)+'BTC')
    print('PnL: '+str((trader.balance/start_balance)*100 - 100)+'%')


def moving_past_ma(df):
    df = compute_MA(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        if i > 13:
            if day[1]['Close'] > day[1]['MA'] and prev_day['Close'] < day[1]['MA']:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                prev_trade = day[1]
                print('')

            if day[1]['Close'] < day[1]['MA'] and prev_day['Close'] > day[1]['MA']:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                prev_trade = day[1]
                print('')

        if i == len(df)-1:
            if trader.btc > 0:
                trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    print('')
    print('Starting balance: $'+str(start_balance))
    print('Final balance: $'+str(trader.balance))
    print(str(trader.btc)+'BTC')
    print('PnL: '+str((trader.balance/start_balance)*100 - 100)+'%')
    print('')
