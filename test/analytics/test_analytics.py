import numpy as np
import pandas as pd

from backtesting.analytics.analytics import compute_RSI, compute_sharpe_ratio


def test_compute_RSI():
    df = pd.DataFrame({'Date': [x for x in range(0, 28)],
                       'Close': [184, 170, 215, 219, 191, 200, 134, 100, 107,
                                 163, 213, 208, 145, 153, 168, 161, 161, 155,
                                 111, 165, 153, 207, 201, 195, 191, 120, 206,
                                 181]})
    expected_rsi = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                             0.0, 0.0, 0.0, 0.0, 48.02, 48.87, 42.33, 40.96,
                             39.19, 45.78, 52.63, 64.04, 62.37,54.85, 46.13, 37.43,
                             58.18, 53.59])

    df = compute_RSI(df)
    assert np.allclose(df.RSI.values, expected_rsi, atol=0.0001, rtol=0.0001)


def test_compute_sharpe_ratio():
    raise NotImplementedError
