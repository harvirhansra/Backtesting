import pandas as pd
import numpy as np

from market.marketdata import get_data_from_csv

def compute_RSI(df, n=14):
    df.set_index
    days = len(df)
    deltas = np.append(np.zeros(1), np.diff(df['Close']))

    avg_gain = np.zeros(days)
    avg_loss = np.zeros(days)
    rs = np.zeros(days)
    rsi = np.zeros(days)

    for i in range(0, len(avg_gain)):
        if i > n-1:
            slice = deltas[i-n:i]
            avg_gain[i] = slice[slice > 0].sum() / n
            avg_loss[i] = -slice[slice < 0].sum() / n
            rs[i] = avg_gain[i] / avg_loss[i]
            rsi[i] = 100.0 - (100.0 / (1.0+rs[i]))

    df['deltas'] = deltas
    df['avg_gain'] = avg_gain
    df['avg_loss'] = avg_loss
    df['RS'] = rs
    df['RSI'] = rsi

    return df


def compute_MA(df, n=14, hourly=False):
    pd.set_option('mode.chained_assignment', None)
    n = 24*n if hourly else n
    df['MA'] = df.Close.rolling(window=n).mean()
    df['MA_std'] = df.MA.rolling(window=n).std()
    return df


def compute_WMA(df, n=14):
    weights = np.arange(1, n)
    df['WMA'] = df.Close.rolling(window=n).apply(lambda prices: np.dot(prices, weights)/weights.sum())
    df['WMA_std'] = df.WMA.rolling(window=n).std()
    return df


def compute_EMA(df, n=14):
    df['EMA'] = df.Close.ewm(span=n).mean()
    df['EMA_std'] = df.EMA.rolling(window=n).std()
    return df


def compute_MACD(df):
    df['EMA26'] = df.Close.ewm(span=26).mean()
    df['EMA12'] = df.Close.ewm(span=12).mean()
    df['MACD'] = df.EMA12.values - df.EMA26.values
    df['SL'] = df.MACD.ewm(span=9).mean()  # signal line
    return df


def compute_SAR():
    pass


def compute_sharpe_ratio(strat_return, period_start, period_end, hourly=False):
    """
    Daily timestamps. Hourly was not available.
    """
    strat_return = np.reshape(strat_return, (-1,24)).sum(axis=1) if hourly else strat_return
    index = pd.read_csv('../resources/CRIX_USD_2015-01-01_2020-05-23_Daily.csv')
    index.Date = pd.to_datetime(index.Date)
    index.Price = index.Price.astype(float)
    index = index[index.Date.between(period_start, period_end)]
    index_return = index.Price.pct_change(periods=1).fillna(0).values

    mean = np.mean(strat_return - index_return)
    variance = np.var(strat_return - index_return)

    return round(mean / np.sqrt(variance), 5)
