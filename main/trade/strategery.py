import sys
import numpy as np
import pandas as pd

from itertools import islice
from PyQt5.QtWidgets import QApplication

from trade.trader import Trader
from ui.graphgui import BacktestingGUI
from trade.pnl import win_or_loss, report_final_pnl
from analytics.analytics import compute_sharpe_ratio, compute_MA, compute_MACD, compute_RSI


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
        self.peak_equity = self.start_balance
        self.market_entered = False

    def buy(self, date, day, quantity=0, max=False):
        trade = self.trader.buy(day.Close, date, quantity, max=max)
        if trade.quantity > 0:
            self.plays.append((trade.date, trade.price, 'buy', None))
            self.prev_trade = trade
            if len(self.plays) == 1:
                self.start_btc = trade.quantity
                self.market_entered = True

    def sell(self, date, day, quantity=0, max=False):
        trade = self.trader.sell(day.Close, date, quantity, max=max)
        wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, -1)
        if trade.quantity > 0:
            self.prev_trade = trade
            self.plays.append((trade.date, trade.price, 'sell, '+str(wl.pnlpct)+'%', wl.winloss))
            self.df.at[date, 'pct_change'] = wl.pnlpct
            if self.log:
                print(', '.join([str(date), wl.winloss, '$'+wl.pnl, str(wl.pnlpct)+'%']))

    def report(self):
        report_final_pnl(self.start_balance, self.start_btc, self.trader.balance,
                         self.trader.btc, self.currency, self.log)
        longs = len([play for play in self.plays if play[3] == 'win' or play[3] == 'loss'])
        wins = len([play for play in self.plays if len(play) == 4 and play[-1] == 'win'])
        losses = len([play for play in self.plays if len(play) == 4 and play[-1] == 'loss'])
        wins_pct = round((wins/longs)*100, 2)
        losses_pct = round((losses/longs)*100, 2)
        sharpe = compute_sharpe_ratio(self.df['pct_change'].values, self.df.index[0], self.df.index[-1], hourly=True)
        if self.log:
            print(f'Long plays: {longs}')
            print(f'Wins: {wins} - {wins_pct}%')
            print(f'Loses: {losses} - {losses_pct}%')
            print('')
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
            self.gui = BacktestingGUI('MA')
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

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            if went_below_ma_std and self.trader.balance > 0 and not self.market_entered:  # when to join market
                self.buy(i, day, max=True)

            # if went_above_ma_std and (not less_than_last_buy) and self.trader.btc > 0 and self.market_entered:
            if went_above_ma_std and self.trader.btc > 0 and self.market_entered:
                self.sell(i, day, max=True)

            # if went_below_ma_std and (not greater_than_last_sell) and self.trader.balance > 0 and self.market_entered:
            if went_below_ma_std and self.trader.balance > 0 and self.market_entered:
                self.buy(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MA[:i].values,
                                      (self.df.MA[:i].values + self.std*self.df.MA_std[:i].values),
                                      (self.df.MA[:i].values - self.std*self.df.MA_std[:i].values))
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

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
            self.gui = BacktestingGUI('MACD')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_MACD(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                # missing timestamp
                self.prev_day = self.prev_day

            macd_goes_below_sl = day.MACD < day.SL and self.prev_day.MACD >= day.SL
            macd_goes_above_sl = day.MACD > day.SL and self.prev_day.MACD <= day.SL

            if macd_goes_above_sl:
                self.buy(i, day, max=True)

            if macd_goes_below_sl and self.market_entered:
                self.sell(i, day, max=True)

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MACD[:i], self.df.SL[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()


class MACDZero(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('MACD')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_MACD(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]

            macd_goes_below_sl = day.MACD < 0 and self.prev_day.MACD >= 0
            macd_goes_above_sl = day.MACD > 0 and self.prev_day.MACD <= 0

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            if macd_goes_above_sl and not self.market_entered:
                self.buy(i, day, max=True)

            if macd_goes_above_sl and self.market_entered:
                self.buy(i, day, max=True)

            if macd_goes_below_sl and self.market_entered:
                self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MACD[:i], self.df.SL[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()


class RSI(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_RSI(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(days=1)]
            except KeyError:
                pass

            above_70_rsi = day.RSI > 70 and self.prev_day.RSI <= 70
            below_30_rsi = day.RSI < 30 and self.prev_day.RSI >= 30

            # above_50_rsi = day.RSI > 50 and self.prev_day.RSI <= 50
            # below_50_rsi = day.RSI < 50 and self.prev_day.RSI >= 50

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            # if self.df.at[i, 'drawdown_pct'] < -5 and self.market_entered:
            #     self.sell(i, day, max=True)

            if below_30_rsi and not self.market_entered:
                self.buy(i, day, max=True)

            elif above_70_rsi and self.market_entered:
                self.buy(i, day, max=True)

            elif below_30_rsi and self.market_entered:
                self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays, self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()


class RSIandMACD(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_RSI(self.df)
        self.df = compute_MACD(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]

            rsi_is_above_70 = day.RSI > 70
            rsi_is_below_30 = day.RSI < 30
            # above_70_rsi = day.RSI > 70 and self.prev_day.RSI <= 70
            # below_30_rsi = day.RSI < 30 and self.prev_day.RSI >= 30

            macd_goes_below_sl = day.MACD < day.SL and self.prev_day.MACD >= day.SL
            macd_goes_above_sl = day.MACD > day.SL and self.prev_day.MACD <= day.SL

            # above_50_rsi = day.RSI > 50 and self.prev_day.RSI <= 50
            # below_50_rsi = day.RSI < 50 and self.prev_day.RSI >= 50

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            # if self.df.at[i, 'drawdown_pct'] < -5 and self.market_entered:
            #     self.sell(i, day, max=True)

            if rsi_is_below_30 and macd_goes_above_sl and not self.market_entered:
                self.buy(i, day, max=True)

            if rsi_is_above_70 and macd_goes_below_sl and self.market_entered:
                self.buy(i, day, max=True)

            if rsi_is_below_30 and macd_goes_above_sl and self.market_entered:
                self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays)  # , self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()


class RSIdelay(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        self.delay = 0

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_RSI(self.df)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            if self.delay > 0:
                self.delay -= 1
            else:
                above_70_rsi = day.RSI > 70 and self.prev_day.RSI <= 70
                below_30_rsi = day.RSI < 30 and self.prev_day.RSI >= 30

                # above_50_rsi = day.RSI > 50 and self.prev_day.RSI <= 50
                # below_50_rsi = day.RSI < 50 and self.prev_day.RSI >= 50
                if self.df.at[i, 'drawdown_pct'] < -15 and self.market_entered and self.trader.btc > 0:
                    self.delay = 0
                    self.sell(i, day, max=True)

                elif below_30_rsi and not self.market_entered:
                    self.buy(i, day, max=True)

                elif above_70_rsi and self.market_entered:
                    self.buy(i, day, max=True)

                elif below_30_rsi and self.market_entered:
                    self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays, self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()


class MA50MA10(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 27
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('MA+RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        self.df = compute_MA(self.df, n=10, hourly=False, multiple=True)
        self.df = compute_MA(self.df, n=50, hourly=False, multiple=True)
        self.df = compute_RSI(self.df, n=14)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None):
            self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            twenty_over_fifty = day['MA10'] > day['MA50'] and self.prev_day['MA10'] <= self.prev_day['MA50']
            twenty_below_fifty = day['MA10'] < day['MA50'] and self.prev_day['MA10'] >= self.prev_day['MA50']

            rsi_is_above_70 = day['RSI'] > 70
            rsi_is_above_90 = day['RSI'] > 90

            if twenty_over_fifty and not rsi_is_above_90:
                self.buy(i, day, max=True)

            elif twenty_below_fifty and self.market_entered:
                self.sell(i, day, max=True)

            elif rsi_is_above_90 and self.market_entered:
                self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df['MA50'][:i], self.df['MA10'][:i], self.df['RSI'][:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        self.report()
