import sys
import numpy as np
import pandas as pd

from time import sleep
from itertools import islice
from collections import namedtuple
from PyQt5.QtWidgets import QApplication

from backtesting.trade.trader import Trader
from backtesting.ui.graphgui import BacktestingGUI
from backtesting.analytics.pnl import win_or_loss, report_final_pnl, report_plays_stats
from backtesting.analytics.analytics import compute_sharpe_ratio, compute_MA, compute_MACD, compute_RSI

play_tuple = namedtuple('Play', ['date', 'price', 'type', 'pnl', 'pnlpct'])


class Strategery(object):

    def __init__(self, market_df, currency, initial_balance=10000, log=True):
        self.log = log

        self.df = market_df
        self.df.loc[:, 'pct_change'] = 0
        self.df['drawdown_pct'] = 0
        self.df['equity'] = initial_balance

        self.currency = currency
        self.trader = Trader(initial_balance, currency, fees=0.0025)

        self.start_day = 0
        self.start_date = self.df.index[self.start_day]
        self.start_btc = self.trader.btc
        self.start_balance = self.trader.balance

        self.plays = []
        self.equity = []
        self.peak_equity = self.start_balance
        self.market_entered = False

    def long(self, date, day, quantity=0, max=True):
        trade = self.trader.long(day.Close, date, quantity, max=max)
        self.plays.append(play_tuple(trade.date, trade.price, trade.type, None, None))
        self.prev_trade = trade
        if len(self.plays) == 1:
            self.start_btc = trade.quantity
            self.market_entered = True

    def close_long(self, date, day, quantity=0, max=True):
        trade = self.trader.close_long(day.Close, date, quantity=0, max=max)
        wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, trade.type)
        # self.prev_trade = trade
        self.df.at[date, 'pct_change'] = wl.pnlpct
        self.plays.append(play_tuple(trade.date, trade.price, trade.type, wl.pnl, wl.pnlpct))
        if self.log:
            print(', '.join([str(date), wl.winloss, '£'+str(wl.pnl), str(wl.pnlpct)+'%']))

    def short(self, date, day, quantity=0, max=False):
        trade = self.trader.short(day.Close, date, quantity, max=max)
        self.plays.append(play_tuple(trade.date, trade.price, trade.type, None, None))
        self.prev_trade = trade
        if len(self.plays) == 1:
            self.start_btc = trade.quantity
            self.market_entered = True

    def close_short(self, date, day, quantity=0, max=True):
        trade = self.trader.close_short(day.Close, date, quantity=0, max=max)
        wl = win_or_loss(self.prev_trade.price, trade.price, trade.quantity, trade.type)
        self.plays.append(play_tuple(trade.date, trade.price, 'close short', wl.pnl, wl.pnlpct))
        if self.log:
            print(', '.join([str(date), wl.winloss, '£'+str(wl.pnl), str(wl.pnlpct)+'%']))

    def report(self):
        buy_and_hold = round(((self.df.iloc[-1].Close - self.df.iloc[0].Close) / self.df.iloc[0].Close) * 100, 2)
        pnl = report_final_pnl(self.start_balance, self.start_btc, self.trader.balance, self.trader.btc,
                               self.currency, self.log)
        report_plays_stats(self.plays)
        max_drawdown = round(min(self.df['drawdown_pct']), 2)
        mean_return = round(self.df.loc[self.df['pct_change'] != 0]['pct_change'].mean(), 2)
        volatility = round(self.df.loc[self.df['pct_change'] != 0]['pct_change'].std(), 2)
        # sharpe = round(compute_sharpe_ratio(pnl, volatility, 0.14, len(self.df)), 2)

        if self.log:
            print('')
            # print(f'Sharpe ratio: {sharpe}')
            print(f'Max drawdown: {max_drawdown}%')
            print(f'Mean return: {mean_return}%')
            print(f'Volatility: {volatility}%')
            print(f'Buy and hold return: {buy_and_hold}%')

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
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                print(f'Using last previous date as data for {i} is missing')

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
            self.peak_equity = self.df.loc[i].equity if (self.df.loc[i].equity > self.peak_equity) else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            if went_below_ma_std and self.trader.balance > 0 and not self.market_entered:  # when to join market
                self.long(i, day, max=True)

            # if went_above_ma_std and (not less_than_last_buy) and self.trader.btc > 0 and self.market_entered:
            if went_above_ma_std and self.trader.btc > 0 and self.market_entered:
                self.close_long(i, day, max=True)

            # if went_below_ma_std and (not greater_than_last_sell) and self.trader.balance > 0 and self.market_entered:
            if went_below_ma_std and self.trader.balance > 0 and self.market_entered:
                self.long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MA[:i].values,
                                      (self.df.MA[:i].values + self.std*self.df.MA_std[:i].values),
                                      (self.df.MA[:i].values - self.std*self.df.MA_std[:i].values))
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0 and (not self.calib):
            self.close_long(i, day, max=True)

        # sell or buy final amount so PnL is calculated correctly for calibration
        if self.trader.balance > 0 and self.start_balance == 0 and self.calib:
            self.long(i, day, max=True)

        if self.trader.btc > 0 and self.start_btc == 0 and self.calib:
            self.close_long(i, day, max=True)

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
                self.long(i, day, max=True)

            if macd_goes_below_sl and self.market_entered:
                self.close_long(i, day, max=True)

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MACD[:i], self.df.SL[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.close_long(i, day, max=True)

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
                self.long(i, day, max=True)

            if macd_goes_above_sl and self.market_entered:
                self.long(i, day, max=True)

            if macd_goes_below_sl and self.market_entered:
                self.close_long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df.MACD[:i], self.df.SL[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.close_long(i, day, max=True)

        self.report()


class RSI(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 14
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
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                pass

            above_70_rsi = day.RSI > 70 and self.prev_day.RSI <= 70
            below_30_rsi = day.RSI < 30 and self.prev_day.RSI >= 30

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.df.loc[i].equity - self.peak_equity)/self.peak_equity)*100

            if below_30_rsi:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)

            elif above_70_rsi:
                if self.trader.open_long is None:
                    self.long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays, self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.close_long(i, day, max=True)

        self.report()


