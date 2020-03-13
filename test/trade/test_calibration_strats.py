import pytest
import pandas as pd

from main.market.marketdata import get_data_from_csv
from main.trade.calibration_strats import above_under_ma_std_calib


@pytest.fixture
def df():
    # df = get_data_from_csv('../../resources/BTC_USD_2019-11-30_2019-12-31-CoinDesk.csv')

    df = pd.read_csv('../../resources/Bitfinex_BTCUSD_1h.csv')[::-1]
    df = df.tail(72)  # last 3 days
    df['Date'] = df['Date'].str.replace('-AM', ':00AM')
    df['Date'] = df['Date'].str.replace('-PM', ':00PM')

    df['Low'].astype(float)
    df['High'].astype(float)
    df.loc[:, 'Currency'] = 'BTC'
    df['Date'] = pd.to_datetime(df['Date'])

    return df


def test_above_under_ma_std_calib(df):
    return above_under_ma_std_calib(df, 14, False)
