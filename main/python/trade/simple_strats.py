import time

from trade.trader import Trader
from trade.pnl import win_or_loss
from analytics.analytics import compute_RSI
from graph.graphdrawer import draw_terminal


def sell_70_buy_30_RSI(df):
    df = compute_RSI(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        if i > 13:
            if day[1]['RSI'] >= 70:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_day['Close'], trade[1], trade[2]))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] <= 30:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_day['Close'], trade[1], trade[2]))
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


def sell_70_buy_70_RSI(df):
    df = compute_RSI(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        if i > 13:
            if day[1]['RSI'] >= 70:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_day['Close'], trade[1], trade[2]))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] <= 70:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_day['Close'], trade[1], trade[2]))
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


def sell_buy_passing_50_RSI(df):
    df = compute_RSI(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0)
    start_balance = trader.balance

    for i, day in enumerate(df.iterrows()):
        # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())
        if i > 13:
            if day[1]['RSI'] <= 50 and prev_trade['RSI'] > 50:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2]))
                prev_trade = day[1]
                print('')

            if day[1]['RSI'] >= 50 and prev_trade['RSI'] < 50:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                print(win_or_loss(prev_trade['Close'], trade[1], trade[2]))
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
