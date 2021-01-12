import pandas as pd
import numpy as np

from backtesting.market.marketdata import get_data_from_csv


def compute_RSI(df, n=14):
    """ Computes Relative Strength Index (RSI) """
    deltas = np.diff(df.Close)

    ups = np.where(deltas < 0, 0, deltas)
    downs = abs(np.where(deltas > 0, 0, deltas))

    avg_gain = np.convolve(ups, np.ones(n)/n, mode='valid')
    avg_loss = np.convolve(downs, np.ones(n)/n, mode='valid')

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0+rs))
    rsi = np.append(np.zeros(14), rsi)

    df['RSI'] = rsi
    return df


def compute_MA(df, n=14, hourly=False, multiple=False):
    """ Computes Simple Moving Average """
    pd.set_option('mode.chained_assignment', None)
    n = 24*n if hourly else n
    if multiple:
        df['MA'+str(n)] = df.Close.rolling(window=n).mean()
        df['MA'+str(n)+'_std'] = df['MA'+str(n)].rolling(window=n).std()
    else:
        df['MA'] = df.Close.rolling(window=n).mean()
        df['MA_std'] = df.MA.rolling(window=n).std()
    return df


def compute_WMA(df, n=14):
    """ Computes Weighted Moving Average """
    weights = np.arange(1, n)
    df['WMA'] = df.Close.rolling(window=n).apply(lambda prices: np.dot(prices, weights)/weights.sum())
    df['WMA_std'] = df.WMA.rolling(window=n).std()
    return df


def compute_EMA(df, n=14):
    """ Computes Exponential Moving Average """
    df['EMA'] = df.Close.ewm(span=n).mean()
    df['EMA_std'] = df.EMA.rolling(window=n).std()
    return df


def compute_MACD(df):
    """ Computes Moving Average Convergence Divergence """
    df['EMA26'] = df.Close.ewm(span=26).mean()
    df['EMA12'] = df.Close.ewm(span=12).mean()
    df['MACD'] = df.EMA12.values - df.EMA26.values
    df['SL'] = df.MACD.ewm(span=9).mean()  # signal line
    return df


def compute_SAR():
    pass


def compute_sharpe_ratio(total_return, vol, rf, df_len):
    breakpoint()
    daily_return = total_return / 365*2
    daily_vol = vol*np.sqrt(365)
    return (daily_return - rf) / daily_vol
