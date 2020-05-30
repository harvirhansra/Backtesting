import numpy as np
import pandas as pd

from itertools import islice
from termcolor import colored

from trade.trader import Trader
from trade.pnl import win_or_loss, report_final_pnl
from analytics.analytics import compute_sharpe_ratio, compute_MA


class Strategery(object):

    def __init__(self, market_df, currency, initial_balance=10000, terminal_mode=False):
        self.tm = terminal_mode  # if true, coloured printing and terminal plotting

        self.df = market_df
        self.df['pct_change'] = np.zeros(len(self.df))

        self.currency = currency
        self.trader = Trader(initial_balance, currency)

        self.start_day = 0
        self.start_date = self.df.index[self.start_day]
        self.start_btc = self.trader.btc
        self.start_balance = self.trader.balance

        self.plays = []
        self.market_entered = False

    def buy(self, date, day, quantity=0, max=False, first=False):
        trade = self.trader.buy(day.Close, date, quantity, max=max)
        if not first:
            wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, 1)
        if trade.quantity > 0:
            self.plays.append((trade.date, trade.price, 'buy'))
            self.prev_trade = trade
            if len(self.plays) == 0:
                self.start_btc = trade.quantity
                self.market_entered = True
            if self.tm:
                print(colored(', '.join([wl.winloss, wl.pnl, wl.pnlpct]), wl.colour))

    def sell(self, date, day, quantity=0, max=False):
        trade = self.trader.sell(day.Close, date, quantity, max=max)
        wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, -1)
        if trade.quantity > 0:
            self.prev_trade = trade
            self.plays.append((trade.date, trade.price, 'sell, '+str(wl.pnlpct)+'%'))
            self.df.at[date, 'pct_change'] = wl.pnlpct
            if self.tm:
                print(colored(', '.join([wl.winloss, wl.pnl, wl.pnlpct]), wl.colour))

    def report(self):
        report_final_pnl(self.start_balance, self.start_btc, self.trader.balance, self.trader.btc, self.currency)
        sharpe_df = self.df.loc[self.start_date:]
        sharpe = compute_sharpe_ratio(sharpe_df['pct_change'].values, sharpe_df.index[0], sharpe_df.index[-1])
        print(f'Sharpe ratio: {sharpe}')

    def enrich_market_df(self):
        return self.df

    def run(self):
        return


class AboveUnderMAStd(Strategery):

    def __init__(self, *args, **kwargs):
        Strategery.__init__(self, *args, **kwargs)

        self.std = 1.5
        self.lookback = 20
        self.calib = False
        self.prev_day = None
        self.prev_trade = None
        self.start_day = (2*self.lookback - 2) if not self.calib else 0
        self.start_date = self.df.index[self.start_day]
        # self.prev_trade = TradeTuple(None, None, df.iloc[0].Close, None, None, None) if prev_trade is None else prev_trade  # dummy trade
        
    def enrich_market_df(self):
        self.df = compute_MA(self.df, self.lookback)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(days=1)]

            if self.prev_trade:
                less_than_last_buy = day.Close < self.prev_trade.price
                greater_than_last_sell = day.Close > self.prev_trade.price
            else:
                less_than_last_buy = False
                greater_than_last_sell = False

            went_above_ma_std = day.Close >= (day.MA + (self.std*day.MA_std)) \
                and self.prev_day.Close < (day.MA+(self.std*day.MA_std))
            went_below_ma_std = day.Close <= (day.MA - (self.std*day.MA_std)) \
                and self.prev_day.Close > (day.MA-(self.std*day.MA_std))

            if went_below_ma_std and self.trader.balance > 0 and not self.market_entered:  # when to join market
                self.buy(i, day, max=True, first=True)

            if went_above_ma_std and (not less_than_last_buy) and self.trader.btc > 0 and self.market_entered:
                self.sell(i, day, max=True)

            if went_below_ma_std and (not greater_than_last_sell) and self.trader.balance > 0 and self.market_entered:
                self.buy(i, day, max=True)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0 and (not self.calib):
            self.sell(i, day, max=True)

        # sell or buy final amount so PnL is calculated correctly for calibration
        if self.trader.balance > 0 and self.start_balance == 0 and self.calib:
            self.buy(i, day, max=True)

        if self.trader.btc > 0 and self.start_btc == 0 and self.calib:
            self.sell(i, day, max=True)

        self.report()
