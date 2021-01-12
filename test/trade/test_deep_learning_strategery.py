import os
import pytest

from backtesting.market.marketdata import get_data_from_csv
from backtesting.trade.deeplearning.strategery import HourlyDL


@pytest.fixture
def df():
    df = None
    return df

def test_HourlyDL_1HR(df):
    hdl = HourlyDL(df, 'BTC', 10000, log=True, ui=True,
                   model_path=os.path.join(os.environ['ROOTDIR'], 'trade/deeplearning/hourly/BTC_USD_122448EMAs_VWAP_LOG_1HR/'))
    # hdl.run()
    return True


def test_HourlyDL_4HR(df):
    hdl = HourlyDL(df, 'BTC', 10000, log=True, ui=True,
                   model_path=os.path.join(os.environ['ROOTDIR'], 'trade/deeplearning/hourly/BTC_USD_122448EMAs_VWAP_LOG_4HR/'))
    # hdl.run()
    return True
