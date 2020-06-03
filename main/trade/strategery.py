import sys
import numpy as np
import pandas as pd

from itertools import islice
from PyQt5.QtWidgets import QApplication

from trade.trader import Trader
from ui.graphgui import BacktestingGUI
from trade.pnl import win_or_loss, report_final_pnl
from analytics.analytics import compute_sharpe_ratio, compute_MA, compute_MACD


class Strategery(object):

    def __init__(self, market_df, currency, initial_balance=10000, log=True):
        self.log = log

        self.df = market_df
        self.df['pct_change'] = np.zeros(len(self.df))
        self.df['drawdown_pct'] = np.zeros(len(self.df))
        self.df['equity'] = np.full((len(self.df), 1), initial_balance, dtype=int)

        self.currency = currency
        self.trader = Trader(initial_balance, currency)

        self.start_day = 0
        self.start_date = self.df.index[self.start_day]
        self.start_btc = self.trader.btc
        self.start_balance = self.trader.balance

        self.plays = []
        self.equity = []
        self.market_entered = False

    def buy(self, date, day, quantity=0, max=False):
        trade = self.trader.buy(day.Close, date, quantity, max=max)
        if trade.quantity > 0:
            self.plays.append((trade.date, trade.price, 'buy'))
            self.prev_trade = trade
            if len(self.plays) == 1:
                self.start_btc = trade.quantity
                self.market_entered = True
                
    def sell(self, date, day, quantity=0, max=False):
        trade = self.trader.sell(day.Close, date, quantity, max=max)
        wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, -1)
        if trade.quantity > 0:
            self.prev_trade = trade
            self.plays.append((trade.date, trade.price, 'sell, '+str(wl.pnlpct)+'%'))
            self.df.at[date, 'pct_change'] = wl.pnlpct
            if self.log:
                print(', '.join([wl.winloss, '$'+wl.pnl, str(wl.pnlpct)+'%']))

    def report(self):
        report_final_pnl(self.start_balance, self.start_btc, self.trader.balance, self.trader.btc, self.currency, self.log)
        sharpe_df = self.df.loc[self.start_date:]
        sharpe = compute_sharpe_ratio(sharpe_df['pct_change'].values, sharpe_df.index[0], sharpe_df.index[-1])
        if self.log:
            print(f'Sharpe ratio: {sharpe}')

    def enrich_market_df(self):
        return self.df


class AboveUnderMAStd(Strategery):

    def __init__(self, market_df, currency, initial_balance, log, ui, std, lookback, calib=False):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.std = std
        self.lookback = lookback

        self.ui = ui

        self.calib = calib
        self.prev_day = None
        self.prev_trade = None
        self.start_day = (2*self.lookback - 2) if not self.calib else 0
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI()
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()
   
    def enrich_market_df(self):
        self.df = compute_MA(self.df, self.lookback)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(days=1)]

            if self.market_entered:
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
                self.buy(i, day, max=True)

            if went_above_ma_std and (not less_than_last_buy) and self.trader.btc > 0 and self.market_entered:
                self.sell(i, day, max=True)

            if went_below_ma_std and (not greater_than_last_sell) and self.trader.balance > 0 and self.market_entered:
                self.buy(i, day, max=True)

            # if went_below_ma_std and self.trader.balance > 0 and self.market_entered:
            #    self.buy(i, day, max=True)

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            # self.df.at[i, 'drawdown_pct'] = -(self.df.loc[i].equity / max(self.df.equity[self.start_date:i])) * 100

            if self.ui:
                self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                          self.df.MA[:i].values,
                                          (self.df.MA[:i].values + self.std*self.df.MA_std[:i].values),
                                          (self.df.MA[:i].values - self.std*self.df.MA_std[:i].values))
                self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
                # self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0 and (not self.calib):
            self.sell(i, day, max=True)

        # sell or buy final amount so PnL is calculated correctly for calibration
        if self.trader.balance > 0 and self.start_balance == 0 and self.calib:
            self.buy(i, day, max=True)

        if self.trader.btc > 0 and self.start_btc == 0 and self.calib:
            self.sell(i, day, max=True)

        self.report()


class MACD(Strategery):

    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI()
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()
   
    def enrich_market_df(self):
        self.df = compute_MACD(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(days=1)]

            if self.market_entered:
                less_than_last_buy = day.Close < self.prev_trade.price
                greater_than_last_sell = day.Close > self.prev_trade.price
            else:
                less_than_last_buy = False
                greater_than_last_sell = False

            macd_goes_below_sl = day.MACD < day.SL and self.prev_day.MACD >= day.SL
            macd_goes_above_sl = day.MACD > day.SL and self.prev_day.MACD <= day.SL

            if macd_goes_above_sl and less_than_last_buy:
                self.buy(i, day, max=True)

            if macd_goes_below_sl and greater_than_last_sell and self.market_entered:
                self.sell(i, day, max=True)

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            # self.df.at[i, 'drawdown_pct'] = -(self.df.loc[i].equity / max(self.df.equity[self.start_date:i])) * 100

            if self.ui:
                self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                          self.df.MACD[:i], self.df.SL[:i])
                self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
                # self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()
