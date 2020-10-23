import ast
import sys
import numpy as np
import pandas as pd
import pandas_ta as ta
import tensorflow as tf
import matplotlib.pyplot as plt

from itertools import islice
from PyQt5.QtWidgets import QApplication
from ui.graphgui import BacktestingGUI
from trade.strategery import Strategery


class StrategeryDL(Strategery):
    def __init__(self, market_df, currency, initial_balance, log, ui, model_path):
        Strategery.__init__(self, market_df, currency, initial_balance, log)

        self.input_df = self.df.copy()
        self.model = tf.keras.models.load_model(model_path)


class HourlyDL(StrategeryDL):
    def __init__(self, market_df, currency, initial_balance, log, ui, model_path):
        StrategeryDL.__init__(self, market_df, currency, initial_balance, log, ui, model_path)

        self.ui = ui
        self.start_day = 20+48

        norms = open('/home/harvir/Code/Backtesting/main/trade/deeplearning/hourly/norms.txt',
                     'r').readline().replace('\n', '')
        self.norms = ast.literal_eval(norms)

        if self.ui:
            qapp = QApplication(sys.argv)
            self.gui = BacktestingGUI('DL')
            self.gui.run_func = self.run
            self.gui.show()
            qapp.exec_()

    def enrich_market_df(self):
        def normalize(df, column, mean, std):
            vals = df[col].values
            df.loc[:, column+'_normal'] = pd.Series((vals - mean) / std,
                                                    index=df.index, dtype=np.float64)

        self.input_df.loc[:, 'ema12'] = self.input_df.ta.ema(12)
        self.input_df.loc[:, 'ema24'] = self.input_df.ta.ema(24)
        self.input_df.loc[:, 'ema48'] = self.input_df.ta.ema(48)
        self.input_df.loc[:, 'vwma'] = self.input_df.ta.vwma()
        self.input_df.loc[:, 'log'] = np.log(self.input_df.close)

        self.input_df.drop(['Currency', 'high', 'low', 'volume', 'pct_change',
                            'drawdown_pct', 'equity'], axis=1, inplace=True)
        self.input_df = self.input_df[48:]

        cols = [x for x in self.input_df.columns]

        for col in cols:
            std = self.norms[col+'_std']
            mean = self.norms[col+'_mean']
            normalize(self.input_df, col, mean, std)

        self.input_df.drop([x for x in self.input_df.columns.tolist()
                            if 'normal' not in x], axis=1, inplace=True)

    def run(self):
        self.enrich_market_df()

        for i, day in islice(self.df.iterrows(), self.start_day, None, 1):

            window_df = self.input_df.loc[i-pd.Timedelta(hours=19):i]
            window_df.drop([c for c in window_df.columns.tolist() if 'normal' not in c], axis=1, inplace=True)

            input = tf.stack([row.values for _, row in window_df.iterrows()])
            input = tf.expand_dims(input, axis=0)

            prediction = (self.model.predict(input)[0][0] * self.norms['close_std']) + self.norms['close_mean']

            if not self.market_entered:
                if prediction > day.Close:
                    self.buy(i, day, max=True)
                    self.market_entered = True
            else:
                if prediction < day.Close and self.trader.btc > 0:
                    self.sell(i, day, max=True)
                elif prediction > day.Close and self.trader.balance > 0:
                    self.buy(i, day, max=True)

            self.df.at[i, 'equity'] = self.trader.balance + (self.trader.btc * day.Close)
            self.peak_equity = self.df.loc[i].equity if self.df.loc[i].equity > self.peak_equity else self.peak_equity
            self.df.at[i, 'drawdown_pct'] = -((self.peak_equity - self.df.loc[i].equity)/self.df.loc[i].equity)*100
            # self.df.at[i+pd.Timedelta(hours=4), 'prediction'] = prediction
            self.df.at[i+pd.Timedelta(hours=1), 'prediction'] = prediction

        # diffs = (self.df.Close - self.df.prediction)
        # diffs.loc[diffs.notnull()].plot.kde()
        # plt.show()

        if self.trader.btc > 0:
            self.sell(i, day, max=True)

        if self.ui:
            self.gui.plot_price_graph(self.df.index[:len(self.df.Close[:i])], self.df.Close[:i], self.plays)
            self.gui.plot_prediction_graph(self.df.loc[self.df.prediction.notnull()].index,
                                           self.df.loc[self.df.prediction.notnull()].prediction)
            self.gui.plot_equity_graph(self.df.index[:len(self.df.Close[:i])], self.df.loc[:i].equity)
            self.gui.plot_drawdown_graph(self.df.index[:len(self.df.Close[:i])], self.df[:i].drawdown_pct.values)
            self.gui.plot_distribution_graph(self.df.loc[self.df['pct_change'] != 0]['pct_change'].values)

        self.report()
