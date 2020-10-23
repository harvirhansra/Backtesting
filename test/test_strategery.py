import pytest

from market.marketdata import get_data_from_csv
from trade.strategery import AboveUnderMAStd, RSI, MACD, MACDZero, RSIandMACD, RSIdelay, MA50MA10


@pytest.fixture
def df():
    df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-27_Gemini_Hourly.csv')
    return df


def test_AboveUnderMAStd(df):
    AboveUnderMAStd(df, 'BTC', 10000, log=True, ui=True, std=2, lookback=20)
    return True


def test_RSI(df):
    RSI(df, 'BTC', 10000, log=True, ui=False).run()
    return True


def test_MACD(df):
    MACD(df, 'BTC', 10000, log=True, ui=True)
    return True


def test_MACDZero(df):
    MACDZero(df, 'BTC', 10000, log=True, ui=True)
    return True


def test_RSIandMACD(df):
    RSIandMACD(df, 'BTC', 10000, log=True, ui=True)
    return True


def test_RSIdelay(df):
    RSIdelay(df, 'BTC', 2000, log=True, ui=True)
    return True


def test_MA50MA10(df):
    MA50MA10(df, 'BTC', 2000, log=True, ui=False).run()
    return True


if __name__ == '__main__':
    df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-27_Gemini_Hourly.csv')
    RSI(df, 'BTC', 10000, log=True, ui=False).run()
    
# if __name__ == '__main__':
#     # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-23_Gemini_Daily.csv')
#     # df = get_data_from_csv('../resources/BTC_USD_2018-07-01_2020-05-23_Gemini_Daily.csv')
#     # df = get_data_from_csv('../resources/BTC_USD_2015-10-08_2020-05-27_Gemini_Hourly.csv')
#     # df = get_data_from_csv('../resources/BTC_USD_2018-05-27_2020-05-27_Gemini_Hourly.csv')
#     df = get_data_from_csv('../resources/BTC_USD_2020-01-01_2020-05-27_Gemini_Hourly.csv')
#     # df = get_data_from_csv('../resources/gemini_BTCUSD_1hr.csv')
#     # df = get_data_from_csv('../resources/gemini_BTCUSD_2019_1min.csv')
#     # s = RSI(df, 'BTC', 10000, log=True, ui=True)
#     s = MA50MA10(df, 'BTC', 2000, log=True, ui=True)
#     # s.run()

# """
#     TODO:
#         - minimum holding period
#         - Longest holding period
#         - Optimise graph drawing with update
#         - Rolling price graph window
#         - Add multiple trades and logging to file
# """
