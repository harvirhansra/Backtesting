import pytest

from market.marketdata import get_data_from_csv
from trade.deeplearning.strategery import HourlyDL


@pytest.fixture
def df():
    # df = get_data_from_csv('~/Code/Backtesting/main/trade/deeplearning/hourly/BTC_USD_TEST_Gemini_Hourly.csv')
    df = get_data_from_csv('~/Code/Backtesting/main/trade/deeplearning/hourly/BTC_USD_TEST_MARCH_Gemini_Hourly.csv')
    return df

def test_HourlyDL_1HR(df):
    hdl = HourlyDL(df, 'BTC', 10000, log=True, ui=True,
                   model_path='/home/harvir/Code/Backtesting/main/trade/deeplearning/hourly/BTC_USD_122448EMAs_VWAP_LOG_1HR/')
    # hdl.run()
    return True


def test_HourlyDL_4HR(df):
    hdl = HourlyDL(df, 'BTC', 10000, log=True, ui=True,
                   model_path='/home/harvir/Code/Backtesting/main/trade/deeplearning/hourly/BTC_USD_122448EMAs_VWAP_LOG_4HR/')
    # hdl.run()
    return True
