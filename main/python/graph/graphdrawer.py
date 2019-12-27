import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import pandas as pd
import termplotlib as tpl

def draw_terminal(x, y):
    x = mpl_dates.date2num(x)
    fig = tpl.figure()
    fig.plot(x, y, width=200, height=60)
    fig.show()

    
def draw_to_image(x, y, path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    fig.savefig(path)


def draw_candlestick(x, y, path=None):
    pass