class RSI(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 14
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
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                pass

            above_50_rsi = day.RSI > 50 and self.prev_day.RSI <= 50
            below_50_rsi = day.RSI < 50 and self.prev_day.RSI >= 50

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.df.loc[i].equity - self.peak_equity)/self.peak_equity)*100

            if below_50_rsi:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)
                    self.short(i, day, max=True)
                elif self.trader.close_short is None:
                    self.short(i, day, max=True)

            elif above_50_rsi:
                if self.trader.open_short is not None:
                    self.close_short(i, day, max=True)
                    self.long(i, day, max=True)
                elif self.trader.open_long is None:
                    self.long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays, self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            if self.trader.open_long is not None:
                self.close_long(i, day, max=True)
            if self.trader.open_short is not None:
                self.close_short(i, day, max=True)

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
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except:
                pass

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
                self.long(i, day, max=True)

            if rsi_is_above_70 and macd_goes_below_sl and self.market_entered:
                self.long(i, day, max=True)

            if rsi_is_below_30 and macd_goes_above_sl and self.market_entered:
                self.close_long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays)  # , self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.close_long(i, day, max=True)

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
                    self.close_long(i, day, max=True)

                elif below_30_rsi and not self.market_entered:
                    self.long(i, day, max=True)

                elif above_70_rsi and self.market_entered:
                    self.long(i, day, max=True)

                elif below_30_rsi and self.market_entered:
                    self.close_long(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])],
                                      self.df.Close[:i], self.plays, self.df.RSI[:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            self.close_long(i, day, max=True)

        self.report()


class MA50MA10(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 50
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('MA+RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec()

    def enrich_market_df(self):
        self.df = compute_MA(self.df, n=10, multiple=True)
        self.df = compute_MA(self.df, n=50, multiple=True)
        self.df = compute_RSI(self.df, n=14)

    def run(self):
        self.enrich_market_df()
        for i, day in islice(self.df.iterrows(), self.start_day, None):
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                pass

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100

            ten_above_fifty = day['MA10'] > day['MA50'] and self.prev_day['MA10'] <= self.prev_day['MA50']
            ten_below_fifty = day['MA10'] < day['MA50'] and self.prev_day['MA10'] >= self.prev_day['MA50']

            rsi_is_below_30 = day['RSI'] < 30
            rsi_is_above_70 = day['RSI'] > 70
            rsi_is_above_90 = day['RSI'] > 90
            rsi_is_above_95 = day['RSI'] > 95

            if ten_above_fifty:
                # if self.trader.open_short is not None:
                #     self.close_short(i, day, max=True)
                #     self.long(i, day, max=True)
                if self.trader.open_long is None:
                    self.long(i, day, max=True)

            elif ten_below_fifty:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)
                #     self.short(i, day, max=True)
                # if self.trader.open_short is None:
                #     self.short(i, day, max=True)

            elif rsi_is_above_90:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)
                #     self.short(i, day, max=True)
                # if self.trader.open_short is None:
                #     self.short(i, day, max=True)

            elif rsi_is_below_30:
                if self.trader.open_long is None:
                    self.long(i, day, max=True)
            #     if self.trader.open_short is not None:
            #         self.close_short(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df['MA50'][:i], self.df['MA10'][:i], self.df['RSI'][:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)
            # self.gui.plot_distribution_graph(self.df['pct_change'].values)


        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            if self.trader.open_long is not None:
                self.close_long(i, day, max=True)
            if self.trader.open_short is not None:
                self.close_short(i, day, max=True)

        self.report()


class MA20MA10(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.ui = ui

        self.prev_day = None
        self.prev_trade = None
        self.start_day = 50
        self.start_date = self.df.index[self.start_day]

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('MA+RSI')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec()

    def enrich_market_df(self):
        self.df = compute_MA(self.df, n=10, multiple=True)
        self.df = compute_MA(self.df, n=20, multiple=True)
        self.df = compute_RSI(self.df, n=14)

    def run(self):
        self.enrich_market_df()
        for i, day in islice(self.df.iterrows(), self.start_day, None):
            try:
                self.prev_day = self.df.loc[i-pd.Timedelta(hours=1)]
            except KeyError:
                pass

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.peak_equity)*100

            ten_above_twenty = day['MA10'] > day['MA20'] and self.prev_day['MA10'] <= self.prev_day['MA20']
            ten_below_twenty = day['MA10'] < day['MA20'] and self.prev_day['MA10'] >= self.prev_day['MA20']

            rsi_is_below_30 = day['RSI'] < 30
            rsi_is_above_70 = day['RSI'] > 70
            rsi_is_above_90 = day['RSI'] > 90
            rsi_is_above_95 = day['RSI'] > 95

            if ten_above_twenty:
                if self.trader.open_short is not None:
                    self.close_short(i, day, max=True)
                    self.long(i, day, max=True)
                if self.trader.open_long is None:
                    self.long(i, day, max=True)

            elif ten_below_twenty:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)
                    self.short(i, day, max=True)
                elif self.trader.open_short is None:
                    self.short(i, day, max=True)

            elif rsi_is_above_90:
                if self.trader.open_long is not None:
                    self.close_long(i, day, max=True)

            elif rsi_is_below_30:
                if self.trader.open_short is not None:
                    self.close_short(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays,
                                      self.df['MA50'][:i], self.df['MA20'][:i], self.df['RSI'][:i])
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)
            # self.gui.plot_distribution_graph(self.df['pct_change'].values)


        # if btc is held at the end of the market data, then sell for USD to get USD PnL
        if self.trader.btc > 0:
            if self.trader.open_long is not None:
                self.close_long(i, day, max=True)
            if self.trader.open_short is not None:
                self.close_short(i, day, max=True)

        self.report()
