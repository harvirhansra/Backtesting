from trade.trader import Trader
from trade.pnl import win_or_loss
from graph.graphdrawer import draw_terminal
from analytics.analytics import compute_MA
from trade.simple_strats import _report_final_pnl
from calibration.calibration import calibrate_std


def above_under_ma_std_calib(df, lookback=14, threaded=True):
    df = compute_MA(df, n=lookback)
    prev_trade = df.iloc[0]
    trader = Trader(10000.0, prev_trade['Currency'])
    start_balance = trader.balance
    start_ccy = 0
    day_entered = 10000

    for i, day in enumerate(df.iterrows()):
        if i > lookback:

            if i > 116:
                std = calibrate_std(df.iloc[i-100:i-1], threaded)
            else:
                std = calibrate_std(df.iloc[0:i-1], threaded)

            # draw_terminal(df['Date'][0:i+1].tolist(), df['Close'][0:i+1].tolist())

            prev_day = df.iloc[i-1]
            less_than_last_buy = day[1]['Close'] < prev_trade['Close']
            greater_than_last_sell = day[1]['Close'] > prev_trade['Close']

            went_above_ma_std = day[1]['Close'] >= day[1]['MA'] + \
                (std*day[1]['MA_std']) and prev_day['Close'] < (day[1]['MA']+(std*day[1]['MA_std']))
            went_below_ma_std = day[1]['Close'] <= (
                day[1]['MA']-(std*day[1]['MA_std'])) and prev_day['Close'] > (day[1]['MA']-(std*day[1]['MA_std']))

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

        if i == len(df)-1:
            trade = trader.sell(day[1]['Close'], date=day[1]['Date'], max=True)

    return _report_final_pnl(start_balance, start_ccy, trader.balance, trader.btc, trader.ccy)
