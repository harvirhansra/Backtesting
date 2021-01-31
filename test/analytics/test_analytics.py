import pytest
import random
import numpy as np
import pandas as pd

from backtesting.analytics.analytics import *


def test_compute_RSI():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_rsi = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 48.02, 48.87, 42.33, 40.96,
                             39.19, 45.78, 52.63, 64.04, 62.37, 54.85, 46.13,
                             37.43, 58.18, 53.59])

    df = compute_RSI(df)  # n=14
    assert np.allclose(df.RSI.values, expected_rsi, atol=0.0001, rtol=0.0001)


def test_compute_MA():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_ma = np.append([np.nan]*9, [168.3, 171.2, 175, 168, 161.4, 159.1,
                                         155.2, 157.9, 163.4, 163.8, 164, 158,
                                         157.9, 163.5, 167.7, 170, 165.9, 170.4,
                                         173])
    df = compute_MA(df, 10)
    assert np.allclose(df.MA.values, expected_ma, atol=0.0001, rtol=0.0001, equal_nan=True)


def test_compute_MA_multiple():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_ma10 = np.append([np.nan]*9, [168.3, 171.2, 175, 168, 161.4, 159.1,
                                           155.2, 157.9, 163.4, 163.8, 164, 158,
                                           157.9, 163.5, 167.7, 170, 165.9, 170.4,
                                           173])

    expected_ma20 = np.append([np.nan]*19, [166.15, 164.6 , 166.45, 165.75, 164.55,
                                            164.55, 160.55, 164.15, 168.2])
    df = compute_MA(df, 10, multiple=True)
    df = compute_MA(df, 20, multiple=True)
    assert np.allclose(df['MA10'].values, expected_ma10, atol=0.01, rtol=0.01, equal_nan=True)
    assert np.allclose(df['MA20'].values, expected_ma20, atol=0.01, rtol=0.01, equal_nan=True)


def test_compute_WMA():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_wma = np.append([np.nan]*9, [155.11, 163.24, 169.93, 164.47, 161.75,
                                          162.95, 163.29, 164.35, 163.82, 154.29,
                                          154.51, 152.51, 161.42, 169.25, 174.98,
                                          179.22, 170.13, 177.42, 179.35])
    df = compute_WMA(df, 10)
    assert np.allclose(df.WMA.values, expected_wma, atol=0.01, rtol=0.01, equal_nan=True)


def test_compute_EMA():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_ema = np.array([184.0, 176.3, 191.86, 200.8, 197.99, 198.51, 182.97,
                             164.09, 151.67, 154.05, 166.09, 174.47, 168.68, 165.65,
                             166.1, 165.13, 164.36, 162.61, 153.01, 155.23, 154.82,
                             164.42, 171.14, 175.51, 178.35, 167.68, 174.68, 175.83])
    df = compute_EMA(df, 10)
    assert np.allclose(df.EMA.values, expected_ema, atol=0.01, rtol=0.01)


def test_compute_MACD():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_macd = np.array([0.0, -0.31, 1.0, 1.71, 0.95, 0.86, -2.2, -5.84,
                              -7.92, -6.4, -2.54, 0.04, -1.6, -2.34, -1.98,
                              -2.11, -2.18, -2.59, -5.69, -4.5, -4.31, -0.49,
                              2.06, 3.61, 4.5, 0.15, 2.86, 3.14])
    expected_sl = np.array([0.0, -0.17, 0.3, 0.78, 0.83, 0.84, 0.07, -1.35, -2.87,
                            -3.66, -3.42, -2.67, -2.45, -2.42, -2.33, -2.29, -2.27,
                            -2.33, -3.01, -3.31, -3.51, -2.91, -1.91, -0.8, 0.27,
                            0.24, 0.77, 1.24])
    df = compute_MACD(df)
    assert np.allclose(df.MACD.values, expected_macd, atol=0.01, rtol=0.01, equal_nan=True)
    assert np.allclose(df.SL.values, expected_sl, atol=0.01, rtol=0.01, equal_nan=True)


@pytest.mark.skip(reason='NotImplemented')
def test_compute_SAR():
    raise NotImplementedError


def test_compute_sharpe_ratio_daily():
    df = pd.DataFrame({'Date': pd.date_range(start='2019-01-01 00:00:00', end='2019-12-31 00:00:00'),
                       'pnl_pct': [-1, 2, -3, 4, -5]*73})
    ratio = compute_sharpe_ratio(df.pnl_pct.values, 0.0014)
    assert ratio == -3.516


def test_compute_sharpe_ratio_hourly():
    df = pd.DataFrame({'Date': pd.date_range(start='2019-01-01 00:00:00', end='2019-12-31 23:00:00', freq='1H'),
                       'pnl_pct': [-0.1, 0.2, -0.3, 0.4, -0.5]*73*24})
    ratio = compute_sharpe_ratio(df.pnl_pct.values, 0.0014, hourly=True)
    assert ratio == -17.221
