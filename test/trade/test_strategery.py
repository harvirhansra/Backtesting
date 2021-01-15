import os
import pytest

from datetime import datetime

from backtesting.market.marketdata import get_data_from_csv, get_historical_from_coinbase
from backtesting.trade.strategery import (AboveUnderMAStd, RSI, MACD, MACDZero, RSIandMACD,
                                          RSIdelay, MA50MA10, MA20MA10)


@pytest.fixture
def df():
    interval = '1hr'
    ticker = 'ETH'
    start = datetime(2020, 1, 4, 00, 00)
    end = datetime(2021, 10, 1, 00, 00)
    df = get_historical_from_coinbase(f'{ticker}-GBP', start, end, interval)

    # df = get_data_from_csv(os.path.join(os.environ['ROOTDIR'], 'resources/COINBASE-BTCGBP-20180101-20210110-1hr.csv'))
    return df


def test_AboveUnderMAStd(df):
    AboveUnderMAStd(df, 'BTC', 10000, log=True, ui=False, std=2, lookback=20).run()
    return True


def test_RSI(df):
    RSI(df, 'BTC', 10000, log=True, ui=False).run()
    return True


def test_MACD(df):
    MACD(df, 'BTC', 10000, log=True, ui=False).run()
    return True


def test_MACDZero(df):
    MACDZero(df, 'BTC', 10000, log=True, ui=False).run()
    return True


def test_RSIandMACD(df):
    RSIandMACD(df, 'BTC', 10000, log=True, ui=False).run()
    return True


def test_RSIdelay(df):
    RSIdelay(df, 'BTC', 2000, log=True, ui=False).run()
    return True


def test_MA50MA10(df):
    MA50MA10(df, 'BTC', 2000, log=True, ui=False).run()
    return True


def test_MA20MA10(df):
    MA20MA10(df, 'BTC', 2000, log=True, ui=False).run()
    return True


if __name__ == '__main__':
    df = get_data_from_csv(os.path.join(os.environ['ROOTDIR'], 'resources/COINBASE-ETHGBP-20180101-20210101-1hr.csv'))
    MA50MA10(df, 'ETH', 400, log=True, ui=True)


# """
#     TODO:
#         - minimum holding period
#         - Longest holding period
#         - Optimise graph drawing with update
#         - Rolling price graph window
#         - Add multiple trades and logging to file
# """
