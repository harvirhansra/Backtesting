import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import pandas as pd
import termplotlib as tpl

from mpl_finance import candlestick_ohlc

def draw_terminal(x, y):
    x = mpl_dates.date2num(x)
    fig = tpl.figure()
    fig.plot(x, y, width=200, height=60)
    fig.show()

    
def draw_to_image(x, y, path):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    fig.savefig(path)


def draw_candlestick(df, path=None):
    fig, ax = plt.subplots()
    ohlc = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
    candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
    fig.savefig(path)
