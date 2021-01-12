from mplfinance.original_flavor import candlestick_ohlc

import termplotlib as tpl
import pandas as pd
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import matplotlib


def draw(x, y):
    if type(x) is list and type(y) is list:
        plt.plot(x, y)
    if type(x) is list and type(y) is not list:
        plt.plot(x, list(y))
    if type(x) is not list and type(y) is list:
        plt.plot(list(x), y)
    else:
        plt.plot(list(x), list(y))

    plt.show(block=True)


def draw_terminal(x, y):
    x = mpl_dates.date2num(x)
    fig = tpl.figure()
    fig.plot(x, y, width=80, height=30)
    fig.show()


def draw_to_image(x, y, path, type='price'):
    fig, ax = plt.subplots()
    if type == 'rsi':
        x = x[14:]
        y = y[14:]
        ax.plot(x, [70]*len(x), 'r')
        ax.plot(x, [30]*len(x), 'g')
    else:
        if any(isinstance(yi, list) for yi in y):
            for yi in y:
                ax.plot(x, yi)
        else:
            ax.plot(x, y)
    fig.savefig(path)


def draw_candlestick(df, path=None):
    fig, ax = plt.subplots()
    ohlc = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
    candlestick_ohlc(ax, ohlc.values, width=0.6,
                     colorup='green', colordown='red', alpha=0.8)
    fig.savefig(path)


def draw_to_gui(df):
    return