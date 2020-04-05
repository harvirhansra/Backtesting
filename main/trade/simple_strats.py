from trade.trader import Trader
from trade.pnl import win_or_loss
from analytics.analytics import compute_RSI, compute_MA, compute_MACD
from ui.graphdrawer import draw_terminal


def sell_70_buy_30_RSI(df, n=14, log=True):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    day_entered = 10000

    plays = []

    for i, day in enumerate(df.iterrows()):

        if i >= n:
            prev_day = df.iloc[i-1]
            above_70_rsi = day[1]['RSI'] > 70 and prev_day['RSI'] <= 70
            below_30_rsi = day[1]['RSI'] < 30 and prev_day['RSI'] >= 30
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            if below_30_rsi and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                start_btc = trade[2]
                plays.append(trade[3])
                day_entered = i
                print('')

            if above_70_rsi and greater_than_last_sell and trader.btc > 0 and i > day_entered:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                plays.append(trade[3])
                if log:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    print('')

            if below_30_rsi and less_than_last_buy and trader.balance > 0 and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                plays.append(trade[3])
                if log:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    print('')
        if log:
            print('')
            print('')
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)


def sell_70_buy_70_RSI(df, n=14, log=True):
    df = compute_RSI(df, n=n)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    day_entered = 10000

    plays = []

    for i, day in enumerate(df.iterrows()):

        if i >= n:
            prev_day = df.iloc[i-1]
            above_70_rsi = day[1]['RSI'] >= 70 and prev_day['RSI'] < 70
            below_70_rsi = day[1]['RSI'] < 70 and prev_day['RSI'] >= 70

            if below_70_rsi and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                start_ccy = trade[2]
                plays.append(trade[3])
                day_entered = i

            if above_70_rsi and trader.btc > 0 and i > day_entered:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                plays.append(trade[3])
                if log:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    print('')

            if below_70_rsi and trader.balance > 0 and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                plays.append(trade[3])
                if log:
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    print('')

        if log:
            print('')
            print('')
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_ccy, trader.balance, trader.btc, trader.ccy, log)


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


def above_under_ma_std(df, stds=2, lookback=14, log=False, draw=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    day_entered = 10000
    start_btc = 0

    plays = []

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        if draw:
            draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

        if i > lookback:
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            went_above_ma_std = day[1]['Close'] >= (day[1]['MA'] + (stds*day[1]['MA_std'])) \
                and prev_day['Close'] < (day[1]['MA']+(stds*day[1]['MA_std']))
            went_below_ma_std = day[1]['Close'] <= (day[1]['MA'] - (stds*day[1]['MA_std'])) \
                and prev_day['Close'] > (day[1]['MA']-(stds*day[1]['MA_std']))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], day[1]['Date'], max=True)
                plays.append(trade[3])
                start_btc = trade[2]
                prev_trade = day[1]
                day_entered = i

            if went_above_ma_std and (not less_than_last_buy) and trader.btc > 0 and i > day_entered:
                trade = trader.sell(day[1]['Close'], day[1]['Date'], max=True)
                if trade[2] > 0:
                    if log:
                        plays.append(trade[3])
                        print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                        print('')
                    prev_trade = day[1]

            if went_below_ma_std and (not greater_than_last_sell) and trader.balance > 0 and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    if log:
                        plays.append(trade[3])
                        print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                        print('')
                    prev_trade = day[1]

            # if i == len(df)-1 and trader.btc > 0:
            #     trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
            #     if log:
            #         plays.append(trade[3])
            #         print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
            #         print('')

        if log:
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)


def moving_past_ma(df, lookback, log=False, draw=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    day_entered = 10000
    start_btc = 0

    plays = []

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        if draw:
            draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

        if i == 0:
            trade = trader.buy(day[1]['Close'], day[1]['Date'], max=True)
            plays.append(trade[3])
            start_btc = trade[2]
            prev_trade = day[1]
            day_entered = i

        if i > 13:
            if day[1]['Close'] > day[1]['MA'] and prev_day['Close'] < day[1]['MA']:
                trade = trader.sell(day[1]['Close'], day[1]['Date'], max=True)
                prev_trade = day[1]
                if log:
                    plays.append(trade[3])
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    print('')

            if day[1]['Close'] < day[1]['MA'] and prev_day['Close'] > day[1]['MA']:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                prev_trade = day[1]
                if log:
                    plays.append(trade[3])
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                    print('')

            if i == len(df)-1 and trader.btc > 0:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                if log:
                    plays.append(trade[3])
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))

        if log:
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)


def macd_crossing_singal_line(df, stds=0, log=False, draw=False):
    df = compute_MACD(df)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    day_entered = 10000
    start_btc = 0

    plays = []

    for i, day in enumerate(df.iterrows()):
        prev_day = df.iloc[i-1]
        if draw:
            draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

        if i > 26:
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']
            macd_goes_below_sl = day[1]['MACD'] < day[1]['SL'] and prev_day['MACD'] >= day[1]['SL']
            macd_goes_above_sl = day[1]['MACD'] > day[1]['SL'] and prev_day['MACD'] <= day[1]['SL']

            if macd_goes_above_sl and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], day[1]['Date'], max=True)
                plays.append(trade[3])
                start_btc = trade[2]
                prev_trade = day[1]
                day_entered = i

            if macd_goes_below_sl and greater_than_last_sell and i > day_entered:
                trade = trader.sell(day[1]['Close'], day[1]['Date'], max=True)
                if trade[2] > 0:
                    if log:
                        plays.append(trade[3])
                        print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                        print('')
                    prev_trade = day[1]

            if macd_goes_above_sl and less_than_last_buy and i > day_entered:
                trade = trader.buy(day[1]['Close'], date=day[1]['Date'], max=True)
                if trade[2] > 0:
                    prev_trade = day[1]
                    if log:
                        plays.append(trade[3])
                        print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'buy'))
                        print('')
                    prev_trade = day[1]

            if i == len(df)-1 and trader.btc > 0:
                trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)
                if log:
                    plays.append(trade[3])
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    print('')

        if log:
            for play in plays:
                print(play)

    return _report_final_pnl(start_balance, start_btc, trader.balance, trader.btc, trader.ccy, log)


def _report_final_pnl(start_balance, start_btc, balance, btc, ccy, log=True):
    final_is_usd = btc == 0
    final = balance if final_is_usd else btc
    start = start_balance if final_is_usd else start_btc
    final_ccy = '$' if final_is_usd else ccy
    pnl = int((final/start)*100 - 100)
    if log:
        print('Starting balance: {}{}'.format(final_ccy, start))
        print('Final balance: {}{}'.format(final_ccy, final))
        print('PnL: '+str(pnl)+'%')
        print('')
    return pnl
