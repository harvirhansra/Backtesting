import pandas as pd
import numpy as np


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


def compute_MA(df, n=14):
    df['MA'] = df.Close.rolling(window=n).mean()
    df['MA_std'] = df.MA.rolling(window=n).std()
    return df


def compute_EMA(df, n=14):
    pass


def compute_MACD():
    pass


def compute_SAR():
    pass
