import time

from trade.trader import Trader
from trade.pnl import win_or_loss
from graph.graphdrawer import draw_terminal
from analytics.analytics import compute_MA
from trade.simple_strats import _report_final_pnl
from calibration.calibration import calibrate_std


def above_under_ma_std_calib(df, lookback=14, log=True, draw=False, threaded=False):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    start_ccy = 0
    day_entered = 10000

    plays = []

    for i, day in enumerate(df.iterrows()):
        if i > lookback:

            if i > 116:
                std = calibrate_std(df.iloc[i-100:i-1], threaded)
            else:
                std = calibrate_std(df.iloc[0:i-1], threaded)

            if draw:
                draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

            prev_day = df.iloc[i-1]
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            went_above_ma_std = day[1]['Close'] >= (day[1]['MA'] + (std*day[1]['MA_std']))\
                and prev_day['Close'] < (day[1]['MA']+(std*day[1]['MA_std']))
            went_below_ma_std = day[1]['Close'] <= (day[1]['MA']-(std*day[1]['MA_std']))\
                and prev_day['Close'] > (day[1]['MA']-(std*day[1]['MA_std']))

            if went_below_ma_std and trader.balance > 0 and i < day_entered:  # when to join market
                trade = trader.buy(day[1]['Close'], day[1]['Date'], max=True)
                plays.append(trade[3])
                start_btc = trade[2]
                prev_trade = day[1]
                day_entered = i

            if went_above_ma_std and not less_than_last_buy and trader.btc > 0 and i > day_entered:
                trade = trader.sell(day[1]['Close'], day[1]['Date'], max=True)
                prev_trade = day[1]
                if log:
                    plays.append(trade[3])
                    print(win_or_loss(prev_trade['Close'], trade[1], trade[2], 'sell'))
                    print('')

            if went_below_ma_std and not greater_than_last_sell and trader.balance > 0 and i > day_entered:
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

    return _report_final_pnl(start_balance, start_ccy, trader.balance, trader.btc, trader.ccy)
